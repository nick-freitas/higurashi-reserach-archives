#!/usr/bin/env python3
"""
Higurashi translation script.
Adds TextENGNew to all MSGSET/LOGSET entries that lack it.
Run with: python3 translate_batch.py <file.json>
"""

import json
import sys
import re

def strip_tags(text):
    """Strip game engine tags from Japanese text for translation."""
    # Remove @vS voice tags
    text = re.sub(r'@vS[^\s.]*\.', '', text)
    # Remove @w### timing tags
    text = re.sub(r'@w\d+\.', '', text)
    # Remove simple tags
    text = re.sub(r'@[krb\-\|]', '', text)
    # Remove @<...@> constructs
    text = re.sub(r'@<[^>]*@>', '', text)
    # Remove `` markers
    text = text.replace('``', '')
    return text.strip()

def needs_translation(entry):
    t = entry.get('type', '')
    if t not in ('MSGSET', 'LOGSET'):
        return False
    if 'TextENGNew' in entry:
        return False
    if not entry.get('TextJPN'):
        return False
    return True

def process_file(filepath, translations):
    """Insert translations into file and write back."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for entry in data:
        if not needs_translation(entry):
            continue
        mid = entry.get('MessageID', entry.get('type', '?'))
        if mid in translations:
            entry['TextENGNew'] = translations[mid]
            count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return count

if __name__ == '__main__':
    print("Use this as a module, not directly.")
