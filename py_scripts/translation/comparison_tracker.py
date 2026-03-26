"""Read-only tracker for translation comparison progress.

Scans Higurashi JSON files to identify entries needing TextENG vs TextENGNew
comparison. Reports status and outputs file batches for agent processing.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

TRANSLATABLE_TYPES = {"MSGSET", "LOGSET"}


@dataclass(frozen=True)
class FileScanResult:
    filename: str
    total_with_textengnew: int
    already_processed: int
    remaining_to_compare: int
    identical_pairs: int
    empty_texteng_pairs: int
    needs_llm_comparison: int


def scan_file(path: Path) -> FileScanResult | None:
    """Scan a single JSON file and return comparison stats.

    Returns None if file is not valid JSON array or has no translatable entries.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(data, list):
        return None

    total_with_textengnew = 0
    already_processed = 0
    identical_pairs = 0
    empty_texteng_pairs = 0

    for entry in data:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") not in TRANSLATABLE_TYPES:
            continue
        if "TextENGNew" not in entry:
            continue

        total_with_textengnew += 1

        if "significantChanges" in entry:
            already_processed += 1
        elif not entry.get("TextENG", ""):
            empty_texteng_pairs += 1
        elif entry.get("TextENG", "") == entry.get("TextENGNew", ""):
            identical_pairs += 1

    if total_with_textengnew == 0:
        return None

    remaining = total_with_textengnew - already_processed
    needs_llm = remaining - identical_pairs - empty_texteng_pairs

    return FileScanResult(
        filename=path.name,
        total_with_textengnew=total_with_textengnew,
        already_processed=already_processed,
        remaining_to_compare=remaining,
        identical_pairs=identical_pairs,
        empty_texteng_pairs=empty_texteng_pairs,
        needs_llm_comparison=needs_llm,
    )


def scan_repo(repo_root: Path) -> list[FileScanResult]:
    """Scan all JSON files in repo root and return results sorted by remaining entries ascending."""
    results: list[FileScanResult] = []
    for path in sorted(repo_root.glob("*.json")):
        result = scan_file(path)
        if result is not None:
            results.append(result)
    results.sort(key=lambda r: (r.remaining_to_compare, r.filename))
    return results


def format_status(results: list[FileScanResult]) -> str:
    """Format a human-readable status summary."""
    total_files = len(results)
    done_files = sum(1 for r in results if r.remaining_to_compare == 0)
    remaining_files = total_files - done_files

    total_entries = sum(r.total_with_textengnew for r in results)
    processed_entries = sum(r.already_processed for r in results)
    remaining_entries = sum(r.remaining_to_compare for r in results)
    identical_entries = sum(r.identical_pairs for r in results)
    empty_eng = sum(r.empty_texteng_pairs for r in results)
    needs_llm = sum(r.needs_llm_comparison for r in results)

    lines = [
        "=== Translation Comparison Status ===",
        f"Files:   {done_files}/{total_files} complete ({remaining_files} remaining)",
        f"Entries: {processed_entries}/{total_entries} processed ({remaining_entries} remaining)",
        f"  - Identical (auto-false):    {identical_entries}",
        f"  - Empty original (auto-true): {empty_eng}",
        f"  - Needs LLM comparison:       {needs_llm}",
    ]
    return "\n".join(lines)


def next_batch(results: list[FileScanResult], count: int) -> list[FileScanResult]:
    """Return the next count files that still need comparison work, smallest first."""
    return [r for r in results if r.remaining_to_compare > 0][:count]


def format_next_batch(batch: list[FileScanResult]) -> str:
    """Format batch as a table for display."""
    if not batch:
        return "No files remaining to process."
    lines = [f"{'File':<45} {'Remaining':>10} {'Identical':>10} {'Needs LLM':>10}"]
    lines.append("-" * 77)
    for r in batch:
        lines.append(
            f"{r.filename:<45} {r.remaining_to_compare:>10} {r.identical_pairs:>10} {r.needs_llm_comparison:>10}"
        )
    return "\n".join(lines)


def format_remaining(results: list[FileScanResult]) -> str:
    """Format all remaining files."""
    remaining = [r for r in results if r.remaining_to_compare > 0]
    return format_next_batch(remaining)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.translation.comparison_tracker <command> [args]")
        print("Commands: status, next <N>, remaining")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent.parent
    command = sys.argv[1]
    results = scan_repo(repo_root)

    if command == "status":
        print(format_status(results))
    elif command == "next":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        batch = next_batch(results, count)
        print(format_next_batch(batch))
    elif command == "remaining":
        print(format_remaining(results))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
