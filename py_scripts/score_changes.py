#!/usr/bin/env python3
"""
Score translation changes in Higurashi JSON files.
Adds changeScore (1-5) to entries with significantChanges: true.

Scale:
1 = Trivial (name spelling, Meep/Mii)
2 = Minor (small factual, context clear)
3 = Moderate (emotional register, specificity, cultural terms)
4 = Major (wrong subject, reversed meaning, fabricated content)
5 = Critical (missing content, misalignment, opposite plot-critical meaning)
"""

import json
import re
import sys
import os
from pathlib import Path

def score_entry(entry):
    """Assign a changeScore based on changeReason, TextENG, and TextENGNew."""
    reason = entry.get('changeReason', '')
    old = entry.get('TextENG', '')
    new = entry.get('TextENGNew', '')

    reason_lower = reason.lower()

    # === SCORE 5: Critical ===
    if 'does not correspond to this entry' in reason_lower:
        return 5
    if 'does not correspond to the japanese source text' in reason_lower:
        return 5
    if 'from a different adaptation' in reason_lower:
        return 5
    if 'completely different content from original translation' in reason_lower:
        return 5
    if 'different narrative overlay' in reason_lower:
        return 5
    if 'incorrectly assigned from a different scene' in reason_lower:
        return 5
    if 'systematic misalignment' in reason_lower:
        return 5
    if 'displaced/misaligned text' in reason_lower:
        return 5
    if 'contains displaced' in reason_lower:
        return 5
    if 'completely restructures this scene' in reason_lower and 'does not correspond' in reason_lower:
        return 5
    if 'missing content' in reason_lower or 'omits entire' in reason_lower:
        return 5
    if 'opposite' in reason_lower and ('plot' in reason_lower or 'critical' in reason_lower):
        return 5
    # Speaker/listener swap in plot-critical context
    if 'speaker is the dreamer' in reason_lower and 'listener is the dreamer' in reason_lower:
        return 5
    # "I dream" vs "you dream" - changes who is experiencing
    if "'i dream'" in reason_lower and "'you dream'" in reason_lower:
        return 5
    # NEW translation is completely wrong / unrelated
    if 'new translation is completely wrong' in reason_lower:
        return 5
    if 'completely wrong' in reason_lower and 'unrelated' in reason_lower:
        return 5
    # Check for cases where new text is suspiciously short vs old (possible misalignment)
    # Only apply when the changeReason doesn't already explain the change
    if new and old and len(new.strip()) < len(old.strip()) * 0.2 and len(old.strip()) > 50:
        if not reason or 'misalign' in reason_lower or 'displaced' in reason_lower:
            return 5

    # === SCORE 4: Major ===
    # Mistranslation corrections
    if 'mistranslat' in reason_lower:
        return 4
    # Misreads / misinterprets the Japanese
    if 'misread' in reason_lower:
        return 4
    if 'misinterpret' in reason_lower:
        return 4
    # Fabricated content not in source
    if 'innuendo' in reason_lower and 'not present' in reason_lower:
        return 4
    if 'not in jpn' in reason_lower or 'not in the japanese' in reason_lower:
        if 'adds' in reason_lower or 'introduces' in reason_lower:
            return 4
    # "not present in jpn/japanese"
    if re.search(r'not present in (?:the )?(?:jpn|japanese)', reason_lower):
        return 4
    # "not in the Japanese" with context
    if re.search(r'not (?:in|present in) (?:the )?(?:japanese|jpn)', reason_lower):
        if re.search(r'(?:old|original) (?:adds?|includes?|says)', reason_lower):
            return 4
    # Wrong factual content (asphalt vs gunpowder)
    if ('asphalt' in reason_lower and 'gunpowder' in reason_lower) or \
       ('火薬' in reason and 'asphalt' in reason_lower):
        return 4
    # Completely different content (mistranslation)
    if "'if i could have'" in reason_lower and "'what that meant'" in reason_lower:
        return 4
    # Wrong subject / attribution
    if 'incorrectly attributes' in reason_lower:
        return 4
    if 'wrong subject' in reason_lower or 'wrong character' in reason_lower:
        return 4
    if 'different attribution' in reason_lower or 'different agent' in reason_lower:
        return 4
    # "confuses who" - wrong subject identification
    if 'confuses who' in reason_lower:
        return 4
    # Reversed characterization (tight vs tenuous)
    if 'tight' in reason_lower and 'tenuous' in reason_lower:
        return 4
    # Dream framing change (plot-relevant in saikoroshi)
    if "'dream'" in reason_lower and 'quoted' in reason_lower and 'framing' in reason_lower:
        return 4
    if 'separates' in reason_lower and 'dream' in reason_lower and 'afterthought' in reason_lower:
        return 4
    # Perspective shift
    if 'perspective shift from first-person to third-person' in reason_lower:
        return 3
    if 'perspective shift' in reason_lower:
        return 4
    # Reversed meaning (various patterns)
    if 'reversed meaning' in reason_lower or 'reverses the meaning' in reason_lower:
        return 4
    if 'reverses' in reason_lower and ('meaning' in reason_lower or 'territory' in reason_lower or 'conditional' in reason_lower):
        return 4
    if 'completely reverses' in reason_lower:
        return 4
    # Generic 'reverses' (e.g. spatial relationship reversed)
    if 'reversed' in reason_lower and ('spatial' in reason_lower or 'relationship' in reason_lower):
        return 4
    # Old is closer to JPN than new
    if 'old is closer' in reason_lower:
        return 4
    # Subject changed (I -> we, etc.)
    if 'subject changed' in reason_lower:
        return 4
    # Subject/perspective changes in entry
    if "changes the subject/perspective" in reason_lower:
        return 4
    # Different names/references (generic)
    if 'different names/references' in reason_lower:
        return 4
    # 'him' vs narrator correctly identified
    if "'him'" in reason_lower and 'correctly identifies' in reason_lower:
        return 4
    # Fabricated / invented content
    if 'fabricat' in reason_lower or 'invented' in reason_lower or 'invents' in reason_lower:
        return 4
    # Critical correction
    if 'critical' in reason_lower and 'corrected' in reason_lower:
        return 4
    # Opposite action/direction/emotion
    if 'opposite' in reason_lower:
        return 4
    # "Old reverses" / "reverses subject"
    if 'old reverses' in reason_lower or 'reverses subject' in reason_lower:
        return 4
    # "completely different" descriptions
    if 'completely different' in reason_lower:
        return 4
    # "entirely different"
    if 'entirely different' in reason_lower:
        return 4
    # "Fundamentally different"
    if 'fundamentally different' in reason_lower:
        return 4
    # "Complete meaning change"
    if 'complete meaning change' in reason_lower:
        return 4
    # "Old completely" rewrites/misread
    if re.search(r'(?:old|original) completely', reason_lower):
        return 4
    # "Old incorrectly"
    if re.search(r'(?:old|original) incorrectly', reason_lower):
        return 4
    # "Changing/changes characterization"
    if 'changing characterization' in reason_lower or 'changes characterization' in reason_lower:
        return 4
    # "Invitation is reversed" / direction reversed
    if 'invitation is reversed' in reason_lower:
        return 4
    # "Corrected fabricated"
    if 'corrected fabricated' in reason_lower:
        return 4
    # Old says X but should be Y / old says but Japanese means Y
    if 'old says' in reason_lower and ('should' in reason_lower or 'incorrectly' in reason_lower or 'wrongly' in reason_lower):
        return 4
    if 'old says' in reason_lower and ('japanese' in reason_lower or 'jpn' in reason_lower):
        if 'correctly' in reason_lower or 'means' in reason_lower or 'actually' in reason_lower:
            return 4
    # "Old says" with Two vs Three Families
    if 'old says' in reason_lower and ('two families' in reason_lower and 'three families' in reason_lower):
        return 4
    # "Old says" with speaker/perspective change
    if 'old says' in reason_lower and ('speaker' in reason_lower or 'different speaker' in reason_lower or 'first person' in reason_lower):
        return 4
    # "Different subject" pattern
    if 'different subject' in reason_lower:
        return 4

    # === Negation / polarity - context dependent ===
    if 'negation' in reason_lower or 'polarity' in reason_lower:
        return _score_negation(entry)

    # === SCORE 3: Moderate ===
    # Complete rewrite with substantially different content
    if 'complete rewrite' in reason_lower:
        return 3
    # At least one sentence completely rewritten
    if 'completely rewritten' in reason_lower:
        return 3
    # Substantially reworded with different semantic content
    if 'substantially reworded' in reason_lower and 'semantic' in reason_lower:
        return 3
    # Changed verb/word with meaning shift (e.g. 'get rid of' to 'erase')
    if 'changed' in reason_lower and ('implies' in reason_lower or 'shifts' in reason_lower):
        return 3
    # Substantially revises to better match Japanese
    if 'substantially revises' in reason_lower:
        return 3
    # Character speech pattern preservation (Rena third-person)
    if 'third-person self-reference' in reason_lower:
        return 3
    # 'Tokyo' in quotes as code name
    if "'tokyo' in quotes" in reason_lower:
        return 3
    # Conditional vs declarative
    if 'conditional' in reason_lower and ('declarative' in reason_lower or 'conditional' in reason_lower):
        return 3
    # Brink vs bottom of despair (different metaphor)
    if 'brink' in reason_lower and 'bottom' in reason_lower:
        return 3
    # Original world vs last world
    if 'original world' in reason_lower and ('last world' in reason_lower or '元の世界' in reason):
        return 3
    # Watanagashi day vs night
    if 'night' in reason_lower and 'watanagashi' in reason_lower:
        return 3
    # Housewife character-focused vs role-focused
    if 'housewife' in reason_lower or 'involvement' in reason_lower:
        if 'character-focused' in reason_lower or 'role-focused' in reason_lower:
            return 3
    # Regular intervals vs intermittent
    if 'regular intervals' in reason_lower and 'intermittent' in reason_lower:
        return 3
    # Multiple significant content differences
    if 'multiple significant content differences' in reason_lower:
        return 3
    # Substantially different
    if 'substantially different' in reason_lower:
        return 3
    # Substantially rewords
    if 'substantially rewords' in reason_lower:
        return 3
    # "Substantially rewritten with very different wording"
    if 'substantially rewritten' in reason_lower:
        return 3
    # Different meaning/nuance
    if 'different meaning' in reason_lower:
        return 3
    # Different phrasing affecting interpretation
    if 'different phrasing' in reason_lower and ('may affect' in reason_lower or 'reader interpretation' in reason_lower):
        return 3
    # "Translation uses different phrasing that shifts the reader's understanding"
    if 'shifts the reader' in reason_lower:
        return 3
    if 'shifts' in reason_lower and 'understanding' in reason_lower:
        return 3
    # "Substantially different translation that conveys the scene differently"
    if 'conveys the scene differently' in reason_lower:
        return 3
    # Different key terms
    if 'different key terms' in reason_lower:
        return 3
    # Significantly reworded, altering meaning
    if 'significantly reworded' in reason_lower and 'altering meaning' in reason_lower:
        return 3
    # Significantly different wording/content
    if 'significantly different' in reason_lower:
        return 3
    # Translation wording changes affect meaning
    if 'wording changes affect meaning' in reason_lower:
        return 3
    # Emotional register / tone shift
    if 'emotional register' in reason_lower or 'tone shift' in reason_lower:
        return 3
    # Cultural terms
    if 'cultural' in reason_lower:
        return 3
    # Different key action verbs
    if 'different key action verb' in reason_lower:
        return 3
    # Captures conditional
    if 'captures the conditional' in reason_lower:
        return 3
    # Adds detail from Japanese source (correction)
    if 'adds detail from the japanese' in reason_lower or 'from the japanese source' in reason_lower:
        return 3
    # Omits content (partial)
    if 'omits content' in reason_lower or 'omits or replaces' in reason_lower:
        return 3
    # Adds substantial additional content
    if 'adds substantial additional content' in reason_lower:
        return 3
    # Reaction completely changed (laughter to stammering)
    if 'reaction completely changed' in reason_lower:
        return 3
    # Restructures and rewords
    if 'restructures and rewords' in reason_lower:
        return 3
    # Question vs statement
    if ('question' in reason_lower and 'statement' in reason_lower) or \
       ('question rather than a statement' in reason_lower):
        return _score_question_statement(entry)
    # Multiple content words differ
    if 'multiple content words differ' in reason_lower:
        return 3
    # Different vocabulary resulting in meaningfully different rendering
    if 'different vocabulary' in reason_lower and 'meaningfully different' in reason_lower:
        return 3
    # "Narrative perspective changed from first person to third person"
    if 'narrative perspective changed' in reason_lower or 'narrative perspective' in reason_lower:
        return 3
    # Generic "different verb/action/description/etc." patterns
    if re.search(r'different (?:verb|action|description|position|intensity|sound|emotion|words?|food|criticism|question|expression|implication|consequence|philosophy|last line)\b', reason_lower):
        return 3
    # "New translation adds" detail from Japanese (accuracy improvement)
    if re.search(r'new (?:translation )?adds', reason_lower):
        return 3
    # "Old omits" / "Original omits" / "New omits"
    if re.search(r'(?:old|original|new) (?:translation )?omits?', reason_lower):
        return 3
    # "New correctly" / "New accurately"
    if re.search(r'new (?:translation )?(?:correctly|accurately)', reason_lower):
        return 3
    # "Old translates X as Y" (correction pattern)
    if re.search(r'(?:old|original) translates?.*(?:as|with) ', reason_lower):
        return 3
    # "Specific target removed" / "Specific X removed"
    if 'specific' in reason_lower and 'removed' in reason_lower:
        return 3
    # "New translation captures" / "preserves" / "renders" / "includes" Japanese nuance
    if re.search(r'new (?:translation )?(?:captures?|preserves?|renders?|includes?)', reason_lower):
        return 3
    # "New translation condenses" / "expands"
    if 'condenses' in reason_lower or 'expands' in reason_lower:
        return 3
    # "Content differs significantly"
    if 'content differs significantly' in reason_lower:
        return 3
    # "Different framing" / "different temporal" / "different focus" / etc.
    if re.search(r'different (?:framing|temporal|focus|specificity|causality)\b', reason_lower):
        return 3
    # "Old says X; new says Y" pattern (generic mismatch)
    if re.search(r"old says .{5,}; new says", reason_lower):
        return 3
    # "Changed from X to Y" / "Changed 'X' to 'Y'"
    if re.search(r"changed (?:from |')", reason_lower):
        return 3
    # "Reframed" pattern
    if 'reframed' in reason_lower:
        return 3
    # "Added X matching JPN"
    if re.search(r'added .{0,30}matching jpn', reason_lower):
        return 3
    # "Removed fabricated" (old had fabricated content removed in new)
    if 'removed fabricated' in reason_lower:
        return 3
    # Incorrectly merges dialogue
    if 'incorrectly merges' in reason_lower:
        return 3
    # "Substantially revise" generic
    if 'substantially revise' in reason_lower:
        return 3

    # === SCORE 2: Minor ===
    # Name/term corrections (village chief for 村長)
    if 'village chief' in reason_lower and '村長' in reason:
        return 2
    # Different character/location names referenced
    if 'different character/location names' in reason_lower:
        return 2
    # Adds or removes specific names/terms
    if 'adds specific names' in reason_lower or 'removes specific names' in reason_lower:
        return 2
    # Adds honorific
    if 'adds' in reason_lower and ('honorific' in reason_lower or '-san' in reason_lower or '-kun' in reason_lower):
        return 2
    # Adds detail capturing Japanese omitted in old
    if 'adds' in reason_lower and ('capturing' in reason_lower or 'omitted in old' in reason_lower):
        return 2
    # More accurately reflecting / better captures
    if 'more accurately' in reason_lower or 'better captures' in reason_lower:
        return 2
    # Child-register changes (Mommy/Daddy)
    if 'child-register' in reason_lower or 'child register' in reason_lower:
        return 2
    # Romanization changes
    if 'romanization' in reason_lower:
        return 2
    # Numerical value changes
    if 'numerical values differ' in reason_lower or 'numerical values' in reason_lower:
        if 'showa' in old.lower() or 'showa' in new.lower():
            return 2
        return 2
    # Inline voice tags removed only
    if reason == 'Inline voice/control tags removed from new translation, which may affect voice playback.':
        return 1
    # Translation reworded AND voice tags removed (minor)
    if 'reworded and inline voice tags removed' in reason_lower:
        return 2
    # Temporal marker (yet)
    if "temporal marker" in reason_lower and "'yet'" in reason_lower:
        return 2
    # Temporal framing
    if 'temporal framing' in reason_lower:
        return 2
    # Added specificity (bloomers -> gym bloomers)
    if 'added specificity' in reason_lower:
        return 2
    # Younger brother (more precise)
    if 'younger brother' in reason_lower and 'brother' in reason_lower:
        return 2
    # Tense changed (present perfect -> past perfect)
    if 'tense changed' in reason_lower:
        return 2
    # Presence vs felt
    if "'presence'" in reason_lower and '気配' in reason:
        return 2
    # Well -> Because
    if "'well' to 'because'" in reason_lower or ("'well'" in reason_lower and "'because'" in reason_lower and 'だって' in reason):
        return 2
    # Tickling unbearable (adds nuance from source)
    if 'tickl' in reason_lower and 'unbearable' in reason_lower:
        return 2
    # Mountain of ancient texts vs pile of documents
    if 'ancient texts' in reason_lower and 'documents' in reason_lower:
        return 2
    # More detailed translation
    if 'substantially more detailed' in reason_lower:
        return 2
    # Silent ellipsis -> vocalization
    if 'silent ellipsis' in reason_lower:
        return 2
    # Small factual detail
    if 'small' in reason_lower and 'factual' in reason_lower:
        return 2
    # Name removal: check if name still present
    if 'removes reference to' in reason_lower:
        name_match = re.search(r'removes reference to (\w+)', reason_lower)
        if name_match:
            name = name_match.group(1)
            old_has = name.lower() in old.lower()
            new_has = name.lower() in new.lower()
            if old_has and new_has:
                return 1  # Just honorific dropped (-chan)
            elif old_has and not new_has:
                return 2  # Name replaced with pronoun
        return 2
    # Name added
    if 'adds specific name' in reason_lower or 'adds reference to' in reason_lower:
        return 2
    # Removes specific name (generic pattern from earlier scripts)
    if 'removes specific name' in reason_lower:
        name_match = re.search(r'removes specific name.*?:\s*(\w+)', reason_lower)
        if name_match:
            name = name_match.group(1)
            if name in ('rika', 'hanyuu', 'oyashiro'):
                return 3
        return 3
    # Group name change (Mountain Dogs -> Yamainu)
    if 'mountain dogs' in reason_lower and 'yamainu' in reason_lower:
        return 2
    # 'Stranger' characterization matching JPN
    if 'stranger' in reason_lower and 'characterization' in reason_lower:
        return 2

    # === SCORE 1: Trivial ===
    # Meep/Mii
    if 'meep' in reason_lower and 'mii' in reason_lower:
        return 1
    if "'meep'" in reason_lower or "'mii'" in reason_lower:
        if 'transliteration' in reason_lower or 'vocalization' in reason_lower:
            return 1
    # Name spelling only
    if 'name spelling' in reason_lower:
        if 'also' in reason_lower:
            return 2
        return 1
    # Pure punctuation
    if 'trivial' in reason_lower or ('punctuation' in reason_lower and 'only' in reason_lower):
        return 1
    # Reaction word (Eh -> Huh, minor interjection)
    if 'reaction word changed' in reason_lower or 'reaction changed from' in reason_lower:
        if 'pain' in reason_lower:
            return 2
        return 1
    # Oops -> ah
    if "'oops'" in reason_lower and "'ah'" in reason_lower:
        return 2

    # === Substantially rewritten (auto-generated reasons with word diffs) ===
    if 'substantially rewritten' in reason_lower:
        return _score_from_text_comparison(old, new)

    # === Brief line changes ===
    if 'brief line' in reason_lower and 'different key words' in reason_lower:
        return _score_brief_line(entry)

    # === Default heuristics ===
    if 'conveys' in reason_lower and 'different' in reason_lower:
        return 3
    if 'alters' in reason_lower and 'nuance' in reason_lower:
        return 3
    if 'rephrased' in reason_lower:
        return 3
    if 'drops' in reason_lower and 'qualifier' in reason_lower:
        return 3
    if 'philosophical' in reason_lower:
        return 3
    if 'imagery' in reason_lower or 'more vivid' in reason_lower:
        return 3
    if 'preserves' in reason_lower and ('metaphor' in reason_lower or 'distinction' in reason_lower):
        return 3
    if 'amount of detail' in reason_lower:
        return 3

    # Generic fallback using text comparison
    if old and new:
        return _score_from_text_comparison(old, new)

    return 3


