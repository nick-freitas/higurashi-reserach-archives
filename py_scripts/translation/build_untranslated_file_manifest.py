#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import build_untranslated_file_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default="artifacts/textengnew/file-jobs.json")
    parser.add_argument("--markdown", default="artifacts/textengnew/file-jobs.md")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    markdown_path = Path(args.markdown)
    manifest = build_untranslated_file_manifest(repo_root, manifest_path, markdown_path)
    print(
        f"generated {manifest['totals']['job_count']} jobs with "
        f"{manifest['totals']['missing_textengnew_entries']} missing entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
