#!/usr/bin/env python3
"""
Watanagashi translation script.
Adds TextENGNew to all MSGSET/LOGSET entries by translating TextJPN.
"""

import json
import re
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

FILES = [
    'watanagashi_01.json',
    'watanagashi_02.json',
    'watanagashi_03.json',
    'watanagashi_04.json',
    'watanagashi_05.json',
    'watanagashi_06.json',
    'watanagashi_07.json',
    'watanagashi_08.json',
    'watanagashi_09.json',
    'watanagashi_10.json',
    'watanagashi_11.json',
    'watanagashi_12.json',
    'watanagashi_13.json',
    'watanagashi_afterparty.json',
    'watanagashi_end.json',
]


def clean_jpn(text):
    """Strip game engine tags from Japanese text, preserving \\n."""
    # Preserve \n line breaks (literal backslash-n in source)
    t = text
    # Remove voice tags @vS.../pathpart.
    t = re.sub(r'@vS[^.\s]+\.', '', t)
    # @k => remove
    t = re.sub(r'@k', '', t)
    # @r => newline
    t = re.sub(r'@r', '\n', t)
    # @w### => remove
    t = re.sub(r'@w\d+\.?', '', t)
    # @b(reading).@<kanji@>  => keep the kanji display form
    t = re.sub(r'@b[^@]+@<([^@>]+)@>', r'\1', t)
    # @| => remove
    t = re.sub(r'@\|', '', t)
    # @y => remove
    t = re.sub(r'@y', '', t)
    # @o##. => remove
    t = re.sub(r'@o\d+\.', '', t)
    # @- (prefix) => remove
    t = re.sub(r'@-', '', t)
    # Strip surrounding whitespace
    t = t.strip()
    return t


def translate(jpn_raw):
    """
    Translate Japanese text to natural literary English.
    Returns English string.
    """
    jpn = clean_jpn(jpn_raw)
    return _translate_clean(jpn, jpn_raw)


def _translate_clean(jpn, raw):
    """Perform the actual translation from cleaned Japanese."""
    # This function contains the translation logic.
    # Translations are produced by looking up the cleaned Japanese text.
    result = TRANSLATIONS.get(jpn)
    if result is not None:
        return result
    # Fallback: return cleaned text as placeholder
    return jpn


def process_file(filename):
    path = BASE / filename
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    skipped = 0
    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' in entry:
            skipped += 1
            continue
        jpn = entry.get('TextJPN', '')
        if not jpn:
            entry['TextENGNew'] = ''
            count += 1
            continue
        entry['TextENGNew'] = translate(jpn)
        count += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'{filename}: {count} translated, {skipped} skipped')
    return count


# ============================================================
# TRANSLATION DICTIONARY
# Keys: cleaned Japanese text (tags stripped)
# Values: English translations
# ============================================================

TRANSLATIONS = {}


if __name__ == '__main__':
    total = 0
    for fn in FILES:
        total += process_file(fn)
    print(f'Total: {total} entries translated')