def _score_from_text_comparison(old, new):
    """Score based on word-level similarity between old and new translations."""
    def _normalize(text):
        text = re.sub(r'@[a-zA-Z][^\s.]*\.?', '', text)
        text = text.replace('``', '"').replace("''", '"').replace('\u201c', '"').replace('\u201d', '"')
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()

    old_n = _normalize(old)
    new_n = _normalize(new)

    if not old_n or not new_n:
        return 3

    old_words = set(old_n.split())
    new_words = set(new_n.split())

    if not old_words or not new_words:
        return 3

    overlap = old_words & new_words
    union = old_words | new_words
    jaccard = len(overlap) / len(union) if union else 1.0

    if jaccard > 0.85:
        return 1  # Very similar, trivial
    elif jaccard > 0.65:
        return 2  # Minor differences
    elif jaccard > 0.40:
        return 3  # Moderate rewrite
    else:
        return 3  # Substantial rewrite but without specific error indicators, cap at 3


def _score_negation(entry):
    """Score negation/polarity changes.

    Most negation/polarity entries in these files are rephrasing with similar
    overall meaning (e.g. 'can't get in' vs 'no way I could get in'), not
    true reversals. Default to 3. Only score 4 if the overall sentiment
    truly flips (e.g. affirmative statement becomes denial of same).
    """
    old = entry.get('TextENG', '')
    new = entry.get('TextENGNew', '')

    eng_clean = re.sub(r'@[kvyrwk|]+\S*\.?', '', old).strip().lower()
    new_clean = re.sub(r'@[kvyrwk|]+\S*\.?', '', new).strip().lower()

    # Very short lines where negation is added/removed are more impactful
    stripped_old = re.sub(r'[``""\'"\s!?.~\n]', '', eng_clean)
    if len(stripped_old) < 15:
        # Short line: adding "can't" to "That's..." changes meaning notably
        return 3

    # Check for subject/perspective changes embedded in negation entries
    if "'i'" in entry.get('changeReason', '').lower() and "'we'" in entry.get('changeReason', '').lower():
        return 4
    if "'i'" in entry.get('changeReason', '').lower() and "'you'" in entry.get('changeReason', '').lower():
        return 4

    # Default: most are moderate rephrasing, not true reversals
    return 3


