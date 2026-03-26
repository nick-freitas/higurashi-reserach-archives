#!/usr/bin/env python3
"""
Translate miotsukushi_omote_01 through _13 JSON files.
Adds TextENGNew key to each MSGSET/LOGSET entry.
"""
import json
import re
import sys

def strip_game_tags(text):
    """Strip game engine tags from Japanese text for translation reference."""
    out = text
    out = out.replace('@r', '\n')
    out = re.sub(r'@k', '', out)
    out = re.sub(r'@w\d+\.', '', out)
    out = re.sub(r'@vS[^\s@]+', '', out)
    out = re.sub(r'@b[^.@]+\.@<([^@]+)@>', r'\1', out)
    out = re.sub(r'@\|', '', out)
    out = re.sub(r'\s*\.\s*$', '', out)
    return out.strip()

def write_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(data):
            f.write('\t{\n')
            keys = list(entry.keys())
            for j, k in enumerate(keys):
                v = entry[k]
                comma = ',' if j < len(keys)-1 else ''
                if isinstance(v, str):
                    # Use json.dumps for proper escaping
                    f.write(f'\t\t{json.dumps(k)}: {json.dumps(v)}{comma}\n')
                elif isinstance(v, int):
                    f.write(f'\t\t{json.dumps(k)}: {v}{comma}\n')
                else:
                    f.write(f'\t\t{json.dumps(k)}: {json.dumps(v)}{comma}\n')
            if i < len(data)-1:
                f.write('\t},\n')
            else:
                f.write('\t}\n')
        f.write(']\n')

