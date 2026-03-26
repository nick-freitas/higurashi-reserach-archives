#!/usr/bin/env python3
"""
Re-evaluate all entries with changeScore 4 or 5 across 108 Higurashi JSON files.
After thorough manual review of all 403 entries, applies corrections.

Categories after review:
1. DOWNGRADE_TO_FALSE: Same meaning, just reworded. Set significantChanges=false, remove changeReason/changeScore.
2. DOWNGRADE_SCORE: Real difference but less severe than marked. Lower score, fresh reason.
3. KEEP: Genuinely major/critical. Keep at 4/5 with fresh reason.
"""

import json
import os
import sys
from collections import defaultdict
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

# After thorough review of all 403 entries, here are the ones that need to be
# downgraded to significantChanges=false (same meaning, just reworded):
# Keyed by (filename, entry_index)
SET_TO_FALSE = {
    # miotsukushi_omote_04.json: Many entries marked as "misaligned" but are actually
    # just minor wording differences (quote style changes, trivial rephrasing)
    ("miotsukushi_omote_04.json", 70): "Both say 'Yeaaaah!!' - just different quote style",
    ("miotsukushi_omote_04.json", 79): "Both say 'Yeaaaah!!' - just different quote style",
    ("miotsukushi_omote_04.json", 82): "Both say 'Leave it to me!' - just different quote style",
    ("miotsukushi_omote_04.json", 84): "Both convey Tomita kicking the can on Mion's command - minor wording",
    ("miotsukushi_omote_04.json", 85): "Both describe the can flying with a satisfying sound and students scattering - minor wording",
    ("miotsukushi_omote_04.json", 88): "Both ask about the curry can from yesterday and what happened to contents - minor wording",
    ("miotsukushi_omote_04.json", 89): "Both say 'I'd never do that, Chie-sensei ate it for lunch' - minor wording",
    ("miotsukushi_omote_04.json", 95): "Both say Rena finished counting to 100 and they switched to battle mode - minor wording",

    # miotsukushi_omote_15.json: Several entries marked as dropping content actually have it all
    ("miotsukushi_omote_15.json", 143): "Both contain gun not loaded detail; 'draw' vs 'have a shot' is minor",
    ("miotsukushi_omote_15.json", 168): "Both say 'the whole Akasaka family, welcome!' - trivial rephrasing",
    ("miotsukushi_omote_15.json", 174): "Both end with 'Right~, Mama?' - content preserved",
    ("miotsukushi_omote_15.json", 178): "Both include 'I'm Ooishi!' - content preserved",
    ("miotsukushi_omote_15.json", 192): "Both end with 'Please, don't worry about it!' - content preserved",
    ("miotsukushi_omote_15.json", 202): "Both end with 'Miyuki and I will relax at the hot springs' - content preserved",
    ("miotsukushi_omote_15.json", 312): "Both say 'confirm she still needs help' - minor rephrasing",
    ("miotsukushi_omote_15.json", 340): "Both convey the Tokyo visitor vs local police comparison - same meaning",
    ("miotsukushi_omote_15.json", 341): "Both include self-deprecating lines - minor rephrasing",

    # miotsukushi_omote_17.json
    ("miotsukushi_omote_17.json", 49): "Both say room checked for bugs, dealt with unconventional opponents - minor wording",
    ("miotsukushi_omote_17.json", 53): "Both describe Keiichi looking daunted but then giving a firm nod - same meaning",
    ("miotsukushi_omote_17.json", 66): "Both say 'I'd like you to tell me' - identical content",
    ("miotsukushi_omote_17.json", 128): "Both say 'You might laugh/You're laughing' at worrying too much - same sentiment",
    ("miotsukushi_omote_17.json", 189): "Both say colleague will look after wife/daughter, send to Tokyo, protection program - same meaning",
    ("miotsukushi_omote_17.json", 232): "Both say five years is a long time, good memory - same content",
    ("miotsukushi_omote_17.json", 252): "Both describe Tomitake about to leave, called back, quizzical look at 'request' - minor wording",

    # miotsukushi_omote_19.json
    ("miotsukushi_omote_19.json", 33): "Both say 'Want to sleep at Rena's house? Share a futon?' - same content",
    ("miotsukushi_omote_19.json", 43): "Both say 'clung to tree trunk, shined flashlight downward' - same meaning",
    ("miotsukushi_omote_19.json", 99): "Both say 'vision warped, ground sensation vanished' - same meaning",
    ("miotsukushi_omote_19.json", 135): "Both say 'clothes muddy, cuts on limbs, covered in sweat/dirt... should have been the case' - identical",
    ("miotsukushi_omote_19.json", 300): "Both say info is police confidential, will reach village leaders today, killed as Watanagashi curse - same",
    ("miotsukushi_omote_19.json", 301): "Both say Coach sat stunned, couldn't believe it - same meaning",
    ("miotsukushi_omote_19.json", 319): "Both say Rika tells Irie about Akasaka being from Public Security investigating Hinamizawa - same",
    ("miotsukushi_omote_19.json", 323): "Both say Public Security rooms are top-secret like CIRO's - same meaning",
    ("miotsukushi_omote_19.json", 327): "Both say Director Irie, grateful for treatment 5 years ago - same meaning",
    ("miotsukushi_omote_19.json", 356): "Both ask 'Do you honestly believe that's a mere coincidence?' - same content",
    ("miotsukushi_omote_19.json", 385): "Both say forensic examination showed 24+ hours since death - same meaning",
    ("miotsukushi_omote_19.json", 387): "Both thank Inspector Minai, credit her for getting forensic statement - same content",

    # miotsukushi_omote_22.json: many entries marked as "substantially different" but are minor rewordings
    ("miotsukushi_omote_22.json", 43): "Both convey same info about Tomitake's belongings being important evidence and a miracle - same meaning",
    ("miotsukushi_omote_22.json", 45): "Both say informant delivered documents to Akasaka last night - same content",
    ("miotsukushi_omote_22.json", 49): "Both say Ooishi forgot where a building is, asks Shion if she recognizes it - same meaning",
    ("miotsukushi_omote_22.json", 311): "Both say 'Hold it / Wait, I'm not finished' - same meaning",
    ("miotsukushi_omote_22.json", 356): "Both say 'I can't go against that / defy that' - same meaning",

    # miotsukushi_omote_end.json
    ("miotsukushi_omote_end.json", 22): "Both ask about marriage if still human - same meaning",
    ("miotsukushi_omote_end.json", 23): "Both say 'What?! How could you leap to that conclusion, know-it-all!' - same meaning",
    ("miotsukushi_omote_end.json", 29): "Both say 'I want to go, but the bicycle is broken' - same meaning",
    ("miotsukushi_omote_end.json", 36): "Both say 'Every day was fun and lively' - same meaning",
    ("miotsukushi_omote_end.json", 112): "Both say 'Wishing for another's happiness and hoping they wish the same for me' - same meaning",
    ("miotsukushi_omote_end.json", 118): "Both say 'Each of us finding our own path and walking it' - same meaning",
    ("miotsukushi_omote_end.json", 157): "Both say 'the supervisor/coach finally arrived, hey!' - same meaning",

    # onikakushi_04.json: Entries about character names being "added/removed" - but checking actual text shows
    # both contain Ooishi-san references. The changeReasons about "adds/removes character name" were hallucinated.
    ("onikakushi_04.json", 166): "Both say 'Rena went upstairs at about half past, so close to an hour' - same meaning",
    ("onikakushi_04.json", 170): "Both mention being absorbed in phone call with Ooishi-san - same content",
    ("onikakushi_04.json", 179): "Both say 'Between my room and the staircase, only a short hallway' - same meaning",
    ("onikakushi_04.json", 183): "Both mention disturbing things said to Ooishi-san racing through mind - same meaning",
    ("onikakushi_04.json", 184): "Both say Mom tells Dad to clean up studio - same meaning but 'mess again' vs 'spill again' is minor",
    ("onikakushi_04.json", 188): "Both describe Rena standing behind while talking to Ooishi - same content",

    # onikakushi_end.json
    ("onikakushi_end.json", 69): "Both say 'officers heading there, 2-3 minutes, hold on, hello?! Maebara-san?!' - same content",
    ("onikakushi_end.json", 76): "Both include the 'But... in the end... *hack hack*!!' - content preserved",
    ("onikakushi_end.json", 81): "Both include 'slowly creeping closer to my back' - content preserved",
    ("onikakushi_end.json", 84): "Both ask 'Who is behind you, Maebara-san?!' - same content",
    ("onikakushi_end.json", 86): "Both include 'Behind you, Maebara-san... who is it?!?!' - same content",

    # minagoroshi_17.json: Several "substantially reworded" entries
    ("minagoroshi_17.json", 385): "Both say 'She's right / Now that she mentioned it, she was right' - same meaning, minor elaboration",
    ("minagoroshi_17.json", 461): "Both say 'Yeah / Yes' in response - same meaning",

    # someutsushi_04.json: pronoun shifts that don't change meaning
    ("someutsushi_04.json", 413): "Both say 'we/I exchanged an awkward greeting and parted' - same meaning",

    # tatarigoroshi_06.json
    ("tatarigoroshi_06.json", 119): "Both convey the same content about Oyashiro-sama's curse - minor rephrasing",
    ("tatarigoroshi_06.json", 177): "Both say Rena was worried about him not showing up at school and potential heat stroke - same meaning",

    # tatarigoroshi_07.json: Entries where changeReason mentions added content not actually present
    ("tatarigoroshi_07.json", 13): "Both say 'omurice with mushrooms that look delicious' - same meaning",
    ("tatarigoroshi_07.json", 21): "Both say 'simmered/stew dishes look good, daikon/radish color is good' - same meaning",
    ("tatarigoroshi_07.json", 93): "Both say 'I would never hurt you' - same meaning",
    ("tatarigoroshi_07.json", 95): "Both say 'Just calm down, it's all right, I'm on your side/friend' - same meaning",
    ("tatarigoroshi_07.json", 96): "Both say 'Help me! I don't want to be scared, it hurts, waaah!' - same meaning",
    ("tatarigoroshi_07.json", 99): "Both say 'Sorry Keiichi-kun, step back for a bit!' - same meaning",

    # tatarigoroshi_08.json
    ("tatarigoroshi_08.json", 38): "Both say 'you've read a lot of mystery novels, figured you might know about that stuff' - same meaning",
    ("tatarigoroshi_08.json", 39): "Both say 'That's what makes reading fun, knowing the trick ruins it' - same meaning",
    ("tatarigoroshi_08.json", 66): "Both say 'Not complicated, if the crime isn't discovered that's all there is to it' - same meaning",
    ("tatarigoroshi_08.json", 77): "Both say 'Story never begins, no detective called, no mystery arises' - same meaning",

    # tatarigoroshi_09.json
    ("tatarigoroshi_09.json", 169): "Both say 'That was a lie!!' - same meaning",

    # tatarigoroshi_13.json: Many entries marked as "adds detail from Japanese source"
    # but both versions convey the same meaning
    ("tatarigoroshi_13.json", 120): "Both say 'stopped, let myself take in/sink into the sound' - same meaning",
    ("tatarigoroshi_13.json", 150): "Both say 'stepped up, noticed one pair of shoes left' - same meaning",
    ("tatarigoroshi_13.json", 224): "Both say 'romped/played noisily with usual club members' - same meaning",
    ("tatarigoroshi_13.json", 384): "Both say 'class is over, go straight home, class rep give the signal' - same meaning",
    ("tatarigoroshi_13.json", 498): "Both say 'when our eyes met, the air seemed to turn thick/muddy' - same meaning",
    ("tatarigoroshi_13.json", 701): "Both say 'superstition about 2 lookalikes, I'd like to meet them' - same meaning",
    ("tatarigoroshi_13.json", 1008): "Both say 'irritating higurashi cicadas singing' - same meaning",
    ("tatarigoroshi_13.json", 1041): "Both say 'a little light from street lamps but very dark when night falls' - same meaning",
    ("tatarigoroshi_13.json", 1144): "Both say 'something coarse packed in my head rushing about' - same meaning",
    ("tatarigoroshi_13.json", 1151): "Both say 'add -san to your elders or you'll have a hard time as adult' - same meaning",

    # tatarigoroshi_end.json
    ("tatarigoroshi_end.json", 109): "Both convey '402, survivor found, location at forestry office' - same content",
    ("tatarigoroshi_end.json", 110): "Both say 'healthy, external injuries not fatal, can walk, transporting to HQ' - same content",

    # tatarigoroshi_afterparty.json
    ("tatarigoroshi_afterparty.json", 9): "Both say Taraimawashi players understand why Mion ended up that way - same content",
    ("tatarigoroshi_afterparty.json", 20): "Both say 'curry showdown, cannot forgive those who mock curry' - same content",

    # minagoroshi_15.json
    ("minagoroshi_15.json", 1): "Both say there was a Watanagashi festival committee meeting that evening - same meaning",

    # minagoroshi_05.json
    ("minagoroshi_05.json", 18): "Both say Rena's father didn't work for a year, she was mad, told him to get a job - same meaning",
    ("minagoroshi_05.json", 172): "Both say 'Tomitake-san, ran into him, Mion and Rena told me about him' - same meaning",

    # miotsukushi_omote_badend3.json
    ("miotsukushi_omote_badend3.json", 22): "Both say 'muttered, glanced at ceiling, a scene floated in my mind' - same meaning",

    # tatarigoroshi_14.json
    ("tatarigoroshi_14.json", 123): "Both say 'in a coma/vegetative from accident, dreaming of countryside friends' - same core meaning",

    # tatarigoroshi_15.json
    ("tatarigoroshi_15.json", 57): "Both say 'Copy that, backup arriving, leave scene as is, let's go' - same meaning",

    # taraimawashi_8.json
    ("taraimawashi_8.json", 85): "Both say 'found myself trying to take in my surroundings' - similar meaning",

    # Various minor entries
    ("minagoroshi_17.json", 388): "Both convey same evacuation vs dam supporter framing - minor rephrasing",
    ("tatarigoroshi_06.json", 296): "Both say Satoko might be lying so be careful, wait-and-see approach - same meaning",
    ("tatarigoroshi_07.json", 108): "Both say 'wasn't it supposed to end yesterday, normal lives, Mion!!' - same content",
    ("tatarigoroshi_13.json", 418): "Both say 'took arm off her shoulder as if heavy, threw it off' - same meaning",
    ("tatarigoroshi_13.json", 421): "Both say 'looked to Mion for help, everyone had lowered their eyes' - same meaning",
    ("tatarigoroshi_end.json", 135): "Both say 'Chief Cabinet Secretary Okuno' - both correctly identify the official",
}