def _score_question_statement(entry):
    """Score question vs statement changes."""
    old = entry.get('TextENG', '')
    eng_clean = re.sub(r'[``""\'"\s@kvyrwk|.\n]', '', old)
    if len(eng_clean) < 15:
        return 2
    return 3


def _score_brief_line(entry):
    """Score brief lines with different key words."""
    old = entry.get('TextENG', '')
    eng_clean = re.sub(r'[``""\'"\s!?.~@\n]', '', old)
    if len(eng_clean) < 10:
        return 1
    if len(eng_clean) < 20:
        return 2
    return 3


def process_file(filepath):
    """Process a single file, adding changeScore to qualifying entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scored = 0
    scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for entry in data:
        if entry.get('significantChanges') == True and 'changeScore' not in entry:
            score = score_entry(entry)
            entry['changeScore'] = score
            scored += 1
            scores[score] += 1

    if scored > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return scored, scores


def main():
    base = Path(__file__).resolve().parent.parent
    files = [
        'tokihogushi_08.json', 'tokihogushi_09.json', 'tokihogushi_10.json', 'tokihogushi_end.json',
        'tsukiotoshi_01.json', 'tsukiotoshi_02.json', 'tsukiotoshi_03.json', 'tsukiotoshi_04.json',
        'tsukiotoshi_05.json', 'tsukiotoshi_06.json', 'tsukiotoshi_07.json', 'tsukiotoshi_08.json',
        'tsukiotoshi_10.json',
        'tsumihoroboshi_01.json', 'tsumihoroboshi_02.json', 'tsumihoroboshi_03.json', 'tsumihoroboshi_04.json',
        'tsumihoroboshi_05.json', 'tsumihoroboshi_06.json', 'tsumihoroboshi_07.json', 'tsumihoroboshi_08.json',
        'tsumihoroboshi_09.json', 'tsumihoroboshi_10.json', 'tsumihoroboshi_11.json', 'tsumihoroboshi_12.json',
    ]

    total_scored = 0
    total_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for fname in files:
        fpath = str(base / fname)
        scored, scores = process_file(fpath)
        total_scored += scored
        for k in scores:
            total_scores[k] += scores[k]

        dist = ', '.join(f'{k}:{v}' for k, v in sorted(scores.items()) if v > 0)
        print(f'{fname}: {scored} entries scored | {dist}')

    print(f'\n=== TOTALS ===')
    print(f'Total entries scored: {total_scored}')
    dist = ', '.join(f'{k}:{v}' for k, v in sorted(total_scores.items()) if v > 0)
    print(f'Score distribution: {dist}')


if __name__ == '__main__':
    main()
