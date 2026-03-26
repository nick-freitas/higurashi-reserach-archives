from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import fcntl


TRANSLATABLE_TYPES = {"MSGSET", "LOGSET"}
DEFAULT_BATCH_SIZE = 25
DEFAULT_MODEL_PROMPT = """You are a literary translator for the Higurashi: When They Cry visual novel.

Translate Japanese visual novel text to natural literary English.

Rules:
- Translate TextJPN only. Ignore TextENG completely except as a rough sanity check for names and scene context.
- Add translations only for entries requested in the input.
- Keep names and honorifics unchanged.
- Preserve explicit \\n line breaks as literal newlines in the output strings.
- Strip or naturally absorb engine tags in the English output: @k, @r, @w###., @vS..., @b...@<...@>, @|.
- For spoken dialogue, do not add outer quotation marks unless the text itself clearly requires them in English.
- Keep the tone literary, accurate, and faithful to Higurashi's voice.
- Return ONLY JSON.

Input format:
[
  {"key": "mid:123", "speaker": "Rena", "text": "Japanese text"},
  ...
]

Return format:
[
  {"key": "mid:123", "translation": "English text"},
  ...
]"""


class ValidationError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileSnapshot:
    filename: str
    translatable_entries: int
    existing_textengnew_entries: int
    missing_textengnew_entries: int
    baseline_texteng_digest: str
    baseline_existing_textengnew_digest: str
    baseline_existing_textengnew_keys: list[str]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def entry_key(entry: dict[str, Any], index: int) -> str:
    message_id = entry.get("MessageID")
    if message_id is not None:
        return f"mid:{message_id}"
    return f"idx:{index}"


def translatable_entries(data: list[Any]) -> list[tuple[int, dict[str, Any]]]:
    result: list[tuple[int, dict[str, Any]]] = []
    for index, entry in enumerate(data):
        if isinstance(entry, dict) and entry.get("type") in TRANSLATABLE_TYPES:
            result.append((index, entry))
    return result


