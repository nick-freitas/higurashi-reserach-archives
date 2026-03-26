#!/usr/bin/env python3
"""Apply pre-computed translations to Higurashi onikakushi JSON files."""

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def strip_tags(text):
    """Strip game engine tags, returning clean Japanese for reference."""
    text = re.sub(r'@vS[^\s.]+\.', '', text)
    text = re.sub(r'@w\d+\.', '', text)
    text = re.sub(r'@[kr|]', '', text)
    text = re.sub(r'@b([^.]+)\.\s*@<([^@]+)@>', r'\2', text)
    text = re.sub(r'``', '', text)
    return text.strip()

def apply_translations(filename, translations):
    """Apply translations dict {MessageID: TextENGNew} to a file."""
    filepath = BASE_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    applied = 0
    skipped = 0
    missing = []

    for entry in data:
        if entry.get('type') not in ('MSGSET', 'LOGSET'):
            continue
        if 'TextENGNew' in entry:
            skipped += 1
            continue
        mid = entry['MessageID']
        if mid in translations:
            entry['TextENGNew'] = translations[mid]
            applied += 1
        else:
            missing.append(mid)

    if missing:
        print(f"  WARNING: {len(missing)} entries missing translations in {filename}: {missing[:5]}...")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print(f"  {filename}: applied={applied}, skipped={skipped}, missing={len(missing)}")
    return applied

