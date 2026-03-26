import json
from pathlib import Path

from scripts.translation.comparison_tracker import scan_file, scan_repo, format_status, format_remaining, next_batch, format_next_batch


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_scan_file_counts_comparable_entries(tmp_path: Path) -> None:
    """File with mix of: needs-comparison, already-processed, no-TextENGNew, identical."""
    write_json(
        tmp_path / "test.json",
        [
            {"type": "SAVEINFO", "category": 0, "JPN": "x", "ENG": "x"},
            # Needs comparison: has TextENGNew, no significantChanges, texts differ
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp1",
                "TextENG": "old one",
                "TextENGNew": "new one",
            },
            # Already processed: has significantChanges
            {
                "type": "MSGSET",
                "MessageID": 2,
                "TextJPN": "jp2",
                "TextENG": "old two",
                "TextENGNew": "new two",
                "significantChanges": False,
            },
            # No TextENGNew: skip
            {
                "type": "MSGSET",
                "MessageID": 3,
                "TextJPN": "jp3",
                "TextENG": "old three",
            },
            # Identical: has TextENGNew, no significantChanges, texts identical
            {
                "type": "MSGSET",
                "MessageID": 4,
                "TextJPN": "jp4",
                "TextENG": "same text",
                "TextENGNew": "same text",
            },
            # LOGSET without MessageID: needs comparison
            {
                "type": "LOGSET",
                "TextJPN": "jp5",
                "TextENG": "old five",
                "TextENGNew": "new five",
            },
        ],
    )
    result = scan_file(tmp_path / "test.json")
    assert result is not None
    assert result.filename == "test.json"
    assert result.total_with_textengnew == 4  # entries 1, 2, 4, 5
    assert result.already_processed == 1  # entry 2
    assert result.remaining_to_compare == 3  # entries 1, 4, 5
    assert result.identical_pairs == 1  # entry 4
    assert result.empty_texteng_pairs == 0
    assert result.needs_llm_comparison == 2  # entries 1, 5 (non-identical, unprocessed)


def test_scan_file_returns_none_for_non_json(tmp_path: Path) -> None:
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    assert scan_file(tmp_path / "bad.json") is None


def test_scan_file_returns_none_when_no_translatable(tmp_path: Path) -> None:
    write_json(
        tmp_path / "empty.json",
        [{"type": "SAVEINFO", "category": 0, "JPN": "x", "ENG": "x"}],
    )
    assert scan_file(tmp_path / "empty.json") is None


def test_scan_file_empty_texteng(tmp_path: Path) -> None:
    """Entry with empty TextENG but present TextENGNew counts as empty_texteng_pairs."""
    write_json(
        tmp_path / "empty_eng.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "",
                "TextENGNew": "new translation",
            },
            {
                "type": "MSGSET",
                "MessageID": 2,
                "TextJPN": "jp",
                "TextENG": "old",
                "TextENGNew": "new",
            },
        ],
    )
    result = scan_file(tmp_path / "empty_eng.json")
    assert result is not None
    assert result.empty_texteng_pairs == 1
    assert result.needs_llm_comparison == 1  # only the non-empty-eng entry


def test_scan_file_skips_select_entries(tmp_path: Path) -> None:
    """SELECT entries should not be counted even if they have TextENGNew."""
    write_json(
        tmp_path / "select.json",
        [
            {
                "type": "SELECT",
                "titleJPN": "jp",
                "titleENG": "eng",
                "choice1JPN": "jp",
                "choice1ENG": "eng",
            },
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "old",
                "TextENGNew": "new",
            },
        ],
    )
    result = scan_file(tmp_path / "select.json")
    assert result is not None
    assert result.total_with_textengnew == 1


def test_scan_file_all_processed(tmp_path: Path) -> None:
    """File where every entry with TextENGNew already has significantChanges."""
    write_json(
        tmp_path / "done.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "old",
                "TextENGNew": "new",
                "significantChanges": False,
            }
        ],
    )
    result = scan_file(tmp_path / "done.json")
    assert result is not None
    assert result.remaining_to_compare == 0
    assert result.needs_llm_comparison == 0


