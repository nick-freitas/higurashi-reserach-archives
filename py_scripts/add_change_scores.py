#!/usr/bin/env python3
"""Add changeScore to entries with significantChanges: true in specified Higurashi JSON files."""

import json
import sys
from pathlib import Path

# Mapping: (filename, MessageID) -> changeScore
# Score guide:
# 1 = Trivial (minor wording preference, slight nuance)
# 2 = Minor (small omission, minor terminology change)
# 3 = Moderate (meaningful nuance change, subject/tense shifts, notable omissions)
# 4 = Major (wrong subject, reversed meaning, fabricated content)
# 5 = Critical (missing/misaligned content, opposite meaning on plot-critical info)

SCORES = {
    # tips_069.json
    ("tips_069.json", 14495): 2,  # Scale of compliment changed (hundred more years vs a hundred or two hundred age)
    ("tips_069.json", 14498): 2,  # 'broad smile' vs 'sly grin' - different emotional quality for ニヤリ
    ("tips_069.json", 14500): 2,  # Generic 'tea' vs 'barley tea' - 麦茶 is specific, referenced in title
    ("tips_069.json", 14511): 3,  # 'tired voice' is OPPOSITE of へこたれない声 ('unfazed/undaunted voice')
    ("tips_069.json", 14512): 2,  # 'chided the girl' vs 'muttered about being hopeless' - different action
    ("tips_069.json", 14520): 2,  # 'higurashi' (series term) vs 'evening cicadas' - thematic choice
    ("tips_069.json", 14526): 4,  # New translation is entirely different from Japanese - content replacement error

    # tips_070.json
    ("tips_070.json", 14559): 3,  # Subject changed from 'they' to 'we' for kowtowing - meaningful nuance
    ("tips_070.json", 14560): 3,  # 庁議 mistranslated as 'debate session' + まいったなぁ misrendered
    ("tips_070.json", 14564): 3,  # Pressure direction reversed: at Chief vs through Minister from above
    ("tips_070.json", 14570): 5,  # REVERSED MEANING: "could possibly be behind" vs "could NOT have done it" - critical
    ("tips_070.json", 14573): 2,  # 'overtime budget' vs generic 'money' - minor specificity
    ("tips_070.json", 14574): 3,  # Who asks Akasaka: Chief himself vs commanding Kanou to do it
    ("tips_070.json", 14576): 3,  # 'on the down-low' (secret) vs 'keep close contact' (frequent) - opposite meaning

    # tips_071.json
    ("tips_071.json", 14606): 2,  # 'won't lose anything by picking' vs 'neither contains anything bad' - slight reframe
    ("tips_071.json", 14642): 3,  # 'wouldn't be hard to imagine' vs 'no way to know' - reversal of futility

    # tips_072.json
    ("tips_072.json", 14659): 2,  # 'closed her eyes' vs 'lowered her eyes' - different physical action
    ("tips_072.json", 14672): 2,  # 'longingly' vs 'melancholy expression' - different emotional quality
    ("tips_072.json", 14684): 2,  # 'stern' vs 'cold composure' - different emotional quality

    # tips_073.json
    ("tips_073.json", 14695): 2,  # Added 'decided to hold back' - minor omission in original
    ("tips_073.json", 14717): 3,  # 'It used to be this time...' is wrong for 刻限は夕方 ('It was evening')

    # tips_074.json
    ("tips_074.json", 14724): 3,  # 'They never warn you in books' vs 'no book needs to tell me' + 'plaything' vs 'doll'
    ("tips_074.json", 14725): 4,  # REVERSED SUBJECT: child can't feel loved vs PARENT loses affection - wrong subject

    # tips_075.json
    ("tips_075.json", 14781): 2,  # 'buried herself' (completed) vs 'tried to burrow' (attempted) - aspect change
    ("tips_075.json", 14789): 1,  # 'don't like' vs 'find unsettling' - mild tone difference
    ("tips_075.json", 14800): 2,  # 'voiced their respects' vs 'prayer and gratitude' - specificity
    ("tips_075.json", 14801): 1,  # Double negative vs assertive - stylistic, same meaning
    ("tips_075.json", 14805): 2,  # 'living incarnation' vs 'reincarnation' - theological distinction
    ("tips_075.json", 14809): 2,  # 'stopped listening' vs 'ignores mine' - temporal nuance

    # tips_076.json
    ("tips_076.json", 14814): 1,  # 'Parent-Teacher Day' vs 'parent observation day' - minor terminology
    ("tips_076.json", 14815): 2,  # 'my child' vs 'that child' - distancing pronoun difference
    ("tips_076.json", 14819): 2,  # Same 'my child' vs 'that child' issue
    ("tips_076.json", 14823): 3,  # 'when I wasn't taking care of her' vs 'behind my back' - misinterpretation
    ("tips_076.json", 14829): 2,  # 'living incarnation' vs 'reincarnation' - theological distinction
    ("tips_076.json", 14837): 4,  # WRONG SUBJECT: mother gets wet vs Rika gets wet; 'discuss weather' vs 'claim she predicts weather'
    ("tips_076.json", 14838): 3,  # Omits 'they say' framing; 'second-hand knowledge' vs 'parroting'
    ("tips_076.json", 14839): 3,  # Muddles the two-part conspiracy mechanism described in Japanese
    ("tips_076.json", 14848): 3,  # Same 'when I wasn't taking care of' vs 'beyond my sight' misinterpretation
    ("tips_076.json", 14856): 2,  # 'living incarnation' vs 'reincarnation' - same theological issue

    # tips_077.json
    ("tips_077.json", 14857): 1,  # Added 'a certain day' - minor omission
    ("tips_077.json", 14864): 2,  # 'dire circumstances' vs 'extreme psychological pressure' - specificity
    ("tips_077.json", 14869): 2,  # 'disappeared' vs 'was made to disappear' - agency difference
    ("tips_077.json", 14870): 3,  # 'curse' vs 'incidents' for 事件 - terminology error
    ("tips_077.json", 14873): 3,  # 'The possibilities are quite limited' vs 'To state my conclusion first' - fabricated meaning
    ("tips_077.json", 14874): 3,  # Omits 'acting on Sonozakis' wishes' - important agency detail
    ("tips_077.json", 14889): 3,  # Omits entire clause about confession of regrets

    # tips_100.json
    ("tips_100.json", 15284): 2,  # Adds 'I like my house' not in JPN, wrong tense
    ("tips_100.json", 15285): 3,  # 冷房 (air conditioning) mistranslated as 'fan'
    ("tips_100.json", 15286): 3,  # Wrong tense + 'near the window' vs 'veranda' (縁側)
    ("tips_100.json", 15287): 2,  # Omits 'Showa 58' era dating
    ("tips_100.json", 15288): 2,  # 'coming around the corner' vs 'in full swing' - stage of season
    ("tips_100.json", 15293): 2,  # 'something good was going to happen' vs 'auspicious start' - temporal framing

    # tips_101.json
    ("tips_101.json", 15307): 3,  # Omits hostess bar context (お店に内緒で)
    ("tips_101.json", 15308): 2,  # 'Private Manager' vs 'Exclusive Manager' - 専属 terminology

    # tips_102.json
    ("tips_102.json", 15309): 2,  # 'swimming pool' vs 'pool resort' + 'mom' vs 'Mama' childlike voice
    ("tips_102.json", 15311): 3,  # Third-person self-reference (Rena) + 'old man' vs 'uncle'
    ("tips_102.json", 15312): 3,  # Missing Rena's third-person self-reference + 'Daddy' vs 'Papa'
    ("tips_102.json", 15313): 3,  # Missing third-person + 'lots and lots' emphasis + 'spending money' specificity
    ("tips_102.json", 15314): 3,  # Missing third-person self-reference + 'became my daddy' structure
    ("tips_102.json", 15315): 3,  # Missing third-person + 'daddy' vs 'Papa' consistency

    # tips_103.json
    ("tips_103.json", 15316): 3,  # Multiple omissions: 'favorite' window, 'as always', 'modest verandah'
    ("tips_103.json", 15317): 3,  # Omits animal counter 一匹 and onomatopoeia どたどた
    ("tips_103.json", 15325): 2,  # 夕涼み as 'sunset' vs 'evening cool'
    ("tips_103.json", 15326): 2,  # 'thick clouds' vs 'clouds with just a hint of weight'
    ("tips_103.json", 15328): 1,  # 'raining' vs 'evening shower' - minor specificity
    ("tips_103.json", 15329): 2,  # 'deep-sea animals' vs 'deep-sea fish' + omits 'never normally seen'
    ("tips_103.json", 15334): 2,  # Missing questioning tone of か
    ("tips_103.json", 15338): 1,  # 'darker' vs 'lead-grey' - color specificity

    # tips_104.json
    ("tips_104.json", 15340): 1,  # Corporation vs Co., Ltd. + honorific removal
    ("tips_104.json", 15342): 3,  # Fabricated 'past visits and inquiries to our office'
    ("tips_104.json", 15344): 2,  # 'Basic Information' vs 'Details' for 記
    ("tips_104.json", 15345): 2,  # 新築 as 'Modern' vs 'New' - property type error
    ("tips_104.json", 15346): 4,  # Fabricated 'XXX Line' placeholder not in Japanese
    ("tips_104.json", 15351): 2,  # 'many prospective buyers' vs 'several times the available units'
    ("tips_104.json", 15355): 1,  # Corporation vs Co., Ltd.

    # tips_105.json
    ("tips_105.json", 15357): 2,  # Omitted 'saw Satoko off' detail
    ("tips_105.json", 15359): 2,  # Past vs present tense + 'without her' vs 'befitting her absence'
    ("tips_105.json", 15360): 2,  # 'what I wanted to do' (interpretation) vs 'was in that sort of mood' (literal)
    ("tips_105.json", 15361): 2,  # 'pulled one out' (futon) vs 'pulled it out' (specific concealed item)
    ("tips_105.json", 15362): 1,  # Minor omission of freezer detail
    ("tips_105.json", 15364): 3,  # かち割り氷 'cracked ice' mistranslated as 'store-bought ice'
    ("tips_105.json", 15366): 4,  # オレンジジュース mistranslated as 'mineral water'
    ("tips_105.json", 15367): 4,  # Vivid color description reduced to 'transparent water' - fabricated
    ("tips_105.json", 15368): 2,  # 'not the right way' vs 'ingredients cancel each other's qualities'
    ("tips_105.json", 15369): 5,  # Entire sentence bears no resemblance to Japanese (fabricated)
    ("tips_105.json", 15370): 5,  # Entirely unrelated to Japanese content (fabricated)
    ("tips_105.json", 15371): 4,  # 'enjoy a bottle for a long time' vs 'enjoy a sense of transgression' - fabricated
    ("tips_105.json", 15378): 4,  # Explicitly says 'alcohol' when JPN keeps it ambiguous - spoils reveal
    ("tips_105.json", 15380): 4,  # Omits critical reveal that the drink is non-alcoholic
    ("tips_105.json", 15381): 3,  # Omits 'inwardly laughing' - important characterization
    ("tips_105.json", 15383): 4,  # 'drown in alcohol' contradicts the story's non-alcoholic reveal
    ("tips_105.json", 15385): 3,  # Omits まぁまぁの部類 'acceptable range' - characterization detail
    ("tips_105.json", 15386): 3,  # 'not yet' vs 'again it won't work out' - loses time-loop implication
    ("tips_105.json", 15387): 3,  # Same また駄目 issue + 命日 rendering
    ("tips_105.json", 15391): 2,  # 'Are you serious?' vs 'Have you no self-awareness?'
    ("tips_105.json", 15393): 2,  # 'annoying' vs 'smothering creature' - different characterization
    ("tips_105.json", 15397): 5,  # Entire punchline of the tip completely lost

    # tips_106.json
    ("tips_106.json", 15399): 2,  # Missing '今年も' (once again this year)
    ("tips_106.json", 15400): 3,  # Missing sale component, 'high praise last year', 'held again'
    ("tips_106.json", 15401): 3,  # Missing guardian requirement + 'memorial gift' vs 'memory'
    ("tips_106.json", 15402): 4,  # Fabricated 'No. XX' placeholder + wrong plan name
    ("tips_106.json", 15403): 2,  # Missing 'dead trees' and 'rejuvenate'
    ("tips_106.json", 15407): 2,  # Simplified developmental framing

    # tips_107.json
    ("tips_107.json", 15409): 4,  # Wrong clinic name: 'Kuroda' vs correct reading of 四月一日
    ("tips_107.json", 15410): 2,  # 'Hello' vs 'Without preamble' for 前略
    ("tips_107.json", 15411): 4,  # Fabricates 'PTSD' diagnosis not in Japanese
    ("tips_107.json", 15413): 4,  # Fabricates 'self-mutilation' detail not in Japanese
    ("tips_107.json", 15415): 3,  # 'high possibility' + 'protect her family' vs 'secure her place'
    ("tips_107.json", 15416): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15417): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15418): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15419): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15420): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15421): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15422): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15423): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15424): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15425): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15426): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15427): 5,  # Entire content from wrong paragraph - misaligned
    ("tips_107.json", 15428): 5,  # Entire content from wrong paragraph - lunch order vs psychology text

    # tips_108.json
    ("tips_108.json", 15429): 5,  # Entirely wrong content - monitoring father vs listening as basic recovery
    ("tips_108.json", 15430): 5,  # Entirely wrong content - father's mental shock vs contagious delusions
    ("tips_108.json", 15431): 5,  # Conflated content from other lines
    ("tips_108.json", 15432): 5,  # Delusional parasitosis spreading vs family/partners susceptible

    # tips_109.json
    ("tips_109.json", 14011): 3,  # 'Five nails' (specific) vs 'multiple' (correct) + introduces nails as instrument
    ("tips_109.json", 14013): 2,  # 'intestines' vs 'internal organs' - scope of mutilation
    ("tips_109.json", 14020): 2,  # Omits 'as you requested' detail

    # tips_110.json
    ("tips_110.json", 15450): 2,  # 'soon left' vs 'the moment I stepped out' - timing precision
    ("tips_110.json", 15451): 2,  # Omits '今さらのように' (belatedly/only now)
    ("tips_110.json", 15454): 3,  # Loses self-correction structure and katakana emphasis
    ("tips_110.json", 15457): 2,  # Past vs present tense + 'who' vs 'what'
    ("tips_110.json", 15459): 3,  # Adds 'for it to be human' not in JPN + '貧弱' as 'vague' instead of 'meager'
    ("tips_110.json", 15462): 4,  # Drastically abbreviated: omits abnormal, protrusions, not human
    ("tips_110.json", 15467): 2,  # Omits 'cruelly vivid reality' contrast
    ("tips_110.json", 15469): 3,  # Replaces onomatopoeia with interpretive description
    ("tips_110.json", 15470): 3,  # Gravel 'kicked' vs 'burst and scattered' + omits '奇怪な音'
    ("tips_110.json", 15476): 2,  # Omits '絹を裂くような' simile
    ("tips_110.json", 15480): 2,  # Omits Rena's full name self-address
    ("tips_110.json", 15481): 2,  # Omits conditional coping mechanism
    ("tips_110.json", 15485): 4,  # 'lights flickering in my head' is entirely wrong for チリチリ (tingling/prickling)

    # tips_074.json - entry that was missed
    ("tips_074.json", 14775): 5,  # New translation contains WRONG dialogue (mother's line instead of Rika's)

    # tips_102.json - additional entries
    ("tips_102.json", 15314): 2,  # Missing third-person self-reference (Rena)
    ("tips_102.json", 15315): 2,  # Missing actual father reference confusion; 'Papa' vs 'dad' + structure
}