# Translation tables: MessageID -> TextENGNew
# File 01: miotsukushi_omote_01.json
translations_01 = {
121776: "Warm.",
121777: "I wonder why. Simply gazing at her fills me with a gentle, spreading warmth from somewhere deep in my chest.",
121778: "A comfortable feeling.",
121779: "Why is that, I wonder. Even though I cannot reach out and touch her... merely being near her brings a strange, inexplicable peace to my heart.",
121780: "My body drifts and floats beside that child—and so, too, does my heart.",
121781: "She knows nothing.",
121782: "She understands nothing.",
121783: "Out of a mind and memory as blank and white as freshly fallen snow... the child speaks words she has only just learned.",
121784: "But her tongue is too clumsy for them; what reaches me is something so far removed from the words' true meaning as to be unrecognizable.",
121785: "She tries again in a fluster, but the result is the same. And so she falls silent, the faintest shadow of disappointment passing over her face.",
121786: "Seeing that, I draw gently closer and lean my ear toward her lips.",
121787: "I cannot make out what she is trying to tell me. ...Or perhaps there is no meaning in her voice at all.",
121788: "Even so, when I hear it, my heart quickens—a warmth seeps through me from within, spreading to every corner of my body... and I cannot help but feel a deep, aching nostalgia.",
121789: "Yes... it must be something very dear, something very beloved, that I left behind long ago.",
121790: "And as proof of that, without even realizing it, I stretch both hands out toward the source of that voice and call to it with everything in me.",
121791: "I don't want to let go.",
121792: "I want to be with her forever.",
121793: "May this wish somehow reach you, wherever you are.",
121794: "And yet.",
121795: "...Who could have foreseen that that longing would become the beginning of a long, heavy, and painful journey for that child?",
121796: "Not even a god could have.",
121797: "Because I—",
121798: "\"...Mmm...\"",
121799: "When I opened my eyes, I found myself lying in a futon.",
121800: "The faint warmth of sunlight shimmered hazily beyond the window.",
121801: "\"...Haah... aah...\"",
121802: "...Morning already.",
121803: "The distant chatter of birds drifted in faintly from outside the window.",
121804: "Mingled among them, the cicadas' voices rang like the patter of passing rain.",
121805: "\"...?\"",
121806: "The comforter felt strangely heavy. A very large futon, at that... Did I have something like this?",
121807: "No—that wasn't it.",
121808: "The ceiling was high. No water stains from rain, either; the wood grain traced its rippled patterns clear and distinct.",
121809: "An unfamiliar room. —No, that wasn't quite right. This ceiling did still live somewhere in the margins of my memory. I had simply forgotten, for it had been so long since I last saw it. ...Or rather, it was taking time to surface.",
121810: "...Come to think of it—when was it that I used to find that pattern unsettling?",
121811: "As my consciousness gradually settled into itself, from somewhere came the faint scent of incense.",
121812: "...That, too, felt strangely familiar.",
121813: "\"Haah...\"",
121814: "Still half-drowsed with sleep, I lifted myself from the futon. A white towel fell away before my eyes, and all at once my forehead blazed with heat.",
121815: "A heavy, dull ache. A numb, leaden weariness spread from the nape of my neck to the back of my head.",
121816: "I picked up the towel where it had draped itself over the comforter. ...It was cold. That coldness was what finally made me understand why I had been sleeping here.",
121817: "\"Right, this place...\"",
121818: "My home.",
121819: "The Furude home—which I had not returned to in so long, not since I began living together with Satoko.",
121820: "And this had been my room.",
121821: "Somehow... I knew. This must be the world inside a dream—the world that appears when the gears of time are wound back...",
121822: "\"...How nostalgic.\"",
121823: "It was rare for me to fall into this kind of sentimentality. After living through so long a span, and dreaming so many dreams... how long had it been since I last thought about this room?",
121824: "That desk.",
121825: "That clock.",
121826: "The clumsy portrait of my mother I worked so hard to draw back in the little ones' class.",
121827: "I had passed them every day and never given them a thought, but now... they were all so dear to me. The strange sensation rising slowly from within my chest was not unpleasant in the least.",
121828: "\"—Oh.\"",
121829: "Something at the edge of my vision caught my attention, and I crawled out from the futon.",
121830: "A wave of dizziness washed over me as I stood, and my feet were unsteady as I crossed toward it... but I reached down and picked it up.",
121831: "\"Long time no see... have you been well?\"",
121832: "I cradled it gently and pressed a soft kiss to the tip of its nose.",
121833: "It was nothing remarkable—only a stuffed bear. But it was precious to me, for my mother had given it to me. After my mother disappeared, it had vanished as well, for reasons I never understood.",
121834: "When I spotted a bear displayed as a shooting-gallery prize at a festival stall, I had for just a moment almost believed it had come back to me. ...Of course that was impossible.",
121835: "\"That's right...\"",
121836: "Something clicked into place, and I turned my ear toward the sounds drifting through the shoji from the kitchen.",
121837: "A tidy, rhythmic sound—a knife working its way through vegetables.",
121838: "Beneath it, I could faintly hear something simmering in a pot... rice porridge, most likely, being made for me.",
121839: "And there—cast faintly in silhouette against the shoji, half-lit by the light behind it—was a figure's back...",
121840: "\"...Mom...\"",
121841: "Even just a shadow... there was no way I could mistake it.",
121842: "\"...\"",
121843: "My chest drew tight with a sweet, unbearable ache.",
121844: "Nostalgia and something fierce and burning overflowed without end, and the back of my throat... trembled.",
121845: "That figure I had been trying to forget.",
121846: "Someone whose memory was painful to return to—who had filled me with sadness and anger... and whom I had loved so dearly.",
121847: "All of that was there, just beyond this shoji.",
121848: "\"...Ah...\"",
121849: "I wanted to open this door.",
121850: "I wanted to fling it open and throw myself upon her back.",
121851: "I wanted to see her face turn—startled, then gently reproving—and look back at me with a soft smile, close enough to touch.",
121852: "...And yet.",
121853: "I couldn't.",
121854: "If I opened the shoji, this dream would surely end.",
121855: "...No, that wasn't it.",
121856: "Perhaps my mother would no longer smile for me. That fear and dread rooted my feet and would not let me move.",
121857: "\"The reincarnation of Oyashiro-sama.\"",
121858: "As the villagers celebrated me and the village elders came to revere and fear me—the distance between my mother and me had grown, and grown, and grown.",
121859: "\"...\"",
121860: "I only wanted to be accepted.",
121861: "By my mother, more than anyone.",
121862: "To have her understand about my friend who was always beside me—\"Hanyuu\"—",
121863: "That the reason I was better at cooking than anyone was because of her.",
121864: "That the reason I could know what would happen next was because of her.",
121865: "...I had no wish to show off or make a display of being special.",
121866: "It was my friend who had shown me all of that.",
121867: "The reason I could do things no one had taught me—not my mother, not anyone—was that she truly was beside me.",
121868: "And so.",
121869: "At every opportunity I boasted, wanting her to believe what I was saying... but my mother was not pleased.",
121870: "On the contrary—it had unnerved her, and made her distrust me.",
121871: "\"...\"",
121872: "At first I was sad. So I tried my hardest to make her understand.",
121873: "But when I realized it was no use, I grew angry.",
121874: "Why.",
121875: "Why.",
121876: "You are my parent. My mother.",
121877: "...I had believed you were the one person who had to understand me, even if no one else in the world did.",
121878: "No matter how unbelievable it sounded, you were supposed to know it was not a lie, and offer me the comfort of being believed.",
121879: "...And yet... you...",
121880: "\"...What a fool... it wasn't like that at all...\"",
121881: "Looking back at that past self, I felt a sadness that was almost funny.",
121882: "No—it was not only my mother's fault. For all that her words were harsh and her assumptions unyielding, there was a self-righteous edge to her, but she worried about me in her own way, and she tried her hardest.",
121883: "If I had simply said nothing to begin with, it could have ended there. If I had accepted things as natural, rejoiced in the way a child my age would, thrown my tantrums... surely my mother would have been as tender with me as she was in those earliest days.",
121884: "Even Hanyuu—if I had taken my time and explained her slowly, carefully... I can believe now that my mother, given enough time, would surely have come to understand.",
121885: "And yet.",
121886: "It was I who failed to do that. It was none other than I who gave up on my own.",
121887: "I sulked, I turned cold... and on the other hand, I looked down on her and made a show of myself.",
121888: "—What feelings that must have stirred in her... by the time I thought of it, it was already too late.",
121889: "Even with Hanyuu's power, I could not return to a time far enough back to do it over.",
121890: "Lonely.",
121891: "Even now... it is just so terribly lonely.",
121892: "\"...\"",
121893: "But...",
121894: "\"...Mom...\"",
121895: "Even so...",
121896: "\"Mom—!\"",
121897: "Even just one word of apology would be enough. I had to tell her—I had to, no matter what.",
121898: "I'm sorry for being glad when it rained.",
121899: "I'm sorry for not appreciating the lunches you made.",
121900: "I'm sorry for not returning your love.",
121901: "And—and—",
121902: "\"Mom... I'm... s... sor... ry...\"",
121903: "With that feeling pressing up through me, I... slid the shoji open—",
121904: "\"...\"",
121905: "I woke.",
121906: "Somewhere in the distance, a cricket was singing.",
121907: "\"...\"",
121908: "This was the outbuilding of the Kimiyoshi house—the place I had long since come to call home.",
121909: "\"...Mmn... mmph...\"",
121910: "In the futon laid out right beside mine, Satoko's profile was peaceful with sleep.",
121911: "Through the window, the bright disc of the moon cast its pale, diffuse light over the darkened room.",
121912: "\"...Oh, that's right...\"",
121913: "I dragged myself up from sleep-dulled consciousness and noisy, tangled memory. ...I remembered: I had rewound time, and had returned once more to that moment.",
121914: "Yes... the tragedy that would visit Hinamizawa.",
121915: "The happy, lively, quietly fulfilled and unremarkable days I had spent with my friends leading up to it—repeated over and over.",
121916: "And there was one thing that had been different this time...",
121917: "\"—Miyo Takano...\"",
121918: "This time alone, I had remembered clearly.",
121919: "The true culprit who had slashed open my belly and killed me.",
121920: "She had exploited \"the curse of Oyashiro-sama\" to trample upon the hopes and efforts of my friends... scheming to fulfill her wretched plan within this small and sealed world. Our enemy.",
121921: "For a time, I had even relied on her, just a little.",
121922: "I had thought she was a kind person who cared about Satoko and me.",
121923: "But—",
121924: "\"—!\"",
121925: "But all of that... I would forget.",
121926: "As long as that woman existed, I... and we could never be happy.",
121927: "This time... this time, I would stop her, without fail.",
121928: "This mad repetition of the world...",
121929: "\"Hah...\"",
121930: "My head had finally cooled.",
121931: "It had been a very long time since I had let myself feel so emotional.",
121932: "I suppose it was because last time... I had witnessed what happened to Keiichi and the others.",
121933: "\"—Right.\"",
121934: "I raised myself from the futon and called out to the companion who was always at my side.",
121935: "\"...Hanyuu, what time is it now? What year of Showa, and what month and day?\"",
121936: "The question I asked first, every single time.",
121937: "How much time remained before the day of fate that had claimed me, without fail, through every world until now.",
121938: "That span had been growing steadily shorter; by now there was precious little time left to spend on preparations.",
121939: "But... this time was a little different.",
121940: "I knew who was an ally—and who was an enemy.",
121941: "That alone was a precious, precious factor I had never once had in any of the worlds before.",
121942: "I did not yet know how to fight.",
121943: "Whether I could win—whether I could escape the shackles of this fate—I still did not know.",
121944: "\"...Even so.\"",
121945: "Even so, I felt as though I could see the faintest glimmer of light.",
121946: "It was the light at the end of a long, long, pitch-dark tunnel—so small it seemed on the verge of being swallowed by the surrounding darkness... and yet so strong.",
121947: "So I could still fight.",
121948: "I could step forward on the feet I had risen to, and gather my strength into the fist I had raised.",
121949: "And for that—how much time did I have left?",
121950: "\"...Hanyuu?\"",
121951: "Something was wrong.",
121952: "No voice. No sound.",
121953: "No—more than that... no presence at all.",
121954: "She was always chattering away at me so relentlessly that she sometimes made me uncomfortable.",
121955: "\"Hanyuu? What's wrong, Hanyuu?\"",
121956: "............\n............\n............\n...Something is strange.",
121957: "\"Hanyuu...?\"",
121958: "This had never happened before.",
121959: "\"Hanyuu?\"",
121960: "Hanyuu was not answering.",
121961: "\"Hanyuu?!\"",
121962: "Hanyuu... wasn't there?!",
121963: "\"Hanyuu—?!\"",
121964: "\"...Nngh, what's wrong, Rika...?\"",
121965: "\"I... meep. It's nothing.\"",
121966: "I forced out a laugh with my usual speech habits, awkward as it was. ...This was bad. I was so shaken that I couldn't manage the switch.",
121967: "I had shouted without thinking... forgetting that Satoko was sleeping right beside me.",
121968: "\"Making strange noises in the middle of the night... Are you feeling all right?\"",
121969: "\"M... meep. It's nothing.\nI think I must have had a bad dream.\"",
121970: "I forced out a laugh with my usual speech habits, awkward as it was. ...This was bad. I was so shaken that I couldn't manage the switch.",
121971: "\"Is that so... haah...\nThen go back to sleep...\"",
121972: "\"...Mii... that's what I'll do.\nGood night, Satoko.\"",
121973: "\"Good night...\"",
121974: "With that, Satoko—who must have been half-asleep already—closed her eyes, and before long her quiet breathing resumed. Once I was certain of that, I slipped from my bed and stepped outside.",
121975: "\"Hanyuu? Can't you hear me, Hanyuu? Answer me!\"",
121976: "I called desperately into the empty air.",
121977: "She should have been here. She was always here.",
121978: "Wherever I went, whatever I did, whatever I thought... she always knew it immediately.",
121979: "And yet this time—why?!",
121980: "\"...Hanyuu...\"",
121981: "I stood there in a daze, staring up at the sky.",
121982: "The moon hung above the night sky, casting its light down over me where I stood in the dark.",
121983: "\"...\"",
121984: "The cold of my sleep-dampened skin sent a shiver through me—a trembling as if even my blood might freeze.",
121985: "A world in which, at last, hope had seemed to glimmer.",
121986: "The enemy was visible. So was her purpose. ...The outcome remained uncertain.",
121987: "And I had finally been able to believe in how extraordinary my friends truly were.",
121988: "I was not alone.",
121989: "Rena was there. Mion and Shion were there. Satoko was there. ...And Keiichi was there.",
121990: "If we united our strength—this time, finally, I had believed I was allowed to hope. A last chance, perhaps the very last.",
121991: "And yet... and yet...",
121992: "\"...Hanyuu—!\"",
121993: "Struck dumb with the weight of what it meant... I crumpled where I stood, sinking to my knees.",
121994: "The one who had been the least reliable... and yet the one who had given my heart the most peace...",
121995: "Was nowhere to be found in this world.",
}