def digest_pairs(pairs: list[tuple[str, Any]]) -> str:
    payload = json.dumps(pairs, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def scan_file(path: Path) -> FileSnapshot | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(data, list):
        return None

    entries = translatable_entries(data)
    if not entries:
        return None

    texteng_pairs: list[tuple[str, Any]] = []
    existing_new_pairs: list[tuple[str, Any]] = []
    missing = 0
    for index, entry in entries:
        key = entry_key(entry, index)
        texteng_pairs.append((key, entry.get("TextENG")))
        if "TextENGNew" in entry:
            existing_new_pairs.append((key, entry.get("TextENGNew")))
        else:
            missing += 1

    return FileSnapshot(
        filename=path.name,
        translatable_entries=len(entries),
        existing_textengnew_entries=len(existing_new_pairs),
        missing_textengnew_entries=missing,
        baseline_texteng_digest=digest_pairs(texteng_pairs),
        baseline_existing_textengnew_digest=digest_pairs(existing_new_pairs),
        baseline_existing_textengnew_keys=[key for key, _ in existing_new_pairs],
    )


def build_untranslated_file_manifest(
    repo_root: Path,
    manifest_path: Path | None = None,
    markdown_path: Path | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    jobs: list[dict[str, Any]] = []

    for path in sorted(repo_root.glob("*.json")):
        snapshot = scan_file(path)
        if snapshot is None or snapshot.missing_textengnew_entries == 0:
            continue
        jobs.append(
            {
                "filename": snapshot.filename,
                "translatable_entries": snapshot.translatable_entries,
                "existing_textengnew_entries": snapshot.existing_textengnew_entries,
                "missing_textengnew_entries": snapshot.missing_textengnew_entries,
                "status": "pending",
                "claimed_by": None,
                "attempts": 0,
                "failure_reason": None,
                "completed_at": None,
                "baseline_texteng_digest": snapshot.baseline_texteng_digest,
                "baseline_existing_textengnew_digest": snapshot.baseline_existing_textengnew_digest,
                "baseline_existing_textengnew_keys": snapshot.baseline_existing_textengnew_keys,
            }
        )

    jobs.sort(key=lambda job: (-job["missing_textengnew_entries"], job["filename"]))

    manifest = {
        "generated_at": utc_now(),
        "repo_root": str(repo_root),
        "totals": {
            "job_count": len(jobs),
            "translatable_entries": sum(job["translatable_entries"] for job in jobs),
            "existing_textengnew_entries": sum(job["existing_textengnew_entries"] for job in jobs),
            "missing_textengnew_entries": sum(job["missing_textengnew_entries"] for job in jobs),
        },
        "jobs": jobs,
    }

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if markdown_path is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# TextENGNew File Jobs",
            "",
            f"- Generated: `{manifest['generated_at']}`",
            f"- Jobs: `{manifest['totals']['job_count']}`",
            f"- Missing entries: `{manifest['totals']['missing_textengnew_entries']}`",
            "",
        ]
        for job in jobs:
            lines.append(
                f"- `{job['filename']}`: missing `{job['missing_textengnew_entries']}`, "
                f"existing `{job['existing_textengnew_entries']}`, status `{job['status']}`"
            )
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return manifest


@contextmanager
def locked_manifest(manifest_path: Path):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    with manifest_path.open("r+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        data = json.load(handle)
        yield data
        handle.seek(0)
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.truncate()
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def claim_next_job(manifest_path: Path, worker: str) -> dict[str, Any] | None:
    with locked_manifest(manifest_path) as manifest:
        for job in manifest["jobs"]:
            if job["status"] == "pending":
                job["status"] = "in_progress"
                job["claimed_by"] = worker
                job["started_at"] = utc_now()
                return job.copy()
    return None


def _find_job(manifest: dict[str, Any], filename: str) -> dict[str, Any]:
    for job in manifest["jobs"]:
        if job["filename"] == filename:
            return job
    raise KeyError(f"Unknown file job: {filename}")


def mark_job_complete(manifest_path: Path, worker: str, filename: str) -> dict[str, Any]:
    with locked_manifest(manifest_path) as manifest:
        job = _find_job(manifest, filename)
        if job["claimed_by"] != worker:
            raise RuntimeError(f"{filename} is claimed by {job['claimed_by']}, not {worker}")
        job["status"] = "complete"
        job["completed_at"] = utc_now()
        job["claimed_by"] = None
        job["failure_reason"] = None
        return job.copy()


def mark_job_failed(manifest_path: Path, worker: str, filename: str, reason: str) -> dict[str, Any]:
    with locked_manifest(manifest_path) as manifest:
        job = _find_job(manifest, filename)
        if job["claimed_by"] != worker:
            raise RuntimeError(f"{filename} is claimed by {job['claimed_by']}, not {worker}")
        job["status"] = "failed"
        job["failure_reason"] = reason
        job["claimed_by"] = None
        return job.copy()


def requeue_failed_job(manifest_path: Path, filename: str) -> dict[str, Any]:
    with locked_manifest(manifest_path) as manifest:
        job = _find_job(manifest, filename)
        if job["status"] != "failed":
            raise RuntimeError(f"{filename} is not failed")
        job["status"] = "pending"
        job["claimed_by"] = None
        job["failure_reason"] = None
        job["attempts"] += 1
        return job.copy()


def apply_file_translations(file_path: Path, translations_by_key: dict[str, str]) -> int:
    file_path = Path(file_path)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    written = 0
    for index, entry in translatable_entries(data):
        key = entry_key(entry, index)
        if "TextENGNew" in entry:
            continue
        translation = translations_by_key.get(key)
        if translation is None:
            continue
        entry["TextENGNew"] = translation
        written += 1

    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return written


def validate_file_against_manifest(repo_root: Path, manifest_path: Path, filename: str) -> dict[str, Any]:
    repo_root = Path(repo_root)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    job = _find_job(manifest, filename)
    path = repo_root / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValidationError(f"{filename} does not contain a JSON list")

    entries = translatable_entries(data)
    texteng_pairs: list[tuple[str, Any]] = []
    existing_new_pairs: list[tuple[str, Any]] = []
    existing_new_keys = set(job["baseline_existing_textengnew_keys"])
    missing = 0
    added = 0
    for index, entry in entries:
        key = entry_key(entry, index)
        texteng_pairs.append((key, entry.get("TextENG")))
        if key in existing_new_keys:
            existing_new_pairs.append((key, entry.get("TextENGNew")))
        elif "TextENGNew" in entry:
            added += 1
        else:
            missing += 1

    if digest_pairs(texteng_pairs) != job["baseline_texteng_digest"]:
        raise ValidationError(f"TextENG changed in {filename}")
    if digest_pairs(existing_new_pairs) != job["baseline_existing_textengnew_digest"]:
        raise ValidationError(f"Pre-existing TextENGNew changed in {filename}")

    return {
        "filename": filename,
        "missing_textengnew_entries": missing,
        "added_textengnew_entries": added,
        "translatable_entries": len(entries),
    }


def summarize_jobs(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    jobs = manifest["jobs"]
    counts: dict[str, int] = {}
    workers: dict[str, str] = {}
    for job in jobs:
        counts[job["status"]] = counts.get(job["status"], 0) + 1
        if job["status"] == "in_progress" and job["claimed_by"]:
            workers[job["claimed_by"]] = job["filename"]
    remaining = sum(job["missing_textengnew_entries"] for job in jobs if job["status"] != "complete")
    return {
        "totals": counts,
        "remaining_missing_entries": remaining,
        "workers": workers,
    }


def parse_translation_response(output: str) -> list[dict[str, Any]]:
    text = output.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError("Translation response must be a JSON array")
    return parsed


def collect_missing_entries(file_path: Path) -> list[dict[str, Any]]:
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []
    for index, entry in translatable_entries(data):
        if "TextENGNew" in entry:
            continue
        entries.append(
            {
                "key": entry_key(entry, index),
                "speaker": entry.get("NamesENG") or entry.get("NamesJPN") or "",
                "text": entry.get("TextJPN", ""),
            }
        )
    return entries


def build_translation_prompt(entries: list[dict[str, Any]]) -> str:
    return f"{DEFAULT_MODEL_PROMPT}\n\n{json.dumps(entries, ensure_ascii=False)}"


def translate_entries_with_claude(
    entries: list[dict[str, Any]],
    claude_cmd: str = "codex",
    timeout: int = 600,
) -> dict[str, str]:
    prompt = build_translation_prompt(entries)
    if Path(claude_cmd).name == "codex":
        with tempfile.NamedTemporaryFile("r+", encoding="utf-8") as output_file:
            result = subprocess.run(
                [
                    claude_cmd,
                    "exec",
                    "--skip-git-repo-check",
                    "-C",
                    str(Path.cwd()),
                    "--output-last-message",
                    output_file.name,
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            output_file.seek(0)
            output = output_file.read()
    else:
        result = subprocess.run(
            [claude_cmd, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = result.stdout
    if result.returncode != 0:
        error_output = (result.stderr or result.stdout).strip()
        raise RuntimeError(error_output or f"{claude_cmd} exited with {result.returncode}")
    parsed = parse_translation_response(output)
    translations: dict[str, str] = {}
    for row in parsed:
        key = row.get("key")
        translation = row.get("translation")
        if not isinstance(key, str) or not isinstance(translation, str):
            raise ValueError("Each translation row must contain string key and translation")
        translations[key] = translation
    return translations


def translate_file_with_claude(
    file_path: Path,
    batch_size: int = DEFAULT_BATCH_SIZE,
    claude_cmd: str = "codex",
) -> dict[str, Any]:
    entries = collect_missing_entries(file_path)
    total = len(entries)
    written = 0
    for start in range(0, total, batch_size):
        batch = entries[start : start + batch_size]
        translations = translate_entries_with_claude(batch, claude_cmd=claude_cmd)
        written += apply_file_translations(file_path, translations)
    return {
        "filename": Path(file_path).name,
        "requested_entries": total,
        "written_entries": written,
    }


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, path)
