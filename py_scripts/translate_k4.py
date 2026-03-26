#!/usr/bin/env python3
"""Add TextENGNew translations to kamikashimashi_4.json"""
import json

translations = {
154575: "\"........From the looks of it, the Sonozaki Group office seems to be keeping things under control......\"",
154576: "Mion and the others had moved building by building, picking up a pair of opera glasses along the way to use as binoculars.",
154577: "After a short surveillance session, they had mapped out what movement was possible between the buildings and tracked the patterns of the surrounding rioters.",
154578: "\"Just like the neighborhood watch back in Hinamizawa.\"",
154579: "\"Usually they huddle behind their barricades looking scared, then the moment they hear something they shout and come stampeding over.\"",
154580: "\"It's rather comical that they think they're behaving rationally......\"",
154581: "\"But now we know their behavior patterns. Including the fact that they were at their most agitated when we first ran into them.\"",
154582: "\"It's not like, they're always running around like that.\"",
154583: "\"Exactly. That alone is valuable information.\"",
154584: "\"Either way, nothing can be done until we cross this main road.\"",
154585: "\"We can't advance any further without crossing it......\"",
154586: "\"So either we go quietly, or we go loudly. Those are our only two options.\"",
154587: "\"Let's use the cover of darkness and slip across.\"",
154588: "\"I'd like to move before your injury gets any worse, Mion. ......Are you still holding up okay?\"",
154589: "\"Heh heh, don't underestimate this old man. A scratch like this is nothing...... Ow, ow, owww?!\"",
154590: "Mion lifts her arm like it's nothing, but there's no way a gunshot wound heals in a day or two.",
154591: "The only thing keeping Mion going is her own formidable physical and mental resilience.",
154592: "The bleeding had stopped thanks to improvised first aid, but it was still the kind of wound that needed a proper doctor.",
154593: "\"Please don't push yourself too hard, okay?\"",
154594: "\"I-I'm fine, I'm fine. A wound this little can't stop Sonozaki blood.\"",
154595: "\"It would be a serious problem if the blood really couldn't stop.\"",
154596: "\"We should be able to get better treatment once we reach the office. So we just have to hold out a bit longer.\"",
154597: "\"So even if it takes time, we make it to that office no matter what.\"",
154598: "\"What about you, Une-chan......?\"",
154599: "\"Are you coming with us? Waiting here for help that may never arrive sounds a little too uncertain.\"",
154600: "\"........................\"",
154601: "\"......Everyone else said the same thing, went out, and got killed. ......I can understand why you'd feel that way.\"",
154602: "\"It's not that, I don't want to leave because I'm afraid.\"",
154603: "\"......Will you trust us?\"",
154604: "\"It's not that I don't. The more I watched you all in action, the feeling that it was more dangerous to stay with you... stopped.\"",
154605: "\"Every one of our club members is at their strongest alone — and together we're invincible!\"",
154606: "\"If you're willing to trust us, we'll protect you no matter what.\"",
154607: "\"That does assume there's some guarantee the Sonozaki Group office is safer than here.\"",
154608: "\"That's no problem. They keep all kinds of emergency supplies stocked there so they can hold out if something happens.\"",
154609: "\"Your family really does have a gift for being prepared.\"",
154610: "\"Heh heh heh. This old man's family policy is to have the fight already won before it starts.\"",
154611: "\"You saved our lives, Une-san. You're our lifesaver. So we'll repay that debt to you.\"",
154612: "\"We'll make sure to bring you somewhere safe.\"",
154613: "\"......It's not like, I'm not happy about that.\"",
154614: "This young girl was caught up alone in an unprecedented disaster. Of course she was anxious.",
154615: "We had initially thought her silent and expressionless, but little by little she was opening up to the high-spirited club members.",
154616: "She was never originally the quiet type.",
154617: "She had merely closed herself off a little to protect her heart from the shock of the disaster.",
154618: "\"Where's your home, Une-chan?\"",
154619: "\"......It's not like, I live in this town.\"",
154620: "\"Huh?! Then where is your home?!\"",
154621: "\"Don't tell me — you got caught up in this while visiting Okinomiya......?\"",
154622: "\"........................\"",
154623: "\"That must have been...... really frightening......\"",
154624: "\"Is it far?\"",
154625: "\"......Not, close. ......But all the bridges are gone and I can't get back......\"",
154626: "\"I see......\"",
154627: "\"You poor thing......\"",
154628: "\"But there's one silver lining.\"",
154629: "\"......Right, I suppose there is.\"",
154630: "\"Une-chan's home and family are outside all of this. So they're safe. Isn't that right?\"",
154631: "\"......... ......That's right.\"",
154632: "As Rena said, that was the one piece of good luck within all the bad.",
154633: "Her home and family were surely safe.",
154634: "The government had destroyed every bridge and tunnel leading into Shishibone City, imposing a physical quarantine.",
154635: "That was as good as admitting it would take no small amount of time to address the situation.",
154636: "But on the other hand, precisely because they had done so, the damage had been contained within the city.",
154637: "Those inside the city were probably despairing or furious, feeling abandoned by the government — but from a broader perspective, it was the right decision.",
154638: "And thanks to it, the place Une needed to return to was safe.",
154639: "......She still had hope.",
154640: "That must have been what allowed her to keep going until today, even as she teetered on the edge of despair.",
154641: "Understanding her circumstances, everyone fell silent for a moment, then closed their fists as a surge of resolve rose within them.",
154642: "\"If you hadn't helped us, who knows what would have happened to us.\"",
154643: "\"There's a good chance some of us wouldn't have made it.\"",
154644: "\"The debt we owe you for saving our lives... is not a small one!\"",
154645: "\"Yeah, that's right, Une-chan. ......All of us club members are going to put everything we've got into getting you home safely!\"",
154646: "\"Th......thank you...... .........so much............\"",
154647: "\"Operation Crossing will commence at 0400 hours! We'll use the cover of darkness to cross the main road in one push and reach the office! I'll take point and scout ahead! I don't want to think about it, but we can't rule out the possibility that the people in the office have also gone over the edge.\"",
154648: "Though she said that to steel us, Mion seemed certain it was not actually the case.",
154649: "She must have confirmed something during her opera-glass surveillance of the office that convinced her everyone inside was still in their right minds.",
154650: "Everyone turned in early to rest and prepare themselves fully.",
154651: "It was a little hard to sleep, lying there terrified of hearing the sound of Satoko's empty-can intruder-detection trap going off.",
}

with open('kamikashimashi_4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for entry in data:
    if entry.get('type') not in ('MSGSET', 'LOGSET'):
        continue
    mid = entry.get('MessageID')
    if 'TextENGNew' in entry:
        continue
    if mid in translations:
        entry['TextENGNew'] = translations[mid]
        count += 1
    else:
        print(f"WARNING: No translation for MessageID {mid}")

with open('kamikashimashi_4.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Verify
with open('kamikashimashi_4.json') as f:
    data2 = json.load(f)
total = sum(1 for e in data2 if e.get('type') in ('MSGSET','LOGSET'))
has_new = sum(1 for e in data2 if e.get('type') in ('MSGSET','LOGSET') and 'TextENGNew' in e)
print(f"Added {count} TextENGNew entries to kamikashimashi_4.json")
print(f"total={total}, has_new={has_new}, needs={total-has_new}")