def process_file(filepath):
    """Process a single JSON file, adding changeScore to qualifying entries."""
    filename = filepath.split("/")[-1]

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified = 0
    for entry in data:
        if entry.get("significantChanges") is True and "changeScore" not in entry:
            msg_id = entry.get("MessageID")
            key = (filename, msg_id)
            if key in SCORES:
                entry["changeScore"] = SCORES[key]
                modified += 1
            else:
                print(f"WARNING: No score defined for {filename} MessageID {msg_id}", file=sys.stderr)

    if modified > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent='\t')
            f.write('\n')

    return modified

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = [
    str(BASE_DIR / "tips_069.json"),
    str(BASE_DIR / "tips_070.json"),
    str(BASE_DIR / "tips_071.json"),
    str(BASE_DIR / "tips_072.json"),
    str(BASE_DIR / "tips_073.json"),
    str(BASE_DIR / "tips_074.json"),
    str(BASE_DIR / "tips_075.json"),
    str(BASE_DIR / "tips_076.json"),
    str(BASE_DIR / "tips_077.json"),
    str(BASE_DIR / "tips_100.json"),
    str(BASE_DIR / "tips_101.json"),
    str(BASE_DIR / "tips_102.json"),
    str(BASE_DIR / "tips_103.json"),
    str(BASE_DIR / "tips_104.json"),
    str(BASE_DIR / "tips_105.json"),
    str(BASE_DIR / "tips_106.json"),
    str(BASE_DIR / "tips_107.json"),
    str(BASE_DIR / "tips_108.json"),
    str(BASE_DIR / "tips_109.json"),
    str(BASE_DIR / "tips_110.json"),
]

total_modified = 0
for filepath in FILES:
    count = process_file(filepath)
    print(f"{filepath.split('/')[-1]}: {count} entries scored")
    total_modified += count

print(f"\nTotal entries scored: {total_modified}")
