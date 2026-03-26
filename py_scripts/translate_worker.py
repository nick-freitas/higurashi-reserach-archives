#!/usr/bin/env python3
"""
Translation worker for Higurashi ENX texts.
Translates TextJPN -> TextENGNew for MSGSET/LOGSET entries.
"""
import json
import sys
import re

def clean_for_display(text):
    """Strip game tags for display only."""
    t = re.sub(r'@v[A-Za-z0-9/_]+\.', '', text)
    t = re.sub(r'@w\d+\.', '', t)
    t = re.sub(r'@b[^.]+\.@<([^@]+)@>', r'\1', t)
    t = re.sub(r'@[krb|]', '', t)
    t = t.strip()
    return t

def process_file(filepath, translations_dict):
    """Load file, add TextENGNew for entries in translations_dict, write back."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' in entry:
            continue
        mid = entry.get('MessageID')
        if mid in translations_dict:
            entry['TextENGNew'] = translations_dict[mid]
            count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: translate_worker.py <filepath>")
        sys.exit(1)
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    missing = [(e.get('MessageID'), e['TextJPN']) for e in data
               if e.get('type') in ('MSGSET','LOGSET') and 'TextENGNew' not in e]
    for mid, txt in missing:
        print(f"{mid}\t{txt}")
