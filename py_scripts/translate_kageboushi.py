#!/usr/bin/env python3
"""
Translate kageboushi JSON files from Japanese to English.
Adds TextENGNew to each MSGSET/LOGSET entry that lacks it.
Uses claude CLI for translation in batches, with parallel file processing.
"""

import json
import os
import sys
import subprocess
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    "kageboushi_01.json",
    "kageboushi_02.json",
    "kageboushi_03.json",
    "kageboushi_04.json",
    "kageboushi_05.json",
    "kageboushi_06.json",
    "kageboushi_07.json",
    "kageboushi_08.json",
    "kageboushi_09.json",
    "kageboushi_10.json",
    "kageboushi_11.json",
    "kageboushi_12.json",
    "kageboushi_end.json",
]

SYSTEM_PROMPT = """You are a literary translator for the Higurashi: When They Cry visual novel. Translate Japanese visual novel text to natural literary English.

Rules:
- Translate TextJPN only
- Natural, literary English prose
- Keep Japanese honorifics (san, kun, chan, sama, etc.)
- Keep character names unchanged
- First-person narration where original uses it
- Preserve literal \\n sequences as-is in output
- Strip game tags from output: @k, @r, @vS..., @w###., @b...@<...@>, @|, @-
- Japanese 「」dialogue → "double quotes" in English
- Japanese 『』radio/broadcast dialogue → "double quotes" in English
- Japanese （） inner thoughts → (parentheses) in English
- … → ...
- Narrator is Akasaka, a Tokyo Metropolitan Police detective
- Key characters: Akasaka (narrator), Ooishi (Okinomiya detective), Tomoe/Minai (local detective), Rika (young girl)

You will receive a JSON array: [{"id": N, "text": "Japanese text"}, ...]
Return ONLY a JSON array: [{"id": N, "translation": "English text"}, ...]
No markdown fences, no explanation, no other text."""

# Lock for file writes (each file has its own data, but we print to stdout)
print_lock = threading.Lock()


def log(msg):
    with print_lock:
        print(msg, flush=True)


def translate_batch_claude(entries):
    """Translate a batch using claude CLI. entries = list of (index, text_jpn)."""
    batch_input = json.dumps(
        [{"id": idx, "text": text} for idx, text in entries],
        ensure_ascii=False
    )

    prompt = f"{SYSTEM_PROMPT}\n\n{batch_input}"

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr[:300]}")

    output = result.stdout.strip()

    # Strip markdown code fences if present
    if output.startswith("```"):
        lines = output.split("\n")
        end_idx = len(lines) - 1
        while end_idx > 0 and not lines[end_idx].strip().startswith("```"):
            end_idx -= 1
        output = "\n".join(lines[1:end_idx])

    parsed = json.loads(output)
    return {r["id"]: r["translation"] for r in parsed}


def process_file(filename, batch_size=25):
    filepath = BASE_DIR / filename

    if not os.path.exists(filepath):
        log(f"  SKIPPING {filename} (not found)")
        return filename, 0

    # Use a per-file lock for reading/writing
    file_lock = threading.Lock()

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find entries needing translation
    to_translate = []
    for i, entry in enumerate(data):
        if entry.get("type") in ("MSGSET", "LOGSET") and "TextENGNew" not in entry:
            to_translate.append((i, entry.get("TextJPN", "")))

    if not to_translate:
        log(f"  {filename}: already complete (0 to translate)")
        return filename, 0

    log(f"  {filename}: {len(to_translate)} entries to translate")

    translated_count = 0
    total_batches = (len(to_translate) + batch_size - 1) // batch_size

    for batch_start in range(0, len(to_translate), batch_size):
        batch = to_translate[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1

        retries = 0
        translations = {}
        while retries < 3:
            try:
                translations = translate_batch_claude(batch)
                break
            except json.JSONDecodeError as e:
                retries += 1
                log(f"    {filename} batch {batch_num}: JSON err retry {retries}")
                time.sleep(2)
            except subprocess.TimeoutExpired:
                retries += 1
                log(f"    {filename} batch {batch_num}: timeout retry {retries}")
                time.sleep(5)
            except Exception as e:
                retries += 1
                log(f"    {filename} batch {batch_num}: err retry {retries}: {str(e)[:60]}")
                time.sleep(3)
        else:
            log(f"    {filename} batch {batch_num}: FAILED after 3 retries, skipping")
            continue

        # Apply translations to data
        for idx, _ in batch:
            if idx in translations:
                data[idx]["TextENGNew"] = translations[idx]
                translated_count += 1

        log(f"    {filename}: batch {batch_num}/{total_batches} done ({translated_count}/{len(to_translate)})")

        # Save after each batch
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    log(f"  {filename}: COMPLETE — {translated_count} translations written")
    return filename, translated_count


def main():
    # Process files in parallel — use 4 workers to stay within rate limits
    max_workers = 4

    total = 0
    log(f"Starting translation with {max_workers} parallel workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, fn, 25): fn for fn in FILES}
        for future in as_completed(futures):
            filename = futures[future]
            try:
                fname, count = future.result()
                total += count
            except Exception as e:
                log(f"  ERROR processing {filename}: {e}")

    log(f"\nDone. Total new translations written: {total}")


if __name__ == "__main__":
    main()
