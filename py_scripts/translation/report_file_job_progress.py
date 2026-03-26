#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import summarize_jobs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="artifacts/textengnew/file-jobs.json")
    parser.add_argument("--markdown", default="artifacts/textengnew/progress.md")
    args = parser.parse_args()

    summary = summarize_jobs(Path(args.manifest))
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    lines = [
        "# TextENGNew Progress",
        "",
        f"- Pending: `{summary['totals'].get('pending', 0)}`",
        f"- In progress: `{summary['totals'].get('in_progress', 0)}`",
        f"- Complete: `{summary['totals'].get('complete', 0)}`",
        f"- Failed: `{summary['totals'].get('failed', 0)}`",
        f"- Remaining missing entries: `{summary['remaining_missing_entries']}`",
        "",
        "## Active workers",
        "",
    ]
    if summary["workers"]:
        for worker, filename in sorted(summary["workers"].items()):
            lines.append(f"- `{worker}`: `{filename}`")
    else:
        lines.append("- none")
    Path(args.markdown).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