def test_scan_repo_finds_files_needing_work(tmp_path: Path) -> None:
    # File needing work
    write_json(
        tmp_path / "alpha.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "old",
                "TextENGNew": "new",
            }
        ],
    )
    # Fully processed file
    write_json(
        tmp_path / "beta.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 2,
                "TextJPN": "jp",
                "TextENG": "old",
                "TextENGNew": "new",
                "significantChanges": False,
            }
        ],
    )
    # File with no TextENGNew at all
    write_json(
        tmp_path / "gamma.json",
        [{"type": "MSGSET", "MessageID": 3, "TextJPN": "jp", "TextENG": "old"}],
    )

    results = scan_repo(tmp_path)
    remaining = [r for r in results if r.remaining_to_compare > 0]
    done = [r for r in results if r.remaining_to_compare == 0]
    assert len(remaining) == 1
    assert remaining[0].filename == "alpha.json"
    assert len(done) == 1
    assert done[0].filename == "beta.json"


def test_scan_repo_sorts_by_remaining_ascending(tmp_path: Path) -> None:
    # Small file: 1 entry
    write_json(
        tmp_path / "small.json",
        [{"type": "MSGSET", "MessageID": 1, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"}],
    )
    # Big file: 3 entries
    write_json(
        tmp_path / "big.json",
        [
            {"type": "MSGSET", "MessageID": 2, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"},
            {"type": "MSGSET", "MessageID": 3, "TextJPN": "jp", "TextENG": "c", "TextENGNew": "d"},
            {"type": "MSGSET", "MessageID": 4, "TextJPN": "jp", "TextENG": "e", "TextENGNew": "f"},
        ],
    )
    results = scan_repo(tmp_path)
    remaining = [r for r in results if r.remaining_to_compare > 0]
    assert remaining[0].filename == "small.json"
    assert remaining[1].filename == "big.json"


def test_format_status(tmp_path: Path) -> None:
    write_json(
        tmp_path / "test.json",
        [
            {"type": "MSGSET", "MessageID": 1, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"},
            {
                "type": "MSGSET",
                "MessageID": 2,
                "TextJPN": "jp",
                "TextENG": "c",
                "TextENGNew": "d",
                "significantChanges": True,
                "changeReason": "test",
            },
        ],
    )
    results = scan_repo(tmp_path)
    output = format_status(results)
    assert "0/1 complete" in output  # 0 done out of 1 file
    assert "1/2 processed" in output  # 1 processed out of 2 entries
    assert "1 remaining" in output


def test_format_remaining(tmp_path: Path) -> None:
    write_json(
        tmp_path / "done.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "a",
                "TextENGNew": "b",
                "significantChanges": False,
            }
        ],
    )
    write_json(
        tmp_path / "todo.json",
        [{"type": "MSGSET", "MessageID": 2, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"}],
    )
    results = scan_repo(tmp_path)
    output = format_remaining(results)
    assert "todo.json" in output
    assert "done.json" not in output


def test_next_batch_returns_n_files(tmp_path: Path) -> None:
    for i in range(5):
        write_json(
            tmp_path / f"file{i}.json",
            [{"type": "MSGSET", "MessageID": i, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"}],
        )
    results = scan_repo(tmp_path)
    batch = next_batch(results, count=3)
    assert len(batch) == 3
    # All should have remaining > 0
    assert all(r.remaining_to_compare > 0 for r in batch)


def test_next_batch_skips_completed(tmp_path: Path) -> None:
    write_json(
        tmp_path / "done.json",
        [
            {
                "type": "MSGSET",
                "MessageID": 1,
                "TextJPN": "jp",
                "TextENG": "a",
                "TextENGNew": "b",
                "significantChanges": False,
            }
        ],
    )
    write_json(
        tmp_path / "todo.json",
        [{"type": "MSGSET", "MessageID": 2, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"}],
    )
    results = scan_repo(tmp_path)
    batch = next_batch(results, count=5)
    assert len(batch) == 1
    assert batch[0].filename == "todo.json"


def test_format_next_batch_output(tmp_path: Path) -> None:
    write_json(
        tmp_path / "test.json",
        [
            {"type": "MSGSET", "MessageID": 1, "TextJPN": "jp", "TextENG": "a", "TextENGNew": "b"},
            {"type": "MSGSET", "MessageID": 2, "TextJPN": "jp", "TextENG": "c", "TextENGNew": "d"},
        ],
    )
    results = scan_repo(tmp_path)
    batch = next_batch(results, count=10)
    output = format_next_batch(batch)
    assert "test.json" in output
    assert "2" in output  # entry count appears
