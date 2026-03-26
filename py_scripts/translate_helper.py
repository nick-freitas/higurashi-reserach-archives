#!/usr/bin/env python3
"""
Translation helper for Higurashi Miotsukushi Omote files.
Reads JSON, adds TextENGNew to each MSGSET/LOGSET entry.
"""

import json
import re
import sys

def strip_tags(text):
    """Remove game engine tags from Japanese text for reference."""
    # Remove voice tags: @vS.../digit+.
    text = re.sub(r'@vS[^.]+\.', '', text)
    # Remove @k (wait for input)
    text = re.sub(r'@k', '', text)
    # Remove @r (line break tag)
    text = re.sub(r'@r', '', text)
    # Remove @w digits (wait)
    text = re.sub(r'@w\d+\.', '', text)
    # Remove @b...@<...@> (ruby/furigana)
    text = re.sub(r'@b([^.]+)\.@<([^>]+)@>', r'\2', text)
    # Remove @|
    text = re.sub(r'@\|', '', text)
    # Remove `` backtick pairs used as quotes in ENG
    # (these appear in TextJPN as corner brackets 「」 anyway)
    return text.strip()

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def needs_translation(entry):
    return (
        entry.get('type') in ('MSGSET', 'LOGSET') and
        'TextJPN' in entry and
        'TextENGNew' not in entry
    )
