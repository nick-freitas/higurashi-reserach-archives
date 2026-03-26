#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import ValidationError, validate_file_against_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default="artifacts/textengnew/file-jobs.json")
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    try:
        result = validate_file_against_manifest(Path(args.repo_root), Path(args.manifest), args.file)
    except ValidationError as exc:
        print(str(exc))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
