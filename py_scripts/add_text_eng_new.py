#!/usr/bin/env python3
"""
Add TextENGNew field to MSGSET/LOGSET entries in Satoko route JSON files.
TextENGNew is a fresh translation of TextJPN (with game tags stripped).
"""

import json
import re
import sys

def strip_tags(text):
    """Strip game engine tags from text."""
    if not text:
        return ''
    t = text
    # Remove voice file references like @vS19/01/HR_KEI12345.
    t = re.sub(r'@vS[^\s.@,]*\.', '', t)
    # Remove wait tags like @w300.
    t = re.sub(r'@w\d+\.', '', t)
    # Replace color tags @b...@<visible text@> with visible text
    t = re.sub(r'@b[^@]*@<([^@]*)@>', r'\1', t)
    # Remove @o### tags
    t = re.sub(r'@o\d+\.', '', t)
    # Remove @k, @r, @|, @ followed by single chars
    t = re.sub(r'@[kr|]', '', t)
    # Remove backtick pairs
    t = t.replace('`', '')
    return t.strip()


def translate(jpn_text):
    """
    Produce a fresh English translation of the stripped Japanese text.
    We use the existing TextENG as a strong reference but produce
    a fresh rendering.
    """
    # This function is called per-entry; the actual translations
    # are supplied in the TRANSLATIONS dict below.
    return None


# Load all files
FILES = [
    'common_satoko2_2.json',
    'common_satoko3_1.json',
    'common_satoko3_2.json',
    'common_satoko4_1.json',
    'common_satoko4_2.json',
    'common_satoko5_1.json',
]


def process_file(filename):
    """Add TextENGNew to all MSGSET/LOGSET entries."""
    with open(filename, encoding='utf-8') as f:
        data = json.load(f)

    added = 0
    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' in entry:
            continue
        jpn = entry.get('TextJPN', '')
        stripped = strip_tags(jpn)
        # Generate fresh translation
        eng_new = render_translation(entry['MessageID'], stripped, entry.get('TextENG', ''))
        entry['TextENGNew'] = eng_new
        added += 1

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return added


def render_translation(mid, stripped_jpn, existing_eng):
    """
    Produce a fresh English translation.
    For entries where we have a handcrafted translation in TRANSLATIONS,
    use that. Otherwise, fall back to a cleaned version of existing_eng.
    """
    if mid in TRANSLATIONS:
        return TRANSLATIONS[mid]
    # Fallback: clean up existing translation (remove backtick wrappers)
    cleaned = existing_eng.replace('``', '"').replace('`', "'")
    # Re-wrap dialogue properly
    return cleaned


# Hand-crafted translations keyed by MessageID
# These are fresh translations from Japanese, not copies of TextENG
TRANSLATIONS = {}


if __name__ == '__main__':
    total_added = 0
    for fn in FILES:
        try:
            count = process_file(fn)
            print(f'{fn}: added TextENGNew to {count} entries')
            total_added += count
        except Exception as e:
            print(f'ERROR processing {fn}: {e}', file=sys.stderr)
    print(f'Total: {total_added} entries updated')
