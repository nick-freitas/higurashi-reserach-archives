#!/usr/bin/env python3
"""
Translation script: adds TextENGNew to all MSGSET/LOGSET entries.
Run this after populating the TRANSLATIONS dict below.
"""
import json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

FILES = [
    'outbreak_1.json', 'outbreak_2.json', 'outbreak_3.json', 'outbreak_4.json',
    'outbreak_5.json', 'outbreak_6.json', 'outbreak_end.json',
    'saikoroshi_1.json', 'saikoroshi_2.json', 'saikoroshi_3.json',
    'saikoroshi_4.json', 'saikoroshi_5.json', 'saikoroshi_end.json',
]

def strip_tags(text):
    """Strip game-engine tags from Japanese source."""
    # ruby annotation @bREADING.@<KANJI@> → keep kanji
    text = re.sub(r'@b[^.@]+\.\s*@<([^@>]+)@>', r'\1', text)
    # voice tags
    text = re.sub(r'@v[A-Za-z0-9/_.]+', '', text)
    # pause / wait
    text = re.sub(r'@k', '', text)
    text = re.sub(r'@w\d+\.', '', text)
    # line-break tag → real newline
    text = re.sub(r'@r', '\n', text)
    # misc tags
    text = re.sub(r'@[|ysa]\d*\.?', '', text)
    # backtick quotes used by some entries
    text = text.replace('``', '').replace("''", '')
    return text.strip()


def process_file(filename, translations):
    path = BASE / filename
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    updated = 0
    skipped = 0
    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' in entry:
            skipped += 1
            continue
        msg_id = entry.get('MessageID', entry.get('NamesJPN', ''))
        key = str(msg_id) if msg_id else None
        if key and key in translations:
            entry['TextENGNew'] = translations[key]
            updated += 1
        else:
            # leave untranslated entries without the key
            pass

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return updated, skipped


if __name__ == '__main__':
    print("Placeholder — run with actual translation dict populated.")
