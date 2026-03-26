#!/usr/bin/env python3
"""
Re-evaluate all entries with changeScore 4 or 5 across 108 Higurashi JSON files.
Phase 1: Extract all such entries for manual review.
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    "meakashi_02.json", "meakashi_03.json", "meakashi_06.json", "meakashi_07.json",
    "meakashi_08.json", "meakashi_09.json", "meakashi_15.json", "meakashi_20.json",
    "meakashi_21.json", "meakashi_22.json", "meakashi_23.json", "meakashi_24.json",
    "meakashi_badend.json", "minagoroshi_01.json", "minagoroshi_02.json",
    "minagoroshi_04.json", "minagoroshi_05.json", "minagoroshi_06.json",
    "minagoroshi_08.json", "minagoroshi_15.json", "minagoroshi_16.json",
    "minagoroshi_17.json", "minagoroshi_20.json", "miotsukushi_omote_04.json",
    "miotsukushi_omote_05.json", "miotsukushi_omote_15.json",
    "miotsukushi_omote_17.json", "miotsukushi_omote_19.json",
    "miotsukushi_omote_20.json", "miotsukushi_omote_22.json",
    "miotsukushi_omote_badend3.json", "miotsukushi_omote_end.json",
    "onikakushi_01.json", "onikakushi_02.json", "onikakushi_04.json",
    "onikakushi_05.json", "onikakushi_06.json", "onikakushi_07.json",
    "onikakushi_08.json", "onikakushi_09.json", "onikakushi_10.json",
    "onikakushi_11.json", "onikakushi_12.json", "onikakushi_end.json",
    "outbreak_1.json", "outbreak_2.json", "outbreak_3.json", "outbreak_4.json",
    "outbreak_5.json", "outbreak_6.json", "outbreak_end.json",
    "saikoroshi_1.json", "saikoroshi_5.json", "saikoroshi_end.json",
    "someutsushi_01.json", "someutsushi_03.json", "someutsushi_04.json",
    "someutsushi_05.json", "taraimawashi_1.json", "taraimawashi_2.json",
    "taraimawashi_3.json", "taraimawashi_4.json", "taraimawashi_7.json",
    "taraimawashi_8.json", "taraimawashi_afterparty.json", "taraimawashi_end.json",
    "tatarigoroshi_01.json", "tatarigoroshi_02.json", "tatarigoroshi_06.json",
    "tatarigoroshi_07.json", "tatarigoroshi_08.json", "tatarigoroshi_09.json",
    "tatarigoroshi_12.json", "tatarigoroshi_13.json", "tatarigoroshi_14.json",
    "tatarigoroshi_15.json", "tatarigoroshi_afterparty.json",
    "tatarigoroshi_end.json", "tips_001.json", "tips_003.json", "tips_004.json",
    "tips_005.json", "tips_006.json", "tips_007.json", "tips_008.json",
    "tips_009.json", "tips_010.json", "tips_012.json", "tips_015.json",
    "tips_016.json", "tips_017.json", "tips_018.json", "tips_020.json",
    "tips_021.json", "tips_023.json", "tips_024.json", "tips_025.json",
    "tips_027.json", "tips_029.json", "tips_030.json", "tips_031.json",
    "tips_032.json", "tips_034.json", "tips_035.json", "tips_041.json",
    "tips_045.json", "tips_048.json", "tips_050.json",
]

def extract_high_score_entries():
    """Extract all entries with changeScore 4 or 5 for review."""
    results = []
    for fname in FILES:
        fpath = str(BASE_DIR / fname)
        if not os.path.exists(fpath):
            print(f"WARNING: {fname} not found", file=sys.stderr)
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, entry in enumerate(data):
            score = entry.get("changeScore")
            if score in (4, 5):
                results.append({
                    "file": fname,
                    "index": i,
                    "messageId": entry.get("MessageID", "N/A"),
                    "changeScore": score,
                    "changeReason": entry.get("changeReason", ""),
                    "textENG": entry.get("TextENG", ""),
                    "textENGNew": entry.get("TextENGNew", ""),
                    "textJPN": entry.get("TextJPN", ""),
                    "namesENG": entry.get("NamesENG", ""),
                })
    return results

if __name__ == "__main__":
    entries = extract_high_score_entries()
    print(f"Total entries with changeScore 4 or 5: {len(entries)}")
    # Output as JSON for review
    with open(str(BASE_DIR / "scripts" / "high_score_entries.json"), 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Saved to scripts/high_score_entries.json")