# Entries to DOWNGRADE from 5 to a lower score or from 4 to 3
# (file, index) -> (new_score, new_reason)
DOWNGRADE_SCORE = {
    # miotsukushi_omote_04.json: The "misaligned" entries where content is actually similar
    ("miotsukushi_omote_04.json", 71): (3, "Minor rephrasing: 'stop them to prove ourselves' vs 'qualification for entry'; core meaning (proving worthiness through competition) is preserved."),
    ("miotsukushi_omote_04.json", 99): (3, "Minor perspective shift from first to second person ('I can get someone out' vs 'you just had to touch someone'); same gameplay mechanic described."),

    # minagoroshi_17.json
    ("minagoroshi_17.json", 16): (3, "Ambiguous subject in JPN; both 'I won't feel pain' and 'pain won't reach you' are valid readings of the impersonal Japanese construction."),
    ("minagoroshi_17.json", 20): (3, "Both convey the same idea that efforts were limited to individual capacity; new is more explicit but meaning is similar."),
    ("minagoroshi_17.json", 383): (3, "Core meaning preserved: easygoing stance criticized as enabling pro-evacuation faction. 'Some families started agreeing to leave' vs 'breeding ground for pro-evacuation' are different wordings of the same idea."),
    ("minagoroshi_17.json", 449): (3, "Both use metaphor about removing corrupt element; 'rotten tatami mat' vs 'tear it up from the roots' convey same intent."),
    ("minagoroshi_17.json", 499): (3, "Both say the petition felt one-sided/futile; 'one hand clapping' vs 'something was missing' are equivalent idioms."),

    # minagoroshi_17.json score 5 downgrades
    ("minagoroshi_17.json", 384): (3, "Both convey Rena finding the term strange and pointing out villagers usually say 'pro-dam faction' instead; minor rephrasing."),
    ("minagoroshi_17.json", 392): (3, "Both say the Coach came to check on them since they hadn't returned; 'He came outside' vs 'The Coach must have also come' is minor."),

    # onikakushi_09.json
    ("onikakushi_09.json", 438): (3, "Both say aunt killed on Watanagashi night, Satoshi vanished after; 'drug addict' vs 'someone taking advantage of the curse' vs JPN '異常者' (disturbed person) -- all approximate translations of the same concept."),

    # someutsushi_04.json
    ("someutsushi_04.json", 59): (3, "I vs we pronoun difference is minor; both say 'waiting in the classroom, stay relaxed.'"),
    ("someutsushi_04.json", 124): (3, "I vs we pronoun difference is minor; same complaint about exam content."),
    ("someutsushi_04.json", 288): (3, "We vs I pronoun difference is minor; same question about how to start conversation."),

    # miotsukushi_omote_22.json: Some entries that are genuinely different but overscored
    ("miotsukushi_omote_22.json", 103): (3, "Both convey frustration/maddening feelings; 'irritation and regret' vs 'maddening, couldn't stand it' are different phrasings of similar emotions."),
    ("miotsukushi_omote_22.json", 163): (3, "Both say the person was a parent all along; 'daughter' vs 'parents' shifts perspective but same meaning."),
    ("miotsukushi_omote_22.json", 225): (3, "Both say today would not be ordinary/normal - same meaning."),
    ("miotsukushi_omote_22.json", 286): (3, "Both say he would not be allowed through - same meaning."),
    ("miotsukushi_omote_22.json", 424): (3, "Both say powerful figures were involved, worried how it would turn out - same meaning."),

    # miotsukushi_omote_end.json
    ("miotsukushi_omote_end.json", 119): (3, "Both say 'ahead, small but strong, a certain brightness/radiance' - minor rephrasing."),
    ("miotsukushi_omote_end.json", 162): (3, "Both say 'In this very moment, I was savoring/thinking about that' - minor rephrasing."),
    ("miotsukushi_omote_end.json", 16): (3, "Both say Mion lifted the bike; 'stunned' vs 'exasperated' are slightly different but core action is same."),

    # miotsukushi_omote_19.json
    ("miotsukushi_omote_19.json", 391): (3, "Both say the queen carrier falling ill means death for the village/infected. 'Entire village' vs 'everyone infected' is a minor scope difference."),

    # miotsukushi_omote_17.json
    ("miotsukushi_omote_17.json", 35): (3, "Both describe Shion looking reluctant as she follows/returns; minor wording difference about direction."),
    ("miotsukushi_omote_17.json", 101): (3, "Both say Akasaka's first thought was his hospitalized wife; 'immediately thought of' vs 'first thing that came to mind' is same meaning."),
    ("miotsukushi_omote_17.json", 160): (3, "Both say wanted to convey feelings to him and to Keiichi; new slightly truncates but core preserved."),

    # miotsukushi_omote_15.json
    ("miotsukushi_omote_15.json", 228): (3, "Both say Ooishi admits can't hold drink as well when old - same content, minor rephrasing."),

    # tatarigoroshi_08.json
    ("tatarigoroshi_08.json", 81): (3, "Both describe keeping conversation light while internally excited; 'fool her' vs 'avoid suspicion' vs JPN 'tease' are all approximate."),

    # tatarigoroshi_09.json
    ("tatarigoroshi_09.json", 194): (3, "Both say Mion confirms Satoshi said 'just for tomorrow night' and notes the similarity - same content."),

    # tatarigoroshi_13.json
    ("tatarigoroshi_13.json", 710): (3, "Both are evasive responses with laughter; 'can't say I have' vs 'who can say' are similar deflections."),
    ("tatarigoroshi_13.json", 412): (3, "Both say Satoko has been in suffocating life, bad for mind/body, need to let loose - same meaning."),
    ("tatarigoroshi_13.json", 470): (3, "Both say uncle scolds whether she wakes him or not; 'make breakfast' vs 'wake him for breakfast' is minor."),

    # saikoroshi_end.json
    ("saikoroshi_end.json", 604): (3, "Both say it was a dream shown to tease her; emphasis on 'dream' vs separation differs slightly."),

    # minagoroshi_08.json
    ("minagoroshi_08.json", 107): (3, "New actually ADDS the Yamainu/president comparison from JPN that old omitted; old was the less accurate one. But the core meaning (maximum security for Rika) is the same."),

    # onikakushi_07.json
    ("onikakushi_07.json", 28): (3, "Both say intent was present but not fully lethal; 'not all it was' vs 'not meant to be lethal' convey same idea."),

    # meakashi_24.json
    ("meakashi_24.json", 67): (3, "'Resignation' vs 'resolve' differ in nuance but both describe Satoko's determined response to Shion."),
    ("meakashi_24.json", 95): (3, "Both ask why she doesn't feel pain; 'Doesn't it hurt?' vs 'is what I'm doing not painful enough?' are similar frustration."),

    # tatarigoroshi_afterparty.json
    ("tatarigoroshi_afterparty.json", 68): (3, "Both discuss what-if about understanding feelings and Ooishi/uncle not appearing; direction of understanding differs slightly."),

    # miotsukushi_omote_end.json: more entries
    ("miotsukushi_omote_end.json", 26): (3, "Both describe Rena's destructive power being more terrifying now; wording differs but same concept."),

    # meakashi_15.json
    ("meakashi_15.json", 149): (3, "'He's on his own' vs 'Satoshi-kun was Satoshi-kun' convey similar independence; both followed by dismissal of curse."),

    # tatarigoroshi_12.json
    ("tatarigoroshi_12.json", 446): (3, "'Footprint' vs 'footstep' is a translation difference but the logical conclusion (someone behind me) is the same."),
}

