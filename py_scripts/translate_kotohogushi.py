#!/usr/bin/env python3
"""
Translate kotohogushi chapters: add TextENGNew to each MSGSET/LOGSET entry.
Processes entries in batches to reduce API calls.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
import anthropic

# ── tag-stripping ─────────────────────────────────────────────────────────────

TAG_RE = re.compile(
    r'@vS\S+?\.'          # voice tags  @vS16/45/DS43071188.
    r'|@k'                # pause marker
    r'|@r'                # line-break marker
    r'|@-'                # misc
    r'|@\|'               # misc
    r'|@w\d+\.'           # wait  @w300.
    r'|@o\d+\.'           # misc overlay
    r'|`[^`]*`'           # backtick sequences
)

RUBY_RE = re.compile(r'@b[^.]+\.@<([^>]+)@>')  # @bよみ.@<表示@>  → keep 表示

def strip_tags(text: str) -> str:
    """Remove game-engine markup, resolve ruby annotations."""
    text = RUBY_RE.sub(r'\1', text)
    text = TAG_RE.sub('', text)
    return text.strip()

# ── prompt construction ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a literary translator specialising in Japanese visual novels.
Arc context: Kotohogushi-hen (Higurashi: When They Cry) — ancient-Japan setting.
Key characters: Hanyuu (羽入, horn-bearing woman / shrine deity), Riku (陸, her husband), Ouka (桜花, their daughter), Shino (志乃, family friend), Mao (魔央, Sonozaki governor's widow).
Lore terms to keep as-is: Ryuun, Ryuun-Ohc, Grifys, Putus, Jedha, Lynos, Turuy Galkia, Ryuuou/柳桜, Yeasomul, Onigafuchi.
Honorifics to preserve: -san, -kun, -chan, -sama, -sensei, -dono.

Translation rules:
- Produce natural, literary English — no machine-translation stiffness.
- Maintain first-person narration where the original uses it.
- Preserve \\n line breaks.
- Do NOT add any tags or markup.
- Translate ONLY the Japanese text provided; do not reference the existing English translation.
- For narration entries with no speaker, preserve the terse, atmospheric style.
- Combat lines should feel dynamic and visceral.
- Ouka often uses "nopah" (にぱ) as a cute expression — render as "Nipah".
- Ouka refers to herself as "Boku" (ボク) — use "I" in English but keep her speech slightly formal/archaic.
"""

def build_batch_prompt(entries):
    """Build a prompt asking to translate a numbered list of Japanese texts."""
    lines = []
    for i, (idx, jpn, speaker) in enumerate(entries, 1):
        spk = f"[{speaker}] " if speaker else ""
        lines.append(f"{i}. {spk}{jpn}")
    block = "\n".join(lines)
    return (
        "Translate each numbered Japanese line to English. "
        "Return ONLY numbered lines in the exact same order, nothing else.\n\n"
        + block
    )

# ── API client ────────────────────────────────────────────────────────────────

client = anthropic.Anthropic()

def translate_batch(entries, retries=3):
    """entries: list of (original_index, stripped_jpn, speaker_eng)
    Returns: list of translated strings in same order."""
    prompt = build_batch_prompt(entries)
    for attempt in range(retries):
        try:
            msg = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()
            # Parse numbered lines
            result_lines = {}
            for line in raw.split("\n"):
                m = re.match(r'^(\d+)\.\s*(.*)', line.strip())
                if m:
                    result_lines[int(m.group(1))] = m.group(2).strip()
            translations = []
            for i in range(1, len(entries) + 1):
                translations.append(result_lines.get(i, ""))
            return translations
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt+1} after error: {e}", flush=True)
                time.sleep(2 ** attempt)
            else:
                raise
    return [""] * len(entries)

# ── main processing ───────────────────────────────────────────────────────────

BATCH_SIZE = 30  # entries per API call

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    "kotohogushi_02.json",
    "kotohogushi_03.json",
    "kotohogushi_04.json",
    "kotohogushi_05.json",
    "kotohogushi_06.json",
    "kotohogushi_07.json",
    "kotohogushi_08.json",
    "kotohogushi_09.json",
    "kotohogushi_10.json",
    "kotohogushi_11.json",
    "kotohogushi_12.json",
    "kotohogushi_13.json",
    "kotohogushi_end.json",
]


def detect_indent(filepath):
    """Detect whether the file uses tabs or spaces for indentation."""
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if line.startswith("\t"):
                return "\t"
            if line.startswith("  "):
                return 2
    return 2


def process_file(filename):
    filepath = BASE_DIR / filename
    indent = detect_indent(filepath)

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    # Collect indices of entries that need translation
    pending = []  # list of (data_index, stripped_jpn, speaker_eng)
    for i, entry in enumerate(data):
        if entry.get("type") not in ("MSGSET", "LOGSET"):
            continue
        if "TextENGNew" in entry:
            continue
        jpn = entry.get("TextJPN", "")
        if not jpn:
            continue
        speaker = entry.get("NamesENG", "") or ""
        stripped = strip_tags(jpn)
        pending.append((i, stripped, speaker))

    if not pending:
        print(f"  Nothing to translate.")
        return 0

    print(f"  {len(pending)} entries to translate...", flush=True)
    translated_count = 0

    for batch_start in range(0, len(pending), BATCH_SIZE):
        batch = pending[batch_start: batch_start + BATCH_SIZE]
        # Translate
        translations = translate_batch(batch)
        # Write back
        for (data_idx, _, _), eng_new in zip(batch, translations):
            if eng_new:
                # Insert TextENGNew after TextENG
                entry = data[data_idx]
                new_entry = {}
                for k, v in entry.items():
                    new_entry[k] = v
                    if k == "TextENG":
                        new_entry["TextENGNew"] = eng_new
                if "TextENG" not in entry:
                    new_entry["TextENGNew"] = eng_new
                data[data_idx] = new_entry
                translated_count += 1

        progress = min(batch_start + BATCH_SIZE, len(pending))
        print(f"  {progress}/{len(pending)} entries done", flush=True)

        # Write after each batch to preserve progress
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
            f.write("\n")

    return translated_count


def main():
    total = 0
    for filename in FILES:
        print(f"\nProcessing {filename}...", flush=True)
        count = process_file(filename)
        print(f"  => {count} entries translated and written.", flush=True)
        total += count
    print(f"\nDone. Total entries translated: {total}")


if __name__ == "__main__":
    main()
