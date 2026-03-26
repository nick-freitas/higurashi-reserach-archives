#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.translation.textengnew_queue import (
    ValidationError,
    build_untranslated_file_manifest,
    claim_next_job,
    mark_job_complete,
    mark_job_failed,
    summarize_jobs,
    validate_file_against_manifest,
)


def pending_jobs_exist(manifest_path: Path) -> bool:
    summary = summarize_jobs(manifest_path)
    return summary["totals"].get("pending", 0) > 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default="artifacts/textengnew/file-jobs.json")
    parser.add_argument("--markdown", default="artifacts/textengnew/file-jobs.md")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--claude-cmd", default="codex")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--logs-dir", default="artifacts/textengnew/logs")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    markdown_path = Path(args.markdown)
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists():
        build_untranslated_file_manifest(repo_root, manifest_path, markdown_path)

    active: dict[str, tuple[str, subprocess.Popen[str], object]] = {}
    workers = [f"worker-{index:02d}" for index in range(1, args.workers + 1)]

    while True:
        for worker in workers:
            if worker in active:
                continue
            job = claim_next_job(manifest_path, worker)
            if job is None:
                continue
            filename = job["filename"]
            log_path = logs_dir / f"{worker}-{filename}.log"
            log_handle = log_path.open("w", encoding="utf-8")
            command = [
                sys.executable,
                str(Path(__file__).with_name("translate_single_file_claude.py")),
                "--repo-root",
                str(repo_root),
                "--file",
                filename,
                "--batch-size",
                str(args.batch_size),
                "--claude-cmd",
                args.claude_cmd,
            ]
            process = subprocess.Popen(
                command,
                cwd=repo_root,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
            )
            active[worker] = (filename, process, log_handle)
            print(f"started {worker} -> {filename}")

        finished: list[str] = []
        for worker, (filename, process, log_handle) in active.items():
            return_code = process.poll()
            if return_code is None:
                continue
            log_handle.close()
            if return_code == 0:
                try:
                    result = validate_file_against_manifest(repo_root, manifest_path, filename)
                    if result["missing_textengnew_entries"] != 0:
                        raise ValidationError(
                            f"{filename} still has {result['missing_textengnew_entries']} missing TextENGNew entries"
                        )
                    mark_job_complete(manifest_path, worker, filename)
                    print(f"completed {worker} -> {filename}")
                except Exception as exc:
                    mark_job_failed(manifest_path, worker, filename, str(exc))
                    print(f"failed {worker} -> {filename}: {exc}")
            else:
                mark_job_failed(manifest_path, worker, filename, f"translator exited with code {return_code}")
                print(f"failed {worker} -> {filename}: exit {return_code}")
            finished.append(worker)

        for worker in finished:
            active.pop(worker, None)

        if not active and not pending_jobs_exist(manifest_path):
            break

        time.sleep(args.poll_interval)

    summary = summarize_jobs(manifest_path)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
