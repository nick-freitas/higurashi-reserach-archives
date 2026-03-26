#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import translate_file_with_claude


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--file", required=True)
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--claude-cmd", default="codex")
    args = parser.parse_args()

    file_path = Path(args.repo_root) / args.file
    result = translate_file_with_claude(file_path, batch_size=args.batch_size, claude_cmd=args.claude_cmd)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
