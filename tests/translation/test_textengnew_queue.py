import json
from pathlib import Path

import pytest

from scripts.translation.textengnew_queue import (
    ValidationError,
    apply_file_translations,
    build_untranslated_file_manifest,
    claim_next_job,
    mark_job_complete,
    mark_job_failed,
    parse_translation_response,
    requeue_failed_job,
    translate_file_with_claude,
    validate_file_against_manifest,
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sample_repo(tmp_path: Path) -> Path:
    write_json(
        tmp_path / "alpha.json",
        [
            {"type": "SAVEINFO", "category": 1, "JPN": "alpha", "ENG": "alpha"},
            {
                "type": "MSGSET",
                "MessageID": 101,
                "TextJPN": "未訳一",
                "TextENG": "old one",
            },
            {
                "type": "MSGSET",
                "MessageID": 102,
                "TextJPN": "既訳二",
                "TextENG": "old two",
                "TextENGNew": "new two",
            },
            {
                "type": "LOGSET",
                "TextJPN": "未訳三",
                "TextENG": "old three",
            },
        ],
    )
    write_json(
        tmp_path / "beta.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 201,
                "TextJPN": "完成済み",
                "TextENG": "done",
                "TextENGNew": "done new",
            }
        ],
    )
    write_json(
        tmp_path / "gamma.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 301,
                "TextJPN": "未訳四",
                "TextENG": "old four",
            }
        ],
    )
    return tmp_path


def test_build_manifest_only_includes_unfinished_files(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)

    manifest = build_untranslated_file_manifest(repo)

    assert manifest["totals"]["job_count"] == 2
    assert manifest["totals"]["missing_textengnew_entries"] == 3
    assert [job["filename"] for job in manifest["jobs"]] == ["alpha.json", "gamma.json"]

    alpha = manifest["jobs"][0]
    assert alpha["translatable_entries"] == 3
    assert alpha["existing_textengnew_entries"] == 1
    assert alpha["missing_textengnew_entries"] == 2
    assert alpha["status"] == "pending"
    assert alpha["claimed_by"] is None


def test_claim_complete_fail_and_requeue_job(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)
    manifest_path = tmp_path / "file-jobs.json"
    build_untranslated_file_manifest(repo, manifest_path)

    first = claim_next_job(manifest_path, "worker-01")
    second = claim_next_job(manifest_path, "worker-02")

    assert first["filename"] == "alpha.json"
    assert second["filename"] == "gamma.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert [job["status"] for job in manifest["jobs"]] == ["in_progress", "in_progress"]

    mark_job_complete(manifest_path, "worker-01", "alpha.json")
    mark_job_failed(manifest_path, "worker-02", "gamma.json", "test failure")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    completed = next(job for job in manifest["jobs"] if job["filename"] == "alpha.json")
    failed = next(job for job in manifest["jobs"] if job["filename"] == "gamma.json")
    assert completed["status"] == "complete"
    assert failed["status"] == "failed"
    assert failed["failure_reason"] == "test failure"

    requeue_failed_job(manifest_path, "gamma.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requeued = next(job for job in manifest["jobs"] if job["filename"] == "gamma.json")
    assert requeued["status"] == "pending"
    assert requeued["claimed_by"] is None
    assert requeued["attempts"] == 1


def test_validate_file_passes_when_only_missing_textengnew_is_added(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)
    manifest = build_untranslated_file_manifest(repo)
    manifest_path = tmp_path / "file-jobs.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    apply_file_translations(
        repo / "alpha.json",
        {
            "mid:101": "fresh one",
            "idx:3": "fresh three",
        },
    )

    result = validate_file_against_manifest(repo, manifest_path, "alpha.json")

    assert result["filename"] == "alpha.json"
    assert result["missing_textengnew_entries"] == 0
    assert result["added_textengnew_entries"] == 2


def test_validate_file_rejects_texteng_mutation(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)
    manifest = build_untranslated_file_manifest(repo)
    manifest_path = tmp_path / "file-jobs.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    data = json.loads((repo / "alpha.json").read_text(encoding="utf-8"))
    data[1]["TextENG"] = "mutated old one"
    write_json(repo / "alpha.json", data)

    with pytest.raises(ValidationError, match="TextENG changed"):
        validate_file_against_manifest(repo, manifest_path, "alpha.json")


def test_validate_file_rejects_existing_textengnew_mutation(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)
    manifest = build_untranslated_file_manifest(repo)
    manifest_path = tmp_path / "file-jobs.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    data = json.loads((repo / "alpha.json").read_text(encoding="utf-8"))
    data[2]["TextENGNew"] = "mutated new two"
    write_json(repo / "alpha.json", data)

    with pytest.raises(ValidationError, match="Pre-existing TextENGNew changed"):
        validate_file_against_manifest(repo, manifest_path, "alpha.json")


def test_apply_file_translations_only_fills_missing_entries(tmp_path: Path) -> None:
    repo = sample_repo(tmp_path)

    written = apply_file_translations(
        repo / "alpha.json",
        {
            "mid:101": "fresh one",
            "mid:102": "should not overwrite",
            "idx:3": "fresh three",
        },
    )

    assert written == 2
    data = json.loads((repo / "alpha.json").read_text(encoding="utf-8"))
    assert data[1]["TextENGNew"] == "fresh one"
    assert data[2]["TextENGNew"] == "new two"
    assert data[3]["TextENGNew"] == "fresh three"


def test_parse_translation_response_strips_markdown_fences() -> None:
    parsed = parse_translation_response(
        '```json\n[{"key":"mid:101","translation":"fresh one"}]\n```'
    )

    assert parsed == [{"key": "mid:101", "translation": "fresh one"}]


def test_translate_file_with_claude_only_requests_missing_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = sample_repo(tmp_path)
    seen_batches: list[list[str]] = []

    def fake_translate(entries, claude_cmd="claude", timeout=180):
        seen_batches.append([entry["key"] for entry in entries])
        return {entry["key"]: f"new:{entry['key']}" for entry in entries}

    monkeypatch.setattr(
        "scripts.translation.textengnew_queue.translate_entries_with_claude",
        fake_translate,
    )

    result = translate_file_with_claude(repo / "alpha.json", batch_size=1)

    assert result["requested_entries"] == 2
    assert result["written_entries"] == 2
    assert seen_batches == [["mid:101"], ["idx:3"]]

    data = json.loads((repo / "alpha.json").read_text(encoding="utf-8"))
    assert data[1]["TextENGNew"] == "new:mid:101"
    assert data[2]["TextENGNew"] == "new two"
    assert data[3]["TextENGNew"] == "new:idx:3"
