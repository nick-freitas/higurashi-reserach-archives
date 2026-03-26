#!/usr/bin/env python3
"""
Compare TextENG vs TextENGNew in Higurashi JSON files.
Determines if changes are significant (meaning-altering) or minor (stylistic).

Significant = a reader could form a different understanding of what's happening.
Not significant = same meaning, just different wording.
"""

import json
import re
import os
from difflib import SequenceMatcher
from pathlib import Path


def strip_tags(text):
    """Remove all game engine tags."""
    if not text:
        return ""
    t = re.sub(r'@v\S+\.', '', text)
    t = re.sub(r'@[kc|y]\d*\.?', '', t)
    t = re.sub(r'@b[^.]*\.', '', t)
    t = re.sub(r'@[<>]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def normalize_full(text):
    """Full normalization."""
    t = strip_tags(text)
    t = t.replace('``', '"').replace("''", '"')
    t = t.replace('—', '-').replace('–', '-').replace('--', '-')
    t = t.replace('…', '...')
    t = re.sub(r'\.{2,}', '...', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = t.lower()
    return t


def is_only_format_change(eng, eng_new):
    """Check if only formatting changed."""
    s1 = strip_tags(eng).replace('``', '"').replace("''", '"')
    s2 = strip_tags(eng_new).replace('``', '"').replace("''", '"')
    return s1 == s2


def get_content_words(text):
    """Extract meaningful content words."""
    t = normalize_full(text)
    t = re.sub(r'[^\w\s]', ' ', t)
    words = t.split()
    stop = {'the', 'a', 'an', 'is', 'was', 'were', 'are', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'shall', 'can', 'need', 'to', 'of',
            'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'during', 'before', 'after', 'between', 'out', 'off',
            'over', 'under', 'again', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'both', 'each', 'more',
            'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'or', 'if',
            'that', 'this', 'these', 'those', 'i', 'me', 'my', 'we', 'our',
            'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its',
            'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'about',
            'up', 'down', 's', 't', 've', 'll', 'd', 're', 'm',
            'like', 'also', 'still', 'even', 'back', 'get', 'got',
            'said', 'told', 'went', 'came', 'made', 'well', 'much',
            'really', 'quite', 'rather', 'now', 'right', 'way',
            'something', 'anything', 'everything', 'nothing',
            'seemed', 'looked', 'felt', 'thought', 'knew',
            'thing', 'things', 'already', 'sort', 'kind', 'enough',
            'though', 'although', 'while', 'because', 'since', 'until',
            'been', 'being', 'having', 'going', 'doing', 'saying',
            'one', 'ones', 'myself', 'yourself', 'himself', 'herself',
            'itself', 'ourselves', 'themselves', 'little', 'bit',
            'able', 'yet', 'upon', 'an', 'however', 'whether',
            'let', 'anyway', 'ever'}
    return [w for w in words if w not in stop and len(w) > 1]


def has_different_action_verbs(eng, eng_new):
    """Check if the main action verbs differ meaningfully."""
    clean_eng = normalize_full(eng)
    clean_new = normalize_full(eng_new)

    # Check for state-vs-action patterns
    # "has X" vs "pressed/pushed/held X"
    state_pattern_old = re.search(r'\bhas\b.*\b(horns?|head|hands?)\b', clean_eng)
    action_pattern_new = re.search(r'\b(pressed|pushed|held|grabbed|reached|touched)\b.*\b(horns?|head|hands?)\b', clean_new)
    if state_pattern_old and action_pattern_new:
        return True

    state_pattern_new = re.search(r'\bhas\b.*\b(horns?|head|hands?)\b', clean_new)
    action_pattern_old = re.search(r'\b(pressed|pushed|held|grabbed|reached|touched)\b.*\b(horns?|head|hands?)\b', clean_eng)
    if state_pattern_new and action_pattern_old:
        return True

    return False


def analyze_change(eng, eng_new, jpn=""):
    """
    Analyze if a translation change is significant.
    Returns (is_significant, reason_or_none)
    """
    if not eng or eng.strip() == '':
        summary = strip_tags(eng_new)[:100]
        return True, f"Original translation was missing entirely; new translation provides: {summary}"

    if eng == eng_new:
        return False, None

    if is_only_format_change(eng, eng_new):
        return False, None

    n_eng = normalize_full(eng)
    n_new = normalize_full(eng_new)

    if n_eng == n_new:
        return False, None

    # Strip all punctuation
    p_eng = re.sub(r'[^\w\s]', ' ', n_eng).strip()
    p_new = re.sub(r'[^\w\s]', ' ', n_new).strip()
    p_eng = re.sub(r'\s+', ' ', p_eng)
    p_new = re.sub(r'\s+', ' ', p_new)
    if p_eng == p_new:
        return False, None

    ratio = SequenceMatcher(None, n_eng, n_new).ratio()

    # Very high similarity
    if ratio > 0.85:
        return False, None

    # Word-level
    words_eng = get_content_words(eng)
    words_new = get_content_words(eng_new)
    set_eng = set(words_eng)
    set_new = set(words_new)

    if set_eng and set_new:
        overlap = set_eng & set_new
        union = set_eng | set_new
        jaccard = len(overlap) / len(union) if union else 1.0
    else:
        jaccard = 0.0 if (set_eng or set_new) else 1.0

    clean_eng = strip_tags(eng).lower()
    clean_new = strip_tags(eng_new).lower()

    # ---- Specific significant patterns ----

    # 1. Time/temporal changes
    time_words = ['morning', 'evening', 'night', 'day', 'afternoon', 'dawn', 'dusk', 'noon', 'midnight']
    tw_eng = set(w for w in time_words if re.search(r'\b' + w + r'\b', clean_eng))
    tw_new = set(w for w in time_words if re.search(r'\b' + w + r'\b', clean_new))
    if (tw_eng - tw_new) and (tw_new - tw_eng):
        return True, f"Time reference changes from '{'/'.join(tw_eng - tw_new)}' to '{'/'.join(tw_new - tw_eng)}', altering when events occur."

    # 2. State vs action description
    if has_different_action_verbs(eng, eng_new):
        return True, "Description changes from a state to an action (or vice versa), depicting a different scene."

    # 3. Specific cultural/meaning-changing term swaps
    specific_pairs = [
        (r'\bmonster\b', r'\byokai\b', "Cultural term changed from 'monster' to 'yokai', carrying different cultural connotations."),
        (r'\bqueen\b', r'\bfeudal lord\b', "Authority metaphor changed from 'queen' to 'feudal lord', shifting cultural framing."),
        (r'\bpurif(?:y|ied|ication)\b', r'\bdrive\s+(?:me\s+)?away\b', "Ritual action changed from 'purify' to 'drive away', which are conceptually different."),
        (r"\bteacher'?s?\s+lounge\b", r'\bstaff\s+room\b', False),  # same thing, not significant
    ]
    for pat_old, pat_new, reason in specific_pairs:
        if reason is False:
            continue  # skip non-significant known pairs
        if re.search(pat_old, clean_eng) and re.search(pat_new, clean_new):
            return True, reason
        if re.search(pat_new, clean_eng) and re.search(pat_old, clean_new):
            return True, reason

    # 4. Substantially different length => detail added/removed
    len_ce = len(strip_tags(eng))
    len_cn = len(strip_tags(eng_new))
    lr = max(len_ce, len_cn) / max(min(len_ce, len_cn), 1)

    if lr > 3.0 and min(len_ce, len_cn) > 10:
        if len_cn > len_ce:
            return True, "New translation adds substantial detail absent from the original, significantly expanding the information conveyed."
        else:
            return True, "New translation significantly condenses the original, omitting detail."

    if lr > 2.0 and ratio < 0.50 and min(len_ce, len_cn) > 20:
        if len_cn > len_ce:
            return True, "New translation expands on the original with additional detail that alters reader understanding."
        else:
            return True, "New translation condenses the original, omitting contextual details."

    # ---- General thresholds ----
    # Visual novel retranslations commonly rephrase substantially while
    # preserving meaning. Use generous thresholds to avoid false positives.
    avg_len = (len(n_eng) + len(n_new)) / 2

    if avg_len < 40:
        # Short text: very lenient (rephrasing short lines easily drops ratio)
        if ratio > 0.35:
            return False, None
        if jaccard > 0.20:
            return False, None
        if len(set_eng) <= 3 and len(set_new) <= 3:
            return False, None

    elif avg_len < 80:
        # Medium-short
        if ratio > 0.40:
            return False, None
        if jaccard > 0.25:
            return False, None

    elif avg_len < 150:
        # Medium
        if ratio > 0.45 and jaccard > 0.15:
            return False, None
        if ratio > 0.55:
            return False, None
        if jaccard > 0.35:
            return False, None

    else:
        # Long texts
        if ratio > 0.50 and jaccard > 0.15:
            return False, None
        if ratio > 0.55:
            return False, None
        if jaccard > 0.30:
            return False, None

    # If we get here, the change is likely significant
    only_old = set_eng - set_new
    only_new = set_new - set_eng

    if ratio < 0.35:
        return True, "Substantially different translation that conveys the scene differently."

    if lr > 1.8 and ratio < 0.55:
        return True, "Translation differs significantly in the amount of detail conveyed."

    if only_old and only_new and (len(only_old) > 2 or len(only_new) > 2):
        return True, "Translation uses different phrasing that shifts the reader's understanding of the scene."

    if ratio < 0.45:
        return True, "Rephrasing changes the emphasis or detail in a way that could affect reader interpretation."

    # Remaining cases with moderate ratio but passed all not-significant tests
    if only_old or only_new:
        return True, "Different word choices alter nuances of the translation."

    return False, None


def process_file(filepath):
    """Process a single JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read(2000)
    uses_tabs = '\t"type"' in raw or '\t\t"type"' in raw

    processed = 0
    significant = 0

    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' not in entry:
            continue

        # Clean previous analysis
        if 'significantChanges' in entry:
            del entry['significantChanges']
        if 'changeReason' in entry:
            del entry['changeReason']

        eng = entry.get('TextENG', '')
        eng_new = entry.get('TextENGNew', '')
        jpn = entry.get('TextJPN', '')

        processed += 1

        if eng == eng_new:
            entry['significantChanges'] = False
        elif not eng or eng.strip() == '':
            entry['significantChanges'] = True
            summary = strip_tags(eng_new)[:100]
            entry['changeReason'] = f"Original translation was missing entirely; new translation provides: {summary}"
            significant += 1
        else:
            is_sig, reason = analyze_change(eng, eng_new, jpn)
            entry['significantChanges'] = is_sig
            if is_sig and reason:
                entry['changeReason'] = reason
                significant += 1

    if uses_tabs:
        output = json.dumps(data, ensure_ascii=False, indent='\t')
    else:
        output = json.dumps(data, ensure_ascii=False, indent=2)

    if not output.endswith('\n'):
        output += '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    return processed, significant


def main():
    files = [
        'matsuribayashi_03.json',
        'minagoroshi_19.json',
        'yoigoshi_end.json',
        'himatsubushi_06.json',
        'tsukiotoshi_02.json',
        'tsumihoroboshi_20.json'
    ]

    base_dir = Path(__file__).resolve().parent.parent

    total_processed = 0
    total_significant = 0

    for f in files:
        path = str(base_dir / f)
        processed, significant = process_file(path)
        print(f'{f}: {processed} entries processed, {significant} significant')
        total_processed += processed
        total_significant += significant

    print(f'\nTotals: {total_processed} entries processed, {total_significant} significant')


if __name__ == '__main__':
    main()