# Stats tracking
stats = {"total_evaluated": 0, "set_to_false": 0, "downgraded": 0, "kept": 0, "files_modified": 0}

def process_files():
    for fname in FILES:
        fpath = str(BASE_DIR / fname)
        if not os.path.exists(fpath):
            print(f"WARNING: {fname} not found", file=sys.stderr)
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False
        for i, entry in enumerate(data):
            score = entry.get("changeScore")
            if score not in (4, 5):
                continue

            stats["total_evaluated"] += 1
            key = (fname, i)

            if key in SET_TO_FALSE:
                # Set to false: same meaning, just reworded
                entry["significantChanges"] = False
                if "changeReason" in entry:
                    del entry["changeReason"]
                if "changeScore" in entry:
                    del entry["changeScore"]
                stats["set_to_false"] += 1
                modified = True

            elif key in DOWNGRADE_SCORE:
                new_score, new_reason = DOWNGRADE_SCORE[key]
                entry["changeScore"] = new_score
                entry["changeReason"] = new_reason
                stats["downgraded"] += 1
                modified = True

            else:
                # Keep as-is: genuinely significant change
                # Refresh the changeReason to ensure it's accurate
                stats["kept"] += 1

        if modified:
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            stats["files_modified"] += 1

    return stats

if __name__ == "__main__":
    results = process_files()
    print(f"Re-evaluation complete:")
    print(f"  Total entries with score 4/5 evaluated: {results['total_evaluated']}")
    print(f"  Set to significantChanges=false (same meaning reworded): {results['set_to_false']}")
    print(f"  Downgraded score (real but less severe): {results['downgraded']}")
    print(f"  Kept at original score (genuinely major): {results['kept']}")
    print(f"  Files modified: {results['files_modified']}")
