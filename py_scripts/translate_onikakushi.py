#!/usr/bin/env python3
"""
Translate Higurashi onikakushi JSON files from Japanese to English.
Adds TextENGNew key to each MSGSET/LOGSET entry.
"""

import json
import re
import sys
import time
from pathlib import Path
import anthropic

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    "onikakushi_01.json",
    "onikakushi_02.json",
    "onikakushi_03.json",
    "onikakushi_04.json",
    "onikakushi_05.json",
    "onikakushi_06.json",
    "onikakushi_07.json",
    "onikakushi_08.json",
    "onikakushi_09.json",
    "onikakushi_10.json",
    "onikakushi_11.json",
    "onikakushi_12.json",
    "onikakushi_afterparty.json",
    "onikakushi_end.json",
]

SYSTEM_PROMPT = """You are a literary Japanese-to-English translator working on the Higurashi: When They Cry visual novel (Onikakushi-hen / Spirited Away chapter).

Rules:
- Translate TextJPN to natural, literary English. Ignore TextENG entirely.
- The protagonist is Keiichi Maebara, a teenage boy who recently moved to the rural village of Hinamizawa. He narrates in first person.
- Keep honorifics (-san, -kun, -chan, -nii, etc.) as-is.
- Keep character names as-is (Keiichi, Rena, Mion, Shion, Satoko, Rika, Tomitake, Irie, Oishi, etc.).
- Preserve \\n exactly.
- Strip all game engine tags: @k, @r, @|, @w###., @vS..., @b...@<...@>, `` (backtick pairs used as quote marks in ENG should become regular dialogue quotes in your output — but if the Japanese uses 「」, render as natural English dialogue with no special punctuation wrapping).
- For narration (no NamesJPN/NamesENG): translate as first-person narration.
- For dialogue (has NamesJPN/NamesENG): translate as natural spoken dialogue. Do NOT add quote marks — the engine handles display.
- Maintain the emotional register: dread, suspense, warm friendship, paranoia, rural atmosphere.
- Be literary but not purple — clear, precise, evocative prose.

Output format: Return ONLY a JSON array of objects, one per input entry, in the same order. Each object: {"MessageID": <id>, "TextENGNew": "<translation>"}. No other text."""

def strip_tags(text):
    """Strip game engine tags from Japanese text before translation context."""
    # Remove voice tags @vS.../...
    text = re.sub(r'@vS[^.]+\.', '', text)
    # Remove wait tags @w\d+.
    text = re.sub(r'@w\d+\.', '', text)
    # Remove @k, @r, @|
    text = re.sub(r'@[kr|]', '', text)
    # Remove @b...@<...@> color tags
    text = re.sub(r'@b[^@]*@<[^@]*@>', lambda m: re.sub(r'@b|@<|@>', '', m.group()), text)
    # Remove backtick pairs ``
    text = re.sub(r'``', '', text)
    return text.strip()

def make_batch_prompt(entries):
    """Build a prompt for a batch of entries."""
    items = []
    for e in entries:
        items.append({
            "MessageID": e["MessageID"],
            "NamesJPN": e.get("NamesJPN", ""),
            "TextJPN": e["TextJPN"],
        })
    return json.dumps(items, ensure_ascii=False, indent=2)

def translate_batch(client, entries, retries=3):
    """Translate a batch of entries, return list of {MessageID, TextENGNew}."""
    prompt = make_batch_prompt(entries)

    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"Translate these entries:\n\n{prompt}"}
                ]
            )
            raw = response.content[0].text.strip()
            # Extract JSON array if wrapped in markdown
            if raw.startswith("```"):
                raw = re.sub(r'^```[a-z]*\n?', '', raw)
                raw = re.sub(r'\n?```$', '', raw)
            results = json.loads(raw)
            return results
        except json.JSONDecodeError as e:
            print(f"  JSON parse error on attempt {attempt+1}: {e}", file=sys.stderr)
            if attempt == retries - 1:
                raise
            time.sleep(2)
        except Exception as e:
            print(f"  API error on attempt {attempt+1}: {e}", file=sys.stderr)
            if attempt == retries - 1:
                raise
            time.sleep(5)

def process_file(client, filename):
    """Process a single JSON file, adding TextENGNew to each MSGSET/LOGSET."""
    filepath = BASE_DIR / filename

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect entries needing translation
    to_translate = []
    for entry in data:
        if entry.get("type") in ("MSGSET", "LOGSET") and "TextENGNew" not in entry:
            to_translate.append(entry)

    if not to_translate:
        print(f"  {filename}: all entries already translated, skipping")
        return 0

    print(f"  {filename}: translating {len(to_translate)} entries...")

    # Translate in batches of 30
    BATCH_SIZE = 30
    translations_map = {}

    for i in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(to_translate) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"    Batch {batch_num}/{total_batches} ({len(batch)} entries)...", end=' ', flush=True)

        results = translate_batch(client, batch)
        for r in results:
            translations_map[r["MessageID"]] = r["TextENGNew"]

        print("done")
        # Small delay to be polite to the API
        if i + BATCH_SIZE < len(to_translate):
            time.sleep(0.5)

    # Apply translations back to data
    applied = 0
    for entry in data:
        if entry.get("type") in ("MSGSET", "LOGSET") and "TextENGNew" not in entry:
            mid = entry["MessageID"]
            if mid in translations_map:
                entry["TextENGNew"] = translations_map[mid]
                applied += 1
            else:
                print(f"  WARNING: MessageID {mid} not in translation results", file=sys.stderr)

    # Write back with 2-space indent
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f"  {filename}: wrote {applied} translations")
    return applied

def main():
    client = anthropic.Anthropic()

    total = 0
    for filename in FILES:
        print(f"\nProcessing {filename}...")
        try:
            count = process_file(client, filename)
            total += count
        except Exception as e:
            print(f"ERROR processing {filename}: {e}", file=sys.stderr)
            raise

    print(f"\nDone. Total entries translated: {total}")

if __name__ == "__main__":
    main()