# =============================================================================
# onikakushi_01.json translations
# =============================================================================
translations_01 = {
31777: "Lost in thought, I had been staring idly at the stream—when I realized I had drifted apart from Rena.",
31778: "I wasn't particularly lonely, though.",
31779: "This place was no longer unfamiliar to me. This was where I lived. My home.",
31780: "Better to wait here than to wander aimlessly and get even more turned around.",
31781: "Someone would surely find me while I lingered in the cool evening air.",
31782: "A familiar voice drifted to my ears. Tomitake-san's.",
31783: "I turned and walked toward it.",
31784: "How did it go, Tomitake-san? Did you get plenty of good shots?",
31785: "Yeah. Thanks to everyone's cooperation!",
31786: "Tomitake-san was with a woman. I felt a small pang of guilt for intruding.",
31787: "And how was it for you, Keiichi-kun? Did you enjoy the festival?",
31788: "From the way she spoke, she seemed to be a local.",
31789: "I really ought to make a proper effort to learn people's faces around here.",
31790: "What was her name again...?",
31791: "That... um... yes, it was fun.",
31792: "My desperate attempt to recall her name must have been written all over my face, because she gave a bright, amused laugh.",
31793: "I heard you only moved here recently. It's hard to believe—you already seem so close with the others.",
31794: "If it looked that way, it was entirely thanks to Rena and Mion and everyone else.",
31795: "Perhaps after joining today's festival, you've come to feel like a proper resident of Hinamizawa?",
31796: "Hmm... I'm not sure, really.",
31797: "My, that's not like you at all.",
31798: "I thought I had already settled into Hinamizawa.",
31799: "But there were still far too many things I didn't know.",
31800: "The faces of the people I kept meeting, for instance. And the things that had happened in the past.",
31801: "...Is that all? You felt like an outsider over something like that?",
31802: "It's not as dramatic as feeling like an outsider. It's just... well, I'm not quite sure how to put it...",
31803: "The major incident involving the dam construction. The fighting that surrounded it.",
31804: "The brutal past event that everyone played dumb about whenever I brought it up.",
31805: "Even if it was all ancient history—as someone who now lived in Hinamizawa, I didn't think it was wrong to want to know about the darker chapters as well as the bright ones.",
31806: "If learning the truth would put your mind at ease, I'll tell you everything I know.",
31807: "Tomitake-san's smile had a warmth to it I hadn't noticed before.",
31808: "But when someone actually said 'ask me anything,' I found it suddenly difficult to gather my thoughts.",
31809: "Even though there was so much I'd wanted to ask.",
31810: "Then... tell me about the dam construction, please. It was a major incident—Hinamizawa was going to be submerged, wasn't it?",
31811: "The dam—the locals would know far more about it than I do. But I'll tell you what I know, if that's enough. It's only what I read in the papers, though.",
31812: "Tomitake-san's gaze went distant as he reached into his memory. Then he began to speak.",
31813: "The decision to build the dam was finalized seven or eight years ago. I heard it was the largest project since Kurobe.",
31814: "Japan had three major priorities at the time.",
31815: "Transforming the nation through improved transportation networks, meeting the surging demand for electricity, and flood control.",
31816: "Dams were in a construction boom—they generated electricity, controlled flooding, and created enormous economic benefits.",
31817: "Enthusiasm for dam construction grew in this region as well, and Hinamizawa was singled out as the site.",
31818: "From what I heard, the reservoir created by the completed dam would have been enormous. The flooding would have swallowed everything from Hinamizawa all the way upstream to Yagouchi.",
31819: "But why go to the trouble of building a dam in an inhabited place like Hinamizawa? Couldn't they have chosen somewhere where nobody lived?",
31820: "Hmm... I'm not entirely sure, but I heard the terrain here was especially suitable for dam construction.",
31821: "Of course, a protest movement arose in Hinamizawa.",
31822: "Rika-chan had used the word 'fought' to describe it. That alone told me the conflict had been fierce.",
31823: "It went to court and was even debated in the National Diet. The Tokyo papers covered it.",
31824: "Mion had mentioned something about that, too.",
31825: "Every resident of Hinamizawa must have united as one to fight.",
31826: "That sense of solidarity here—something that couldn't be captured with a word as simple as 'community'—was surely the product of that battle.",
31827: "And then, one after another, misconduct and corruption came to light. As the situation grew more tangled, the decision was eventually made to halt construction.",
31828: "If I was ever going to ask, now was the moment.",
31829: "It was precisely the sort of gruesome incident that would captivate a boy my age.",
31830: "I felt a flicker of embarrassment at being petty enough to have my curiosity sharpened by Rena and Mion's refusals to talk.",
31831: "Still, since the opportunity had presented itself, I decided to ask. If it laid this odd fascination to rest, so much the better.",
31832: "Um... there was a dismemberment, wasn't there?",
31833: "There was. I happened to be in Hinamizawa at the time, so I remember it well.",
31834: "My tentative question was met with a perfectly nonchalant answer.",
31835: "It was around this time four years ago, if I recall. That was also the day of the Watanagashi.",
31836: "The dam dispute was in its final throes—debate in disarray, scandals erupting one after another.",
31837: "It was the incident that finally put an end to the dam project.",
31838: "A fight broke out among the construction workers, and the victim was killed.",
31839: "Fearing discovery, the six perpetrators divided the body into six parts and each concealed one.",
31840: "In the end, unable to bear the weight of their guilt, five of the six turned themselves in—but the sixth remains at large to this day.",
31841: "The right arm that person hid has never been found.",
31842: "The broad outline matched what I had read in that tabloid I'd picked up earlier.",
31843: "It was certainly a grim incident—but not so terrible that Rena and Mion would need to conceal it from me.",
31844: "They must not have wanted someone who'd just moved here to form a negative impression of Hinamizawa.",
31845: "I felt grateful for friends who cared that much—and more than a little ashamed of my own morbid interest.",
31846: "It was near the tail end of all the dam trouble, you see. So everyone was saying it was Oyashiro-sama's curse.",
31847: "Oyashiro-sama's curse...",
31848: "Oyashiro-sama, if I recalled correctly, was the name of the deity enshrined at the shrine where today's festival was held.",
31849: "I see.",
31850: "Their guardian deity had visited divine punishment on the wicked dam construction for trying to flood Hinamizawa—that was the idea.",
31851: "The younger ones apparently didn't see it that way... but the elderly here never doubted it was Oyashiro-sama's curse.",
31852: "Tomitake-san's companion smiled at this with a playful air.",
31853: "Tomitake-san joined her laughter, and I found myself laughing along.",
31854: "...But what about now, I wonder. There may be quite a few—even among the young.",
31855: "Quite a few... what?",
31856: "Believers. In Oyashiro-sama's curse.",
31857: "Both Tomitake-san and the woman were still smiling—but the warmth had gone out of their eyes.",
31858: "And after that. Every year it happens. Always around this time of year.",
31859: "Happens? What happens?",
31860: "Tomitake-san paused a moment, as if savoring the suspense, then glanced around and lowered his voice.",
31861: "Every year... on the day of the Watanagashi... someone dies.",
31862: "The year after the dismemberment, on the night of the Watanagashi—a man from Hinamizawa who had supported the dam project fell from a cliff overlooking rapids while traveling, and died. His wife's body was never recovered.",
31863: "He had supported the dam even though he lived here. When the accident happened, the elders whispered among themselves that it was Oyashiro-sama's curse.",
31864: "The woman said this with the same playful smile.",
31865: "And the year after that. On the night of the Watanagashi once more. This time, the head priest of the shrine died suddenly from an unexplained cause. His wife drowned herself in the pond that very night.",
31866: "The head priest—you mean the priest from this very shrine, the one where we just had the festival?",
31867: "The woman nodded.",
31868: "The villagers whispered that they had failed to appease Oyashiro-sama's wrath.",
31869: "And the year after that—again on the night of the Watanagashi—a local housewife was found beaten to death.",
31870: "...A housewife?",
31871: "All the people who had died under mysterious circumstances until now had been connected to the dam or to Oyashiro-sama in some way.",
31872: "With that in mind, I couldn't help wondering—could this housewife also have had some connection?",
31873: "Exactly.",
31874: "The woman said it with that playful look—no, it was something closer to cruelty.",
31875: "The victim's household happened to be the family of the younger brother of the dam supporter who fell to his death two years earlier.",
31876: "The younger brother himself is still alive, it seems—but he was greatly disturbed by it all, and moved to a nearby town.",
31877: "For a long moment, I couldn't close my mouth.",
31878: "The battle over the dam construction—with Hinamizawa's very existence at stake—",
31879: "and the brutal murder at the center of it all.",
31880: "That was all I had known, and all I had meant to ask about.",
31881: "But that wasn't the whole story.",
31882: "Homicide. Body disposal. Accidental deaths. Sudden illness. Suicide. A woman beaten to death.",
31883: "I'm a modern person, at my core.",
31884: "I didn't want to believe in curses...",
31885: "But these strange deaths kept occurring every year—always on the day of the Watanagashi—and the victims were always connected to the dam?",
31886: "Taken one by one, it was easy enough to dismiss each as coincidence.",
31887: "But laid side by side like this... it seemed far more unreasonable to insist they were all coincidental.",
31888: "I didn't believe in curses. But one thing was undeniable—there was a will at work, determined that something would happen on the day of the Watanagashi, every single year.",
31889: "The woman seemed to read my thoughts, and gave a quiet chuckle.",
31890: "As if to say: perhaps we frightened him too much after all.",
31891: "Embarrassed at being so easily read, I pressed Tomitake-san to continue—a trace of irritation and impatience in my voice.",
31892: "Then? The following year's Watanagashi—someone died again, right? Who was it this time?",
31893: "Now there's a question... Who do you think, Keiichi-kun?",
31894: "Wh—what!?",
31895: "The smug way he said it rubbed me the wrong way.",
31896: "Don't dodge the question! I'm being completely serious here!",
31897: "Now, now, Keiichi-kun. Calm down.",
31898: "The woman gently soothed me, and I realized I'd been losing my composure.",
31899: "I'm not dodging anything, Keiichi-kun. It's just—the 'following year' you're referring to, the next Watanagashi...",
31900: "Is tonight.",
31901: "When Tomitake-san hesitated to say it, she finished the sentence for him.",
31902: "A cold sweat broke across my skin. An ugly, creeping sensation I couldn't stand.",
31903: "Nobody says it aloud, but they're all thinking the same thing—that something will happen again tonight.",
31904: "Even with the festival as lively as it was!?",
31905: "You know, last year's victim—the housewife—apparently wasn't a believer. She didn't attend the Watanagashi festival.",
31906: "There was a rumor going around—that if you didn't attend this year's festival, you'd incur Oyashiro-sama's wrath. You hadn't heard anything about that, Keiichi-kun?",
31907: "Not a single whisper of it had reached me.",
31908: "Then—then everyone's attendance at the festival was... out of fear of the curse!?",
31909: "That's what I suspect... There were far more people at the Watanagashi than usual.",
31910: "I suppose everyone is just... afraid, when it comes down to it. Of Oyashiro-sama's curse.",
31911: "...",
31912: "I was struck speechless.",
31913: "In this modern age.",
31914: "Where every field of study had made remarkable progress, illuminating what was once unknown and misunderstood.",
31915: "Where black-and-white television had become extinct and rockets had carried humanity to the moon.",
31916: "And yet... in a society this advanced?",
31917: "Apparently many youth groups from nearby towns were invited as ringers to fill the crowd, but given the recent string of incidents, not many accepted. The municipal committee members were complaining about how difficult it was to find participants.",
31918: "The police, for their part, are treating each case as separate and unrelated. But even so, they apparently stationed quite a few plainclothes officers for security tonight.",
31919: "I was beginning to understand, little by little, why Rena and Mion had kept their lips so sealed.",
31920: "If nothing happened tonight, they could keep me in the dark and everything would pass without incident.",
31921: "If nothing happened, all would be well. In that case, the whole thing would have been nothing but baseless worry.",
31922: "I should simply have pretended from the start that I knew nothing. They could have gone on acting as though everything was normal.",
31923: "And then our ordinary days would have returned.",
31924: "Perhaps it was a bit too much for him, after all?",
31925: "The woman ran a hand through her hair with a small sigh.",
31926: "N-No... not at all, I'm fine, really...",
31927: "I was trying to appear nonchalant, but it only made my flustered state more obvious.",
31928: "Watching me, Tomitake-san looked like he was starting to regret having said anything.",
31929: "He let out a breath, then spoke with a forced brightness.",
31930: "Surely you don't actually believe in such a thing as the curse, Keiichi-kun?",
31931: "...Well... I suppose not...",
31932: "If every case were truly unexplained—perpetrators unknown, methods a mystery—then I might concede the possibility of a curse. But that's not the reality. For each incident, the police investigated and uncovered the truth and the perpetrators.",
31933: "Hearing the word 'police' made me feel a great deal better.",
31934: "It was the perfect antidote to the word 'curse.'",
31935: "Take the very first one—the dismemberment. I told you, didn't I? All but one perpetrator were arrested. It's only a matter of time for the last one. The motive turned out to be an argument that escalated while they were drinking. There's nothing supernatural about that.",
31936: "That much was true. If it hadn't happened on the night of the Watanagashi, I wouldn't have associated it with the curse at all.",
31937: "The accidental deaths of the couple who supported the dam—same thing. He was in a position that earned him enemies, so the police investigated thoroughly from that angle. Their conclusion was accident, not foul play.",
31938: "But... that one also happened on the day of the festival, didn't it?",
31939: "Ha ha ha. Think about it, Keiichi-kun. Could someone with as many enemies as he had in Hinamizawa really attend the local festival without trouble?",
31940: "The Watanagashi would have been a particularly uncomfortable time for him to be here. That's probably why he made a point of traveling away from Hinamizawa around this time of year.",
31941: "The explanation wasn't entirely convincing, but I grasped what Tomitake-san was trying to say.",
31942: "So I pressed him earnestly, asking the questions I needed answered to put my mind at ease.",
31943: "Then, Tomitake-san—what about the priest who died after that? Also on the night of the Watanagashi...",
31944: "The priest's death is even easier to account for. The Watanagashi is the biggest annual event for a Shinto priest. He likely collapsed from accumulated exhaustion, compounded by illness. Or perhaps he already had a chronic condition.",
31945: "But in this day and age, with all our advances in medicine, for the cause to remain unknown...",
31946: "It's exaggeration. Rumors feeding rumors. Two incidents in consecutive years—anyone would grow hypersensitive. The sudden death was admittedly unusual, but...",
31947: "An unusual death like that always triggers a police autopsy. And there wasn't enough evidence to open a full investigation, was there? It was ultimately a natural death.",
31948: "The priest's wife committed suicide, didn't she? What about that?",
31949: "As I've already explained—by the third year, the entire village was shaken. People of deep faith were quick to see the curse's hand. The priest's wife was one of them.",
31950: "Apparently a suicide note was found. Something to the effect of 'my death will appease Oyashiro-sama's wrath.'",
31951: "Then—what about the housewife's incident? Again on the day of the Watanagashi!",
31952: "That case was solved and the perpetrator arrested. He was a certain kind of disturbed individual who confessed to recreating the Hinamizawa curse incidents for his own amusement.",
31953: "Then—then—! What about the incident the year after that!? ...Oh, uh...",
31954: "Right. The year after that is this year.",
31955: "Tomitake-san laughed brightly.",
31956: "Nothing will happen. Not this time. The curse never existed to begin with. It was simply a string of coincidences, and those who believed in the curse spread the idea that they were connected.",
31957: "My internal compass was finally finding its bearings again.",
31958: "I felt a little ashamed of how childish I'd been—losing my composure so easily, nearly working myself into a panic.",
31959: "I know very well that Keiichi-kun genuinely loves Hinamizawa. Even if Oyashiro-sama's curse were real, I can't imagine it would touch someone like you.",
31960: "My heart felt lighter.",
31961: "I should probably forget everything I heard tonight, and soon.",
31962: "Tomorrow, I'd face Rena and Mion and the others with the same smile as always.",
31963: "They surely hoped tonight would pass without incident too—so we could all go on as normal tomorrow, with nothing weighing on anyone.",
31964: "Perhaps reading my change in mood, the woman who had been perched on a rock and listening quietly stretched her arms and rose to her feet.",
31965: "Well, then. I ought to be heading back.",
31966: "Oh my—! I suppose I've been talking rather too long as well!",
31967: "The crowd from earlier had thinned considerably. Here and there, a few family groups lingered to enjoy the cool evening.",
31968: "I glanced at my watch. We'd been talking for the better part of an hour.",
31969: "You came with your friends, didn't you, Keiichi-kun? Shouldn't you go find them?",
31970: "...Oh, right! They might all be out looking for me!",
31971: "Hahahaha! Making the girls search for you—that's quite the scoundrel!",
31972: "Goodnight, Keiichi-kun. See you again. And you too, Jirou-san—I'll see you a little later.",
31973: "Tomitake-san seems like quite the scoundrel himself. (So his first name is Jirou...)",
31974: "She brushed off the back of her skirt and disappeared into the shrine grounds, still bustling with people packing up after the festival.",
31975: "Keiichi-kuuun!! I'm so sorry~!!",
31976: "In her place, Rena came running toward me.",
31977: "I could see everyone else behind her.",
31978: "Speak of the devil.",
31979: "My bad, Kei-chan! We got completely caught up talking!",
31980: "I'd been just as caught up in my own conversation and had completely forgotten about them, so we were even.",
31981: "Oh my, Tomitake-san was with you! How perfectly convenient!!",
31982: "We still need to announce the results of today's shooting gallery competition.",
31983: "Oh—th-that's right! So I'm going to end up dead last after all?",
31984: "In the end, after my spectacular victory, Rika-chan had stepped up as the final challenger—but nearly all the targets were gone by then.",
31985: "There were a few remaining, but every last one was tiny and difficult to hit.",
31986: "She aimed carefully and fired all three shots—and missed completely. She was supposed to share last place with Tomitake-san.",
31987: "But then she stood in front of the stall and gave a pitiful little mewing cry, and the owner crumbled on the spot.",
31988: "She received a pack of gum as a consolation prize.",
31989: "The method was audacious, but she magnificently avoided last place.",
31990: "Come to think of it... Rika-chan is quite the schemer, isn't she.",
31991: "I have no idea what Keiichi is talking about.",
31992: "And so! It's decided—dead last goes to Tomitake-san!!!",
31993: "Everyone clapped and cheered excitedly. Tomitake-san smiled an embarrassed, bewildered smile.",
31994: "Now then, Tomitake-san—are you ready? Penalty time!!",
31995: "Huh? Oh... I completely forgot about that!!",
31996: "Too soft, Tomitake-san. This is exactly why you can't afford to lose in our club.",
31997: "Mion pulled a felt-tip marker from her pocket. Oh—it's that, is it.",
31998: "Show a bit of mercy, Mion. At least use a water-based marker. A permanent one is too cruel.",
31999: "Ahaha, it has to be permanent! A water-based one would just wash out in the laundry.",
32000: "W-Wait, what! What is this!? Please go easy on me!",
32001: "We all pinned his arms behind his back as Mion approached, marker in hand.",
32002: "And—squeak, squeak, squeak!",
32003: "But she didn't write on his face. She wrote on the shirt he was wearing.",
32004: "This year's the year you make it big! —Mion",
32005: "Rena took the marker next. Show me your photos next time, okay? ☆ —Rena",
32006: "It was rather endearing, and I couldn't help laughing.",
32007: "Ha, this is less a penalty and more a farewell message.",
32008: "Ho ho ho! I'm not so lenient as the others! Mine is a proper penalty!",
32009: "Ha, you loser! —Satoko",
32010: "Better luck next time. —Rika",
32011: "Here you are, Keiichi-san.",
32012: "I couldn't quite decide what to write—but given what kind of penalty this was, this felt most fitting.",
32013: "Please come back and play with us again. —Keiichi",
32014: "Tomitake-san had been quiet the whole time.",
32015: "At first he'd looked bewildered, but by the end his expression had shifted to something different.",
32016: "Having to go all the way back to Tokyo wearing this—does that count as part of the penalty?",
32017: "Of course! Make sure you wear it all the way home!",
32018: "Ahahaha, you could even wear it next time you come! ...Wouldn't that be nice!",
32019: "He looked deeply moved.",
32020: "Embarrassment mixed with a tangle of other emotions—his face had gone completely red.",
32021: "Understood. I'll wear this the next time I come. I promise.",
32022: "Cheers and applause from everyone.",
32023: "It was the finest parting gift we could have given to a friend we were about to say goodbye to for the night.",
32024: "I noticed the woman who had been with Tomitake-san standing near the shrine grounds.",
32025: "Tomitake-san seemed to notice her too, and understood it was time.",
32026: "Your companion seems to be waiting! Is it almost time? Hmm~?",
32027: "Yeah, seems that way... haha.",
32028: "Tomitake-san walked over to her and appeared to apologize for making her wait.",
32029: "We each called out something to him.",
32030: "Each time we did, he turned around and waved.",
32031: "Little by little, his silhouette dissolved into the darkness of the night and disappeared.",
32032: "A fairly simple goodbye, all told.",
32033: "For everyone else, this wasn't the first time they'd seen him off.",
32034: "They had done this many times before.",
32035: "...He's gone.",
32036: "Well, I suppose we should be heading out too!",
32037: "Rika-chan had to stay behind—apparently the committee members were having a gathering. Satoko stayed with her as her tag-along.",
32038: "I headed home with the usual group.",
32039: "On the walk back, we talked animatedly about the day's exploits.",
32040: "Should have done this, wish we'd done that—all of that.",
32041: "We parted ways with Mion, and then it was just Rena and me.",
32042: "We reached my house and said goodbye to Rena as well.",
32043: "It's pretty late. Will you be alright on your own?",
32044: "Yeah, I'll be perfectly fine! It's close by—I'll run.",
32045: "If you run into any suspicious characters, yell.",
32046: "If I yell... will you come save me? ...Maybe?",
32047: "If I hear you.",
32048: "Oh...! ...O-Okay! I'll yell loud enough for you to hear me!",
32049: "Rena dashed off, swinging her arms with more enthusiasm than could possibly be necessary.",
32050: "She'd be fine. In that state, she was a match for any adult.",
32051: "Rena's cheerful presence faded, and quiet returned.",
32052: "The curse that no one so much as whispered about. The more I'd learned about it tonight, the deeper the unease settled in.",
32053: "The others surely felt it too—they just weren't letting it show.",
32054: "But if nothing happened, it would all turn out to be empty worry.",
32055: "Nothing will happen. Nothing sinister. Nothing at all.",
32056: "What are you doing standing out there, Keiichi? Come inside. You'll catch cold.",
32057: "It was my mom.",
32058: "Did you go, Mom? To the Watanagashi?",
32059: "Your father never woke up, in the end. So I missed it. Disappointing.",
32060: "She stuck out her tongue with a sheepish look.",
}

# =============================================================================
# onikakushi_02.json — we need to read it first for the IDs
# =============================================================================

def main():
    import os

    # Process file 01
    print("Processing onikakushi_01.json...")
    apply_translations("onikakushi_01.json", translations_01)

if __name__ == "__main__":
    main()