# File 02
def get_file02_data():
    with open('miotsukushi_omote_02.json') as f:
        return json.load(f)

def get_file_data(n):
    with open(f'miotsukushi_omote_{n:02d}.json') as f:
        return json.load(f)

def apply_translations(data, trans_dict):
    count = 0
    for entry in data:
        if entry.get('type') in ('MSGSET', 'LOGSET'):
            mid = entry.get('MessageID')
            if mid and mid in trans_dict and 'TextENGNew' not in entry:
                entry['TextENGNew'] = trans_dict[mid]
                count += 1
    return count

def save_file(n, data):
    fname = f'miotsukushi_omote_{n:02d}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, entry in enumerate(data):
            f.write('\t{\n')
            keys = list(entry.keys())
            for j, k in enumerate(keys):
                v = entry[k]
                comma = ',' if j < len(keys)-1 else ''
                if isinstance(v, int):
                    f.write(f'\t\t{json.dumps(k)}: {v}{comma}\n')
                else:
                    f.write(f'\t\t{json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}\n')
            if i < len(data)-1:
                f.write('\t},\n')
            else:
                f.write('\t}\n')
        f.write(']\n')

if __name__ == '__main__':
    file_n = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    if file_n == 1:
        data = get_file_data(1)
        n = apply_translations(data, translations_01)
        save_file(1, data)
        print(f"File 01: {n} entries translated")
    else:
        print(f"File {file_n}: not yet implemented")
