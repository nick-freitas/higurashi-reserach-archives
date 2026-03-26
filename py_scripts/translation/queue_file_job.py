#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import (
    claim_next_job,
    mark_job_complete,
    mark_job_failed,
    requeue_failed_job,
    summarize_jobs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="artifacts/textengnew/file-jobs.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--worker", required=True)

    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("--worker", required=True)
    complete_parser.add_argument("--file", required=True)

    fail_parser = subparsers.add_parser("fail")
    fail_parser.add_argument("--worker", required=True)
    fail_parser.add_argument("--file", required=True)
    fail_parser.add_argument("--reason", required=True)

    requeue_parser = subparsers.add_parser("requeue")
    requeue_parser.add_argument("--file", required=True)

    subparsers.add_parser("status")

    args = parser.parse_args()
    manifest_path = Path(args.manifest)

    if args.command == "claim":
        job = claim_next_job(manifest_path, args.worker)
        print(json.dumps(job, ensure_ascii=False, indent=2) if job else "null")
        return 0
    if args.command == "complete":
        print(json.dumps(mark_job_complete(manifest_path, args.worker, args.file), ensure_ascii=False, indent=2))
        return 0
    if args.command == "fail":
        print(json.dumps(mark_job_failed(manifest_path, args.worker, args.file, args.reason), ensure_ascii=False, indent=2))
        return 0
    if args.command == "requeue":
        print(json.dumps(requeue_failed_job(manifest_path, args.file), ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(summarize_jobs(manifest_path), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
