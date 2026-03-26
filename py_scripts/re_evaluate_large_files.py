#!/usr/bin/env python3
"""
Re-evaluate changeScore 4/5 entries in 5 large Higurashi JSON files.

After manual investigation, the files fall into these categories:
- tsumihoroboshi_02.json: ALL score 4/5 entries are misaligned (ENGNew doesn't translate the JPN) -> KEEP
- tsumihoroboshi_03.json: ALL score 4/5 entries are misaligned -> KEEP
- tsumihoroboshi_04.json: idx 1-229 misaligned (KEEP), idx 230+ are retranslations (CLEAR)
- tatarigoroshi_10.json: ALL score 4/5 entries are retranslations (same meaning, different wording) -> CLEAR
- tips_140.json: ALL are empty TextENG with new TextENGNew content -> KEEP as score 5
"""
import json
import os
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def normalize(text):
    """Strip tags, punctuation, whitespace for comparison."""
    if not text:
        return ""
    t = re.sub(r'@[a-zA-Z][^\s@.]*\.?', '', text)
    t = t.replace('``', '').replace("''", '').replace('"', '').replace("'", '')
    t = ' '.join(t.lower().split())
    return t


def detect_indent(filepath):
    """Detect the indentation style of a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read(1000)
    if '\t' in raw.split('\n')[1] if len(raw.split('\n')) > 1 else '':
        return '\t'
    for line in raw.split('\n')[1:]:
        stripped = line.lstrip()
        if stripped and line != stripped:
            spaces = len(line) - len(stripped)
            return spaces
    return 2


def process_tatarigoroshi_10():
    """ALL score 4/5 entries are retranslations -> CLEAR all."""
    filepath = str(BASE / "tatarigoroshi_10.json")
    indent = detect_indent(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}

    for entry in data:
        score = entry.get('changeScore', 0)
        if score < 4:
            continue
        stats['total'] += 1

        # All entries are retranslations - clear them
        entry['significantChanges'] = False
        if 'changeReason' in entry:
            del entry['changeReason']
        if 'changeScore' in entry:
            del entry['changeScore']
        stats['cleared'] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

    return "tatarigoroshi_10.json", stats


def process_tsumihoroboshi_02():
    """ALL score 4/5 entries are misaligned -> KEEP all, but refresh reasons."""
    filepath = str(BASE / "tsumihoroboshi_02.json")
    indent = detect_indent(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}

    for entry in data:
        score = entry.get('changeScore', 0)
        if score < 4:
            continue
        stats['total'] += 1

        eng = entry.get('TextENG', '')
        eng_new = entry.get('TextENGNew', '')

        if not eng.strip() and eng_new.strip():
            # Empty old, content in new
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "Original translation was missing; new translation adds content."
            stats['kept'] += 1
        elif eng.strip() and not eng_new.strip():
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "New translation is empty; original had content."
            stats['kept'] += 1
        else:
            # Misaligned content
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "Content misalignment: TextENGNew does not translate the Japanese source text; it appears to contain text from a different part of the story."
            stats['kept'] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

    return "tsumihoroboshi_02.json", stats


def process_tsumihoroboshi_03():
    """ALL score 4/5 entries are misaligned -> KEEP all, refresh reasons."""
    filepath = str(BASE / "tsumihoroboshi_03.json")
    indent = detect_indent(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}

    for entry in data:
        score = entry.get('changeScore', 0)
        if score < 4:
            continue
        stats['total'] += 1

        eng = entry.get('TextENG', '')
        eng_new = entry.get('TextENGNew', '')

        if not eng.strip() and eng_new.strip():
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "Original translation was missing; new translation adds content."
            stats['kept'] += 1
        elif eng.strip() and not eng_new.strip():
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "New translation is empty; original had content."
            stats['kept'] += 1
        else:
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "Content misalignment: TextENGNew does not translate the Japanese source text; it appears to contain text from a different part of the story."
            stats['kept'] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

    return "tsumihoroboshi_03.json", stats


def process_tsumihoroboshi_04():
    """idx 1-229: misaligned (KEEP). idx 230+: retranslations (CLEAR)."""
    filepath = str(BASE / "tsumihoroboshi_04.json")
    indent = detect_indent(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}
    TRANSITION_IDX = 230

    for i, entry in enumerate(data):
        score = entry.get('changeScore', 0)
        if score < 4:
            continue
        stats['total'] += 1

        eng = entry.get('TextENG', '')
        eng_new = entry.get('TextENGNew', '')

        if i < TRANSITION_IDX:
            # Misaligned section
            if not eng.strip() and eng_new.strip():
                entry['significantChanges'] = True
                entry['changeScore'] = 5
                entry['changeReason'] = "Original translation was missing; new translation adds content."
                stats['kept'] += 1
            elif eng.strip() and not eng_new.strip():
                entry['significantChanges'] = True
                entry['changeScore'] = 5
                entry['changeReason'] = "New translation is empty; original had content."
                stats['kept'] += 1
            else:
                entry['significantChanges'] = True
                entry['changeScore'] = 5
                entry['changeReason'] = "Content misalignment: TextENGNew does not translate the Japanese source text; it appears to contain text from a different part of the story."
                stats['kept'] += 1
        else:
            # Retranslation section - clear
            entry['significantChanges'] = False
            if 'changeReason' in entry:
                del entry['changeReason']
            if 'changeScore' in entry:
                del entry['changeScore']
            stats['cleared'] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

    return "tsumihoroboshi_04.json", stats


def process_tips_140():
    """ALL entries have empty TextENG with content in TextENGNew -> KEEP as score 5."""
    filepath = str(BASE / "tips_140.json")
    indent = detect_indent(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}

    for entry in data:
        score = entry.get('changeScore', 0)
        if score < 4:
            continue
        stats['total'] += 1

        eng = entry.get('TextENG', '')
        eng_new = entry.get('TextENGNew', '')

        if not eng.strip() and eng_new.strip():
            # Genuinely missing translation -> keep at 5
            entry['significantChanges'] = True
            entry['changeScore'] = 5
            entry['changeReason'] = "Original translation was missing; new translation adds content."
            stats['kept'] += 1
        else:
            # Unexpected case - check manually
            # But clear if both have content (retranslation)
            ne = normalize(eng)
            nn = normalize(eng_new)
            if ne and nn:
                entry['significantChanges'] = False
                if 'changeReason' in entry:
                    del entry['changeReason']
                if 'changeScore' in entry:
                    del entry['changeScore']
                stats['cleared'] += 1
            else:
                stats['kept'] += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')

    return "tips_140.json", stats


def main():
    processors = [
        process_tsumihoroboshi_02,
        process_tsumihoroboshi_04,
        process_tatarigoroshi_10,
        process_tsumihoroboshi_03,
        process_tips_140,
    ]

    grand_total = {'total': 0, 'cleared': 0, 'kept': 0, 'downgraded': 0}

    for proc in processors:
        name, stats = proc()
        print(f"{name}: re-evaluated={stats['total']}, "
              f"kept={stats['kept']}, cleared={stats['cleared']}, "
              f"downgraded={stats['downgraded']}")
        for k in grand_total:
            grand_total[k] += stats[k]

    print(f"\n{'='*60}")
    print(f"GRAND TOTALS:")
    print(f"  Total re-evaluated: {grand_total['total']}")
    print(f"  Kept at 4/5: {grand_total['kept']}")
    print(f"  Downgraded: {grand_total['downgraded']}")
    print(f"  Cleared (significantChanges=false): {grand_total['cleared']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
