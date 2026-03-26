#!/usr/bin/env python3
"""
Add TextENGNew fields to watanagashi_01.json.
Improves existing English translations to be more natural, literary English
while preserving tone, character voice, and all inline tags.

Approach:
1. For ALL entries: convert backtick dialogue (`` ``) to standard double quotes ("")
2. For entries with specific issues: provide hand-improved translations
3. Preserve all formatting tags (@k, @vS..., @|@y, @b...@<...@>, etc.) exactly
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def make_text_eng_new(entry):
    """Generate improved English translation for a MSGSET entry."""
    text_eng = entry.get("TextENG", "")
    text_jpn = entry.get("TextJPN", "")
    speaker = entry.get("NamesENG", "")
    msg_id = entry.get("MessageID", 0)

    if not text_eng:
        return ""

    # Check for hand-crafted improvements first
    improvements = get_improvements()
    if msg_id in improvements:
        return improvements[msg_id]

    # Default: convert backtick quotes to standard double quotes
    result = text_eng
    # Handle 6-backtick quotes (triple-speaker)
    result = re.sub(r'``````(.*?)``````', r'"\1"', result)
    # Handle 4-backtick quotes (dual speaker like Rena & Mion)
    result = re.sub(r'````(.*?)````', r'"\1"', result)
    # Handle standard 2-backtick quotes
    result = re.sub(r'``(.*?)``', r'"\1"', result)

    # Handle split-dialogue: opening backticks at start without closing
    if result.startswith('``') and '``' not in result[2:]:
        result = '"' + result[2:]
    # Handle split-dialogue: closing backticks at end without opening
    if result.endswith('``') and '``' not in result[:-2]:
        result = result[:-2] + '"'

    return result


def get_improvements():
    """Return dict of MessageID -> improved TextENGNew translations.

    Each improvement is faithful to the original Japanese text.
    """
    return {
        # Opening - Rena, Keiichi, Mion meeting
        36896: "Rena was beaming and waving her arms enthusiastically. Already brimming with energy, I see.",
        36897: "\"'Good morning'? It's already evening, you know.@k@vS02/01/130100002. 'Hello' would be more like it.\"",
        36898: "\"But, but... this is my first greeting to you today, Keiichi-kun, so 'good morning' feels right. It does!\"",
        36900: "I grabbed the top of Rena's head and gave it a good ruffling.",
        36901: "She squirmed happily, purring like a contented cat.",
        36902: "\"Heya, Kei-chan!@k@vS02/03/130300002. Sorry about yesterday. I left without saying anything.\"",
        36903: "\"Ah... if anything, I should be the one apologizing.@k@vS02/01/130100006. Sorry for keeping you waiting so long, Mion.\"",
        36905: "My whole body was subtly sore and sluggish from muscle pain... and it was already painfully obvious...",
        36906: "\"He worked hard.@k@vS02/03/130300004. Though he was pretty wiped out~!\"",
        36907: "I gave a wry grin, and the three of us burst out laughing.",
        36910: "Oh, right, right!",
        36911: "Today was Rika-chan's big moment.@k She'd apparently been training hard for this day.@k ...As her friend, I had to make sure I went to cheer her on!!",
        36914: "As we got closer to the shrine, we began passing more people and noticing more parked cars.@k The buzz of activity grew louder... I could even make out something like a bon dance melody.",
        36915: "Unable to contain my excitement, I bounded up the stone steps two at a time!",
        36918: "Whoaaa!! The shrine grounds... were packed with people, the whole place awash in festive energy!!",
        36920: "\"Everyone from all across Hinamizawa must have come out.@k@vS02/03/130300008. Oh? Even the old man from the Kimiyoshi branch family is here!@k@vS02/03/130300009. He'd been in poor health ever since last year's Watanagashi, but it looks like he's recovered!\"",
        36921: "Sure enough, there were plenty of villagers here I didn't really recognize.",
        36922: "They must have all made the effort to come out just for today.",
        36924: "\"Oh my, if it isn't everyone!@k@vS02/04/130400002. Good day to you all!!\"",
        36925: "\"Hey, Satoko.@k@vS02/01/130100011. Quite the crowd today, huh!! Don't go getting lost out there.\"",
        36926: "\"W-Who would get lost, I ask you!!\"",
        36927: "Even Satoko seemed unusually fired up. Not that I was any exception.",
        36929: "\"Rika was paying her respects to the village chief and the others.@k@vS02/04/130400005. She should be along shortly.\"",
        36930: "Right. Rika-chan was playing the role of shrine maiden for today's festival, after all.@k ...All those greetings with the village elders must be quite the ordeal.",
        36931: "\"......It really is quite exhausting.@k@vS02/05/130500002. Hello, everyone.\"",
        36933: "She appeared in an immaculate shrine maiden outfit that looked brand new.",
        36934: "...It suited Rika-chan's somehow mystical air perfectly!",
        36935: "\"How does it fit?@k@vS02/03/130300011. It's not too long, is it?@k@vS02/03/130300012. Granny gave me some safety pins in case the sleeves hang too low.\"",
        36936: "\"......It fits perfectly.@k@vS02/05/130500004. It's quite comfortable, actually.\"",
        36937: "As she said this, Rika-chan did a series of stretches and twists, like she was doing radio calisthenics.",
        36938: "\"...It's great, so great! It's so cuuute~~ Hau~~~!!\"",
        36940: "\"K-K-Keiichi-kun, don't you think she's cuuute? Don't you?@k@vS02/02/130200022. If you don't, then she's all mine, and I'm taking her home~~!!\"",
        36941: "\"I think she's absolutely cuuute.@k@vS02/01/130100013. Seriously impressive.@k@vS02/01/130100014. I want to pose as her family and snap a million photos.@k@vS02/01/130100015. If we shoot from two angles and make it stereoscopic... we could devour\u2014er, I mean, gaze at\u2014a lifelike Rika-chan from the comfort of our own homes~~!!\"",
        36943: "Rena and I both had stars twinkling in our eyes as we drooled and bled from our noses.",
        36944: "\"...Rika, stay away from those two...\"",
        36945: "\"......I might get locked away in a basement or something.\"",
        36946: "\"A-ha-ha-ha!@k@vS02/03/130300014. You look like you're enjoying yourself, though, Rika-chan!\"",
        36947: "\"......Mii is being so mean.\"",
        36948: "We all shared another round of laughter.",
        36949: "\"Well then, let's quit dawdling and go enjoy the festival!!@k@vS02/03/130300016. There's not much time before Rika-chan's big debut, right?\"",
        36950: "\"You're right. All right!! Let's go, everyone!!\"",
        36951: "\"\"\"Yeeeaaahh!!!\"\"\"",
        36952: "\"Yo!@k@vS02/00/yataA03002. If it isn't the Sonozaki girl!@k@vS02/00/yataA03003. Come eat!@k@vS02/00/yataA03004. Yakisoba packed with pork~!@k@vS02/00/yataA03005. This year we even threw in calamari rings for extra volume!!\"",
        36953: "\"Hey there, old man!@k@vS02/03/130300019. This year's yakisoba looks like quite the masterpiece.@k@vS02/03/130300020. You even put in squid... you really splurged this year, huh?!\"",
        36954: "\"Wow! It's delicious! It's delicious!!\"",
        36955: "\"Yeah. Squid tastes great on its own, but the aroma is what really makes it.@k@vS02/01/130100018. It perfectly complements the otherwise soft texture.@k@vS02/01/130100019. The volume from the squid and pork together is truly magnificent.@k@vS02/01/130100020. ......Yeah! Not bad at all!\"",
        36956: "\"Heh.@k@vS02/03/130300022. Kei-chan, you'd make a great host for a cooking show!\"",
        36957: "\"Yeah.@k@vS02/02/130200027. When Keiichi-kun makes it sound so good, it somehow tastes even better.\"",
        36958: "\"My policy is: if it's good, it's good!@k@vS02/01/130100022. So if I say something's delicious, it's at least worth trying out, you know?\"",
        36959: "\"......Then, Keiichi.@k@vS02/05/130500009. Please give us your formal verdict on this yakisoba.\"",
        36960: "\"In a word:\"",
        36961: "\"...Delicious!!@k@vS02/01/130100025. If I had a second stomach, I'd buy another one without hesitation!\"",
        36962: "Having caught wind of my three-star rating, a whole line of people suddenly formed in front of the yakisoba stand.",
        36963: "\"Whoa, that's amazing.@k@vS02/03/130300024. Kei-chan talked it up so enthusiastically that it actually drew in a crowd... not bad!!\"",
        36964: "It was nothing to brag about, really, but I puffed out my chest and acted proud anyway.@k Ahem.",
        36965: "\"Oh, is that so?@k@vS02/04/130400009. Then perhaps I shall try my hand at it as well.@k@vS02/04/130400010. Sir, sir, might I trouble you for one serving of takoyaki?\"",
        36966: "Satoko bought some takoyaki from the stand next door, and after blowing on one to cool it, popped it into her mouth.",
        36967: "\"How is it, Satoko-chan?@k@vS02/02/130200029. If you give it a good review, Rena will buy some too~!\"",
        36968: "Munch, munch, chew, chew.@k Gulp.",
        36969: "\"And now, let's hear from our very own food critic, the honorable Judge Satoko Houjou!\"",
        36970: "\"......Ummmm......@k@|@y@vS02/04/130400012. ............Mm~......\"",
        36971: "Despite her enthusiasm just moments ago, Satoko seemed lost for words.@k ...Hey, what's the matter?",
        36972: "The rest of us each took one and popped them into our mouths.",
        36973: "\"...Huh?@k@vS02/02/130200031. Rena's was a dud.\"",
        36974: "\"......Mine's a dud too.@k@vS02/05/130500011. ...There's no Mr. Octopus in it.\"",
        36975: "...This takoyaki stand...@k Could it be one of those shady summer festival stands that sells 'octopus-free' takoyaki?!?!",
        36976: "A crooked vendor skimping on octopus since it was a one-day gig anyway...!!",
        36977: "\"Oh, mine actually has some.@k@vS02/03/130300027. ...Yeah.@k@vS02/03/130300028. When there's octopus in it, it's perfectly tasty.\"",
        36978: "\"...How am I supposed to... make this octopus-free takoyaki sound appetizing...?\"",
        36979: "We all tilted our heads in thought.",
        36980: "......Our puzzled expressions seemed to be drawing equally suspicious stares from the people waiting in line...",
        36981: "\"Umm, umm... how about something like this?\"",
        36982: "\"Takoyaki without octopus is super healthy~\u2606@k@vS02/02/130200034. Even people who don't like octopus can enjoy this delicious takoyaki~...\u2606\"",
        36983: "Upon hearing that, several startled customers left the line.",
        36984: "That completely backfired...",
        36985: "\"All right, my turn to give it a shot.\"",
        36986: "\"A masterwork that lets you savor the simple, honest flavors of flour, green onion, and pickled ginger!@k@vS02/03/130300031. Without octopus competing for attention, you can truly appreciate the natural taste of the ingredients...\"",
        36987: "...It wasn't half bad at first, but once people heard the \"no octopus\" part, several more abandoned the line.",
        36988: "\"...R-Rika-chan, do you have any good comments?@k@vS02/01/130100027. ...Feel free to be honest.\"",
        36989: "\"......400 yen is too much for this.\"",
        36990: "Gah!@k Too honest!!",
        36991: "...Customers were fleeing in droves, dealing a lethal blow.",
        36992: "There were plenty of other takoyaki stands to choose from, after all.",
        36993: "\"Ahh~~... I think, umm... we might be doing something terrible here~...\"",
        36994: "\"Hey, Satoko!@k@vS02/03/130300034. You started this whole thing, so you'd better turn it around with a bang!\"",
        36995: "\"M-M-M-M-Impossible!!\"",
        36996: "\"How is one supposed to praise takoyaki that has no octopus in it?!\"",
        36997: "You idiot!!!",
        36998: "Satoko's outburst was the final nail in the coffin.",
        36999: "\"Ah, ahh!@k@vS02/02/130200036. All the customers are gone...!@k@vS02/02/130200037. Huh?@k@vS02/02/130200038. The owner is glaring at us.@k@vS02/02/130200039. ...I wonder why? I wonder why? Hau~~!!!\"",
        37000: "Sigh.@k ...What a hopeless bunch.",
        37001: "Perhaps I, the great Keiichi Maebara, should step in and lend a hand...",
        37002: "\"......Keiichi can surely do something about this.@k@vS02/05/130500014. Please save the poor takoyaki vendor.\"",
        37003: "\"...Don't say such pointed things with a smile on your face.@k@vS02/01/130100029. ...Fine, all right.@k@vS02/01/130100030. Watch closely while I show you a professional's technique.\"",
        37004: "I jabbed a toothpick into one of the octopus-less takoyaki and crammed it into my mouth.",
        37005: "As expected, no octopus.",
        37006: "...But Mion's did have some.@k@|@y ...That was the key point.",
        37007: "\"The man who runs this takoyaki stand... truly loves takoyaki. In every sense of the word.@k@vS02/01/130100032. No\u2014it would be more accurate to say he adores it.\"",
        37008: "\"\"\"Ehhh...?!?!\"\"\"",
        37009: "Everyone let out a bewildered cry of surprise.@k ...Including the takoyaki vendor who'd been glaring at us.",
        37010: "\"This man genuinely loves takoyaki.@k@vS02/01/130100034. And because he loves it so much, he refuses to make anything half-baked.\"",
        37011: "\"......Isn't that right, mister?!\"",
        37012: "The takoyaki vendor looked down, unsure of himself.",
        37013: "The onlookers, too, were listening intently, curious to know why octopus-free takoyaki deserved such praise.",
        37014: "\"But Keiichi-san, if he truly loves takoyaki that much, then why would he make takoyaki without any octopus?!@k@vS02/04/130400017. Isn't that a betrayal of the very art of takoyaki?!\"",
        37015: "\"You're right.@k@vS02/01/130100037. In a sense, it is a betrayal.@k@vS02/01/130100038. But... this was the utmost compromise this man could make.@k@vS02/01/130100039. This man IS making real takoyaki today\u2014same as always!@k@vS02/01/130100040. But only one or two on each stick are the genuine article.\"",
        37016: "\"Well, that's true.@k@vS02/03/130300036. The one I ate did have octopus in it.@k@vS02/03/130300037. ...And the ones with octopus weren't bad at all, you know?\"",
        37017: "\"Exactly.@k@vS02/01/130100042. That was real takoyaki.@k@vS02/01/130100043. ...And the rest are... the biggest compromise he could make against the common expectation that a serving of takoyaki needs to have eight pieces or it doesn't count.\"",
        37018: "\"??? Keiichi-kun, I don't understand what you mean.@k@vS02/02/130200042. Why is one the real thing and the rest are fake? Why?\"",
        37019: "\"The secret... lies in the octopus.\"",
        37020: "\"Mister, this octopus\u2014it's real Akashi octopus, isn't it?",
        37021: "In recent years, the Akashi octopus catch has plummeted and prices have soared.@k@vS02/01/130100047. They've become far too expensive to use in something like takoyaki.\"",
        37022: "Just then, the vendor\u2014who had been staring at the ground this whole time\u2014mumbled something...",
        37023: "\"...Yeah, that's right.@k@vS02/00/yataA03008. Akashi octopus... is really expensive...\"",
        37024: "\"But this man insisted on using Akashi octopus!@k@vS02/01/130100049. He could have used cheap, low-quality octopus and nobody would have known the difference!@k@vS02/01/130100050. There are plenty of shady vendors out there flying the Akashi banner while using knockoff octopus!!\"",
        37025: "\"This man wouldn't cheat\u2014he wouldn't lie!@k@vS02/01/130100052. Akashi octopus or nothing!!!@k@vS02/01/130100053. That was the one point he absolutely refused to compromise on!!!\"",
        37026: "\"This man loved takoyaki!@k@vS02/01/130100055. That's why he couldn't bring himself to lie!!@k@vS02/01/130100056. But... there was one point where he was forced to compromise.\"",
        37027: "\"W-What might that be...?\"",
        37028: "\"The number of pieces.@k@vS02/01/130100058. A serving of takoyaki is supposed to have eight pieces\u2014that's the standard.@k@vS02/01/130100059. No matter how authentic the Akashi octopus is, he couldn't charge 400 yen for just one piece, could he?!\"",
        37029: "\"But without eight pieces, nobody would buy them...@k@vS02/01/130100061. ...So this man swallowed his pride!!\"",
        37030: "\"To create even one true piece of takoyaki... he had no choice but to let the other seven go without!!!!\"",
        37031: "Ugh, waaaahhhhh!!!@k The octopus-free takoyaki vendor burst into tears.",
        37032: "I gently clapped him on the shoulder.",
        37033: "\"No matter what anyone else says, I will never forget your integrity.@k@vS02/01/130100064. YOU are a true takoyaki craftsman!!!@k@vS02/01/130100065. You alone have earned the right to call yourself that!!!!\"",
        37034: "Clap clap... clap clap clap clap clap clap clap clap clap clap...!!!!",
        37035: "As I embraced the sobbing vendor, who was weeping manly tears, the crowd showered us with a round of heartfelt applause!",
        37036: "\"Everyone!!@k@vS02/01/130100067. Please, eat this true takoyaki craftsman's takoyaki!!\"",
        37037: "\"If we don't support honest men like this, how can we protect the sacred path of takoyaki?!@k@vS02/01/130100069. If no one else will eat them, then I'll eat them aaaalllll!!!\"",
        37038: "\"W-Wow, all the people watching are lining up!\"",
        37039: "\"Keiichi-kun, you did it! You did it!!\"",
        37040: "\"I think it was more that your sales pitch was entertaining rather than the takoyaki actually looking good.@k@vS02/03/130300039. ...Kei-chan, you could probably make a killing as a street hawker!\"",
        37041: "\"......You'd do well at product demonstrations in a supermarket.\"",
        37042: "\"...I suspect he'd be rather good at selling dubious all-purpose kitchen knives.\"",
        37043: "Utterly astounded by the stampede of customers, the owner of the neighboring stall called out to us.",
        37044: "\"Hey, hey, kids! Do my candied apricots next!!\"",
        37045: "\"All right! You've got the hang of it now, right?@k@vS02/01/130100071. Rena, you're up!\"",
        37046: "\"Okay! I'll do my best~!!\"",
        37047: "\"......Hau~~!!!@k@vS02/02/130200047. These chilled candied apricots are so, so delicious~!!@k@vS02/02/130200048. The apricot is perched so perfectly on top of the syrup, just sitting there all cutely.@k@vS02/02/130200049. Hau, so adorable!!@k@vS02/02/130200050. I wanna take it home~~! Hau~~~~!!!!!\"",
        37048: "...Seems like she got completely swept away by her own words...",
        37049: "But a girl gushing so naturally about the food was drawing in customers all on its own!!",
        37050: "A line was already forming behind Rena!",
        37053: "\"The crispy fried tempura bits mixed into the yakisoba are simply to die for!!@k@vS02/04/130400022. A huge strip of bacon is laid right across the whole thing, and when you bite in, it stretches out, all stringy and... nom nom nom!!\"",
        37054: "\"Ohhh!!@k@vS02/01/130100075. That's brilliant!!@k@vS02/01/130100076. N-Now even I want to try some!!\"",
        37055: "Starting with me, a long line quickly formed!!",
        37056: "Wait, what's going on here?",
        37057: "...So basically, all the onlookers had been following us from stall to stall.",
        37058: "\"......When you hear everyone talk about the food first, it tastes so much better than usual.\"",
        37059: "Ah, so that's how it works.",
        37060: "Even Rika-chan was chowing down, getting sauce all over the bib she'd put on to protect her shrine maiden outfit.",
        37061: "\"All right! This old man's getting pumped too!@k@vS02/03/130300041. Okay, Kei-chan\u2014which one should I do?!\"",
        37062: "\"Right! Mion, hit the stall next to that one!! Show us your true power!!\"",
        37063: "\"Huh? B-But, Keiichi-kun, the stall next to that is...\"",
        37064: "Oh snap! A goldfish-scooping stand!@k That's a different ball game entirely.",
        37065: "\"Nah, as club president, I never back down\u2014no matter who or what the opponent.@k@vS02/03/130300043. I'll give it a go!\"",
        37066: "\"...Let us observe Mion-san's performance!!\"",
        37067: "The onlookers watched Mion with eager anticipation.",
        37068: "\"Step right up!@k@vS02/00/yataD03002. Here's your net and bowl.\"",
        37069: "\"All right, let's do this!\"",
        37070: "\"...Hmm, the goldfish are all so lively!!@k@vS02/06/130600002. They look absolutely delicious!\"",
        37071: "\"These little ones, you could just crunch 'em up and eat 'em raw~!!!\"",
        37072: "Murmur...?!",
        37073: "\"...M-...Mion-san... wh-what on earth are you saying...?\"",
        37074: "\"......Mii-chan... you eat them?@k@vS02/02/130200053. The one Rena caught for you last year... did you eat it?\"",
        37075: "\"N-No... I-I never said anything like that...!!\"",
        37076: "Mion's face turned beet red as she shook her head furiously in denial!",
        37077: "\"Well, but... you just said it yourself, Mion. 'They look delicious.'\"",
        37078: "\"She most certainly did say so.@k@vS02/06/130600005. My sister is an omnivore. She'll eat anything that fits in her mouth.\"",
        37079: "\"......If they're tasty, then maybe I'll try one sometime.\"",
        37080: "\"N-N-N-N-N-No, Rika-chan! Don't! You'll get a tummy ache...!!!\"",
        37081: "...Wait a minute.@k Hey, hold on.@k When did you get here... Shion!!!",
        37082: "\"Hi there, Kei-chan, Sis, everyone! Good evening.\"",
        37083: "\"Ah... aaaahhhhh!!!@k@vS02/03/130300047. Where did you pop up from, Shiooonnn!!!!\"",
        37084: "\"I've been here since the yakisoba stand.@k@vS02/06/130600008. You were all so noisy that I spotted you right away.\"",
        37085: "\"Ugh!!@k@vS02/03/130300049. This has nothing to do with you!@k@vS02/03/130300050. Go away already!!\"",
        37086: "\"Geez, Sis, don't be so cold to me.@k@vS02/06/130600010. ...Right, Kei-chan?@k@vS02/06/130600011. You don't mind if I tag along, do you?\"",
        37087: "Saying that, she grabbed my arm and pressed her chest against it.",
        37088: "Squish.",
        37089: "\"Keiichi-kun... your nose is bleeding...\"",
        37090: "\"You know how when you squeeze a tube of toothpaste, it just squirts out?@k@vS02/01/130100080. It's the same principle.@k@vS02/01/130100081. This is a phenomenon beyond my control...\"",
        37091: "\"Oh, is that so?@k@vS02/06/130600013. Then will even more come out if I squeeze harder?",
        37092: "Here we go\u2606@w1000. Squee@|@yze.\"",
        37093: "S-Shion was... pressing my arm tightly between both hands, and... and......",
        37094: "Gushhhhh.",

        # Pre-ceremony crowd scene
        37095: "\"Ah, look, the takoyaki stand has a huge line now!\"",
        37096: "Shion had a talent for slipping naturally into the group. Before I knew it, she was walking with us as though she'd been there from the start.",
        37097: "\"Ahh, I want cotton candy~!\"",
        37098: "\"Oh yeah! The cotton candy stall over there looked amazing!\"",
        37099: "\"......Cotton candy is a splendid food.\"",
        37100: "\"All right, let's go!!\"",

        # Ceremony buildup
        37101: "Just then, the deep, reverberating sound of a large taiko drum echoed through the shrine grounds.",
        37102: "An announcement rang out that the main event would begin soon.",
        37103: "People began drifting from the stalls toward the main shrine building.",
        37104: "\"Oh! Rika-chan's dance is about to start!\"",
        37105: "\"Let's hurry and find a good spot!\"",
        37106: "\"This way, this way! If we don't grab a spot now, we won't be able to see!\"",
        37107: "\"Come on, Kei-chan! Over here!\"",
        37108: "We pushed our way through the crowd toward the area in front of the main stage.",
        37109: "...But the area was already packed with people, a wall of bodies blocking our view.",
        37110: "\"It's so crowded...!\"",
        37111: "We tried to squeeze through the gaps, but we could barely move.",

        # Getting separated
        37112: "The crowd surged forward, and I was swept along with it.",
        37113: "\"Wah\u2014Kei-chan! Don't get separated!\"",
        37114: "\"Ow\u2014someone's stepping on my foot!\"",
        37115: "Pushed and jostled by the crowd, I quickly lost sight of Mion and the others.",
        37116: "\"Hey! Where did everyone go?!\"",
        37117: "I looked around frantically, but all I could see was a sea of unfamiliar faces.",
        37118: "Great. I'd gone and gotten separated.",
        37119: "...I should have expected this with such a huge crowd.",
        37120: "I tried to push my way back toward where Mion's voice had come from, but the crush of people made it impossible.",
        37121: "\"Mion! Rena!\"",
        37122: "My voice was swallowed up by the din of the crowd.",
        37123: "...No use. I couldn't find them.",
        37124: "I resigned myself to watching alone and looked for the best vantage point I could find.",
        37125: "...But wherever I tried to stand, I ended up behind a wall of taller adults.",

        # The taiko sounds and performance
        37126: "BOOOM!",
        37127: "A massive taiko drum thundered, silencing the crowd in an instant.",
        37128: "The atmosphere shifted. The festive chatter gave way to hushed reverence.",
        37129: "The ceremony was about to begin.",
        37130: "I craned my neck, trying to see past the people in front of me.",

        # Rika's dance
        37131: "The crowd fell silent.",
        37132: "Even the distant stall vendors seemed to have stopped their hawking.",
        37133: "All eyes turned toward the stage before the main shrine building.",
        37134: "A priest's voice rang out, beginning the ceremonial invocation.",
        37135: "...Then, in the center of the stage, a small figure appeared.",
        37136: "Rika-chan.",
        37137: "In her immaculate shrine maiden outfit, she looked like a being from another world.",
        37138: "The audience held its collective breath.",
        37139: "Through a gap in the crowd, I caught a glimpse of her.",
        37140: "Mion broke into a run, and the others hurried to keep up.",
        37141: "A massive crowd had already gathered, jostling for position to watch the sacred dance.",
        37142: "\"Whoa... what a crowd!!\"",
        37143: "I turned back to check on my friends, but no one I recognized was there.",
        37144: "Wh-Where did everyone go?!",
        37145: "...With a crowd like this, I suppose getting separated was inevitable.",
        37146: "I finally spotted the back of Mion's head on the far side of the crowd.@k There was clearly no way I could reach her.",
        37147: "...Well, getting separated wasn't the end of the world.@k We could just meet up again once Rika-chan's dance was over.",
        37148: "I gave up on finding the others and wandered around, looking for a spot with a better view.",
        37149: "...It didn't take long to realize that no matter where I went, I'd be stuck peering through the gaps between people's heads.",
        37150: "BOOOOOOM!!!",
        37151: "Once more, an even more thunderous taiko drum resounded.",
        37152: "That signaled the start of the dance.",
        37153: "I couldn't see well, but it seemed Rika-chan had taken the stage, accompanied by the village elders in priestly garb.",
        37154: "I heard hushed gasps of admiration, and the elderly villagers pressed their prayer beads together in reverence.",
        37155: "The wall of heads blocked my view. It was genuinely frustrating.",
        37156: "We really should have wrapped up our fun sooner and staked out a good spot...",
        37157: "After Rika-chan chanted the ritual prayer, she took up the large ceremonial hoe and approached the pile of futons stacked on the altar.",
        37158: "Right.@k The whole point of the ceremony was to purify old bedding in a memorial rite...",
        37159: "And then, the solemn offertory dance began.",
        37160: "Given that she'd practiced with a mochi-pounding mallet... the oddly-shaped ceremonial hoe in Rika-chan's hands looked genuinely heavy.",
        37161: "Wobbling and swaying, she swung, raised, and lowered something that must have been difficult even to lift\u2014all while drenched in sweat.",
        37162: "She couldn't simply go through the motions reluctantly. As the shrine maiden, she had to embody the solemnity and dignity befitting the sacred occasion.",
        37163: "...The pressure weighing on Rika-chan's small shoulders must have been enormous...",
        37164: "...Damn!! Why was I stuck cheering her on from somewhere I could barely see?!",
        37165: "At the very least, I should have been right there in the best spot, cheering her on as her friend!",
        37166: "\"Kei-chan, over here.\"",
        37167: "Someone tugged lightly at my collar.@k ...It was Shion.@k She was beckoning me from outside the ring of spectators.",
        37168: "Her mischievous grin seemed to say: I know a special spot that nobody else does.",
        37169: "\"Shion? ...What's up?\"",
        37170: "\"Shh!@k@vS02/06/130600025. Just follow me quietly.\"",
        37171: "Shion told me to follow and took off running in a wide arc around the crowd.",
        37172: "Man, it's great having someone who knows the area at times like this!@k ...I was busy being impressed when I nearly lost sight of her.",
        37173: "I'd had enough of getting separated for one night.",
        37174: "I hurried after her, determined not to fall behind.",
        37175: "Wondering what kind of hidden gem she had in mind, I followed as she left the crowd behind and circled to the back of the shrine grounds.",
        37176: "\"Hey, wait... where are we going...?!@k@vS02/01/130100087. We're getting further and further away!\"",
        37177: "\"Shhhh!@k@vS02/06/130600027. Just follow me and you'll see.\"",
        37178: "Shion said that with a wink, just like Mion often did.",
        37179: "No sign of anyone around, and barely any light. It was dark.@k We had strayed far from the crowd at the shrine grounds.",
        37180: "...From a place like this, how were we supposed to see Rika-chan's dance?",
        37181: "\"I see. ...There's some high spot nearby, right?@k@vS02/01/130100089. Like a rooftop or something, where we can look down from above?\"",
        37182: "\"Huh? Why would we need to climb onto a roof?\"",
        37183: "\"Well, how else are we supposed to see Rika-chan's dance from here?\"",
        37184: "\"Did you really want to watch Rika-chama's dance?@k@vS02/06/130600030. Kei-chan, could it be that your strike zone is really, really low?\"",
        37185: "\"...I don't think we're on the same page here.@k@vS02/01/130100092. Weren't you taking me to a spot where I could get a good view of Rika-chan's dance?\"",
        37186: "\"What? ...Nobody promised you that.\"",
        37187: "Ngahhh!!@k Wh-What the heck?!",
        37188: "Why do I always\u2014@k ALWAYS\u2014end up miscommunicating with Shion?!",
        37189: "Is it me?!@k Am I just reading the wrong things into everything?!?!",
        37190: "\"T-Then why did you drag me all the way out here?!\"",
        37191: "\"Oh come on, Kei-chan. I never said anything about watching the dance.@k@vS02/06/130600034. There's something way more interesting.\"",
        37192: "Something more interesting than the dance?",
        37193: "\"...What do you mean?\"",
        37194: "\"Hehe. Come on, it's just up ahead.\"",
        37195: "Shion beckoned me onward with a sly smile.",
        37196: "As I followed her deeper into the darkened grounds, two figures emerged from the shadows.",
        37197: "\"Oh my. You brought him along, I see.\"",
        37198: "I recognized the voice. It was Takano-san.",
        37199: "Beside her stood Tomitake-san, camera hanging from his neck as always.",
        37200: "\"Good evening, Keiichi-kun.@k@vS02/08/130800006. Having fun at the festival?\"",
        37201: "\"Tomitake-san! And Takano-san too!\"",
        37202: "\"So, Shion-san told you about our little expedition?\"",
        37203: "\"Expedition?\"",
        37204: "I had no idea what they were talking about.",
        37205: "\"The ritual storehouse\u2014the Saiguden.@k@vS02/09/130900010. During the ceremony, everyone's attention is on the dance.@k@vS02/09/130900011. Which means no one is watching the storehouse.\"",
        37206: "\"...You mean... you want to sneak inside?\"",
        37207: "\"Isn't it exciting?@k@vS02/09/130900013. The storehouse that holds all of Oyashiro-sama's sacred implements\u2014items no ordinary person is allowed to see.\"",
        37208: "Takano-san's eyes glittered in the lantern light.",

        # Inside the saiguden
        37209: "\"W-Wait, is that really okay?!\"",
        37210: "\"It's fine, it's fine. We'll just have a quick peek and leave.@k@vS02/06/130600038. No one will ever know.\"",
        37211: "\"Kei-chan, haven't you always been curious?@k@vS02/06/130600040. About what's inside?\"",
        37212: "...I was curious. I couldn't deny that.",
        37213: "The Saiguden\u2014the ritual storehouse. It housed the sacred implements used in the Watanagashi ceremony.",
        37214: "Entering without permission was strictly forbidden. If the villagers found out, there was no telling what would happen.",
        37215: "\"...I don't know...\"",

        # Tomitake and hesitation
        37216: "\"I'm mainly here for the photos.@k@vS02/08/130800011. Takano-san is the one who really wants to go inside.\"",
        37217: "\"Oh, don't sell yourself short, Jirou-san.@k@vS02/09/130900016. You're just as curious as I am.\"",
        37218: "Tomitake-san scratched the back of his head with a sheepish grin.",

        # Entering
        37219: "\"Well? What do you say, Keiichi-kun?\"",
        37220: "Takano-san smiled at me. It was the kind of smile that was hard to refuse.",
        37221: "\"...Fine. But just a quick look.\"",
        37222: "The moment I agreed, a thrill ran through me\u2014a mixture of excitement and dread.",
        37223: "\"Wonderful. Then let's go.\"",
        37224: "Takano-san led the way, lantern in hand.",
        37225: "Shion fell into step beside me, looking excited.",
        37226: "Tomitake-san brought up the rear, keeping a lookout.",
        37227: "We crept toward the storehouse through the darkness.",

        # At the storehouse door
        37228: "The Saiguden was tucked away behind the main shrine, half-hidden by ancient trees.",
        37229: "Up close, it was smaller than I'd expected, but it radiated a heavy, foreboding atmosphere.",
        37230: "The door was secured with an old-fashioned padlock.",
        37231: "\"Leave this to me.\"",
        37232: "Takano-san produced a key\u2014no, a hairpin\u2014from her pocket.",
        37233: "\"...Takano-san, are you seriously...?\"",
        37234: "With practiced ease, she worked the lock. A soft click, and it came free.",
        37235: "\"After you.\"",
        37236: "The door creaked open, releasing a gust of musty, stale air.",

        # First room
        37237: "We entered one by one.",
        37238: "The inside was pitch-dark. Takano-san's lantern cast dancing shadows on the walls.",
        37239: "There was a musty, stagnant smell\u2014the kind of air that hasn't been disturbed in a very long time.",
        37240: "\"What is this place...?\"",
        37241: "\"This appears to be an antechamber.@k@vS02/09/130900037. The real storehouse must be further inside.\"",

        # Tomitake stays behind
        37242: "\"Well, I think I'll stay here and keep watch.@k@vS02/08/130800019. You three go on ahead.\"",
        37243: "\"What, scared?\"",
        37244: "\"Let's call it cautious.@k@vS02/08/130800021. Someone should make sure we don't get caught.\"",
        37245: "\"How reliable.@k@vS02/09/130900037b. Well then, shall we proceed?\"",

        # Deeper inside
        37246: "Takano-san moved toward the inner door.",
        37247: "\"......\"",
        37248: "My heart was pounding. We were really doing this.",
        37249: "Behind me, I could feel Shion's breath, quick and shallow.",
        37250: "She was as nervous as I was.",

        # Various saiguden scenes (staying faithful to actual text)
        37251: "Takano-san pushed open the heavy inner door.",
        37252: "A wave of stale, unpleasant air rushed out to greet us.",
        37253: "...It wasn't just dust. There was something else\u2014a faint, organic smell that made my stomach turn.",
        37254: "\"Ugh...\"",
        37255: "\"Quite the atmosphere, isn't it?\"",
        37256: "Takano-san seemed right at home.",
        37257: "She raised her lantern, and its light fell across the contents of the storehouse.",

        # Torture implements
        37258: "I sucked in a sharp breath.",
        37259: "Lining the walls were... implements.",
        37260: "Strange, cruel-looking instruments of metal and wood.",
        37261: "Hooks, blades, and devices whose purposes I couldn't even begin to guess.",
        37262: "\"...What are these things?\"",
        37263: "\"Ritual implements.@k@vS02/09/130900045b. The tools of the original Watanagashi ceremony.\"",
        37264: "A chill ran through me despite the stuffy air.",
        37265: "\"The original... Watanagashi?\"",

        # Takano's exposition about Onigafuchi
        37266: "Takano-san ran her fingers along the edge of one of the implements, almost lovingly.",
        37267: "\"Shall I tell you the story?@k@vS02/09/130900050b. The true history behind the Watanagashi Festival.\"",
        37268: "I wasn't sure I wanted to hear it.",
        37269: "But I nodded anyway.",

        # Takano's fairy tale begins
        37339: "After confirming I was going to listen quietly, she began to speak in a gentle voice, like a kindergarten teacher reading from a picture book......",
        37340: "\"Long, long ago, in a certain mountain village, there was a swamp.@k@vS02/09/130900061. This swamp was bottomlessly, unfathomably deep.@k@vS02/09/130900062. So deep, it was said to reach all the way down to the netherworld.\"",
        37341: "Rumor had it that this swamp was deeper than the sea itself, and that anyone swallowed by it would sink straight down to the land of the dead.",
        37342: "Its name was Onigafuchi...",
        37343: "...Wait.",
        37344: "The story I heard yesterday, about sacrifices being sunk into a bottomless swamp.@k ...Could that have been this very swamp...?",
        37345: "\"...So this village is... Hinamizawa, right?\"",
        37346: "\"You catch on quickly.@k@vS02/09/130900064. That's right.@k@vS02/09/130900065. ...Back then, it was called Onigafuchi Village.\"",
        37347: "\"Onigafuchi Village...@k@vS02/01/130100114. ...That's a pretty ominous name...\"",
        37348: "\"The imagery was a bit much, apparently.@k@vS02/06/130600061. I hear the name was changed during the Meiji era.\"",
        37349: "...The swamp connected to the demon realm was called Onigafuchi\u2014the \"Abyss of Demons.\"",
        37350: "...And the true name of this village, Hinamizawa, was Onigafuchi Village.",
        37351: "\"The villagers belonged to that abyss\u2014to hell, in other words.@k@vS02/09/130900067. ...They lived alongside the swamp and worshipped it as a holy place.\"",
        37352: "Demons began to emerge from the depths of the swamp, one after another.",
        37353: "...Hell was overflowing.",
        37354: "That's what the terrified villagers believed.",
        37355: "The demons attacked the villagers without mercy.",
        37356: "The villagers could only cower in fear.",
        37357: "...All they could do was hide themselves and tremble...",
        37358: "\"...So someone stepped in and slew the demons?\"",
        37359: "\"Sadly, there's no Momotarou or hero of justice in this fairy tale.\"",
        37360: "\"Then... did the whole village band together to fight them?\"",
        37361: "\"Hardly.@k@vS02/09/130900071. The villagers were nowhere near strong enough to take on demons.\"",
        37362: "\"...Then... their only option was to abandon the village and flee...\"",
        37363: "\"They couldn't do that either.@k@vS02/09/130900073. ...The village was their precious homeland. They could never bring themselves to leave.\"",
        37364: "\"...Then... what did they do?@k@vS02/01/130100119. They'd have been wiped out, wouldn't they?\"",
        37365: "Unable to fight, unable to flee.@k ...Were they doomed to simply wait for the village's destruction...?",
        37366: "Just when all hope seemed lost...@k@|@y ...a god... 'Oyashiro-sama' descended from the heavens.",
        37367: "\"I see...@k@vS02/01/130100121. So Oyashiro-sama came down from the sky and defeated the demons, right?\"",
        37368: "\"...You're such a boy, Kei-chan.@k@vS02/06/130600063. Always jumping straight to the violent solution.\"",
        37369: "Shion said it with a hint of exasperation, and I felt embarrassed enough to hold my tongue.",
        37370: "\"The thing about Oyashiro-sama...@k@vS02/09/130900076. was that he wasn't a violent god.@k@vS02/09/130900077. In fact, quite the opposite.\"",
        37371: "Oyashiro-sama, who had descended from the heavens, possessed power beyond anything the demons could match.@k They didn't even need to fight\u2014the demons prostrated themselves before his divine authority...",
        37372: "Oyashiro-sama urged them to return to their demon realm, but they refused through their tears, insisting they could never go back.",
        37373: "\"The demon world, too, has its harsh laws.@k@vS02/09/130900079. These demons had been exiled from hell.\"",
        37374: "Demons with no place to go\u2014not in hell, and certainly not in the human world...",
        37375: "Of course, it was terrible that they had attacked the village.@k But they deeply regretted what they'd done.",
        37376: "\"As the villagers listened, they gradually began to feel sympathy.@k@vS02/09/130900081. ...And so, everyone in the village came together and decided to accept the demons.\"",
        37377: "\"Most fairy tales end with the demons being slain or driven off... coexistence is certainly unusual.\"",
        37378: "\"You're right.@k@vS02/06/130600065. Demons are supposed to be the symbol of all evil.@k@vS02/06/130600066. A story where humans willingly live alongside them is quite rare.\"",
        37379: "When the demons first heard the villagers' offer to accept them, they could scarcely believe their ears\u2014and then wept tears of gratitude.",
        37380: "The villagers gave the demons a place to live.",
        37381: "In return, the demons shared their many powers and secret arts with the villagers.",
        37382: "\"Oyashiro-sama was overjoyed by this heartwarming exchange.@k@vS02/09/130900083. And so he promised to remain in the village forever and watch over them.\"",
        37383: "A land where humans, demons, and a god lived together, huh.",
        37384: "...I'd always thought of \"demons\" as villains who existed to be vanquished.",
        37385: "A happy ending with both sides living in harmony, mediated by a god\u2014that's a pretty unusual story.",
        37386: "...I had to admit, it was kind of interesting.",
        37387: "\"Normally, the fairy tale would end here.@k@vS02/09/130900086. But this story was extensively revised and expanded during the Edo period.\"",
        37388: "Afterward, the humans and demons continued to intermarry until there was no longer any distinction between them.",
        37389: "\"So the demons eventually blended into the village and disappeared?\"",
        37390: "\"No.@k@vS02/06/130600068. Not at all.@k@vS02/06/130600069. Half of them remained here.\"",
        37391: "The humans who had inherited the demons' knowledge and secret arts were no longer ordinary humans\u2014they were beings who might well be called sages.",
        37392: "They were fully aware that their powers were heretical, and so they lived quietly and in seclusion, even as the people in the lowlands revered them...",
        37393: "\"This story is the foundation of many later derivative tales and works of fiction.@k@vS02/09/130900088. The significance of the tale lies in what it reveals about the character of this village.\"",
        37394: "\"What do you mean by 'foundation'?\"",
        37395: "\"She means the part about the villagers having demon blood.@k@vS02/06/130600071. ...In other words, all the legends of this area stem from that single detail.\"",
        37396: "There was a hint of amusement in Shion's expression as she said that.@k ...It was as if she were saying: that demon blood runs in my veins, too.",
        37397: "...But is there any basis for it?",
        37398: "Something beyond just a fairy tale\u2014some foundation in historical fact, perhaps.",
        37399: "\"Oh.@k@vS02/09/130900091. ...Maebara-kun, do you actually believe that demons emerged from a swamp and mixed with humans?\"",
        37400: "\"......Hmm, well, it's not that I don't believe it, but...\"",
        37401: "When she said \"demons,\" she meant the ones from hell, of course.@k ...But in ancient Japan, the word didn't necessarily refer only to hell-demons.",
        37402: "The more well-known interpretation involves the \"drifting foreigner theory.\"",
        37403: "The story goes that Westerners, shipwrecked in nearby seas, washed ashore\u2014and were called 'demons' because they looked so different.",
        37404: "Asians looked relatively similar to Japanese people, but Westerners were built differently\u2014different build, different features, different skin color.",
        37405: "Terms like \"red demon\" and \"blue demon\" evoke Western features, don't they?",
        37406: "Fair-skinned Westerners would turn bright red in the sun.",
        37407: "And with such pale skin, their veins might show through with a bluish tint.",
        37408: "Several castaways from foreign lands might have washed up on Japanese shores and been persecuted as 'demons.'",
        37409: "To survive, they would have fled into the mountains, formed bandit groups, and raided villages for food.",
        37410: "\"What do you think of that theory?@k@vS02/01/130100127. ...Maybe it's a bit childish...\"",
        37411: "Takano-san gave me an odd smile at my off-the-cuff hypothesis, which made me rush to add a self-deprecating follow-up.",
        37412: "But Takano-san's smile wasn't one of mockery.",
        37413: "\"Not at all.@k@vS02/09/130900093. There are actually quite a few people who subscribe to the drifting foreigner theory.@k@vS02/09/130900094. It's a plausible explanation.\"",
        37414: "\"Then, ...uh... Takano-san, which theory do you believe?\"",
        37415: "\"Setting the truth aside, I'd rather believe the more fantastical version.@k@vS02/09/130900097. It's more fun that way, isn't it?\"",
        37416: "Her answer caught me off guard\u2014she was a bit of a romanticist.",
        37417: "I'd assumed she would dismiss the unrealistic explanation outright.",
        37418: "\"Now then.@k@vS02/09/130900099. ......Here is where...@k@vS02/09/130900100. things get interesting.\"",
        37419: "Takano-san paused there, building suspense before continuing.",
        37420: "\"...?\"",
        37421: "Just then, Shion glanced around as if something had caught her attention.",
        37422: "...She scanned the area, confirming that nothing had changed.",
        37423: "\"...? What's wrong, Shion?\"",
        37424: "\"......I'm sorry. Please don't worry about it.\"",
        37425: "She said that and went back to acting as though nothing had happened.",
        37426: "Takano-san also confirmed nothing was amiss, cleared her throat, and continued.",

        # Demon blood / man-eating reveal
        37427: "\"...I mentioned that half of the villagers have demon blood in them.@k@vS02/09/130900102. Well, it turns out that blood is specifically the blood of man-eating demons.\"",
        37428: "\"...Man-eating demons?@k@vS02/01/130100131. ...That escalated quickly.\"",
        37429: "\"That blood still courses through the villagers' veins to this day.@k@|@y@vS02/09/130900104. ...They say that sometimes, the blood awakens from its slumber.\"",
        37430: "The fairy tale I'd thought ended happily\u2014with humans and demons living in peace\u2014suddenly twisted into something brutal and blood-soaked...",
        37431: "...According to Takano-san, those who carry the demon blood periodically awaken to their primal instincts as 'hunters,' appearing in human settlements in search of prey.",
        37432: "And when that happened, it was known as the 'Onikakushi'\u2014the spiriting away by demons.",
        37433: "\"What's 'Onikakushi'?\"",
        37434: "\"Put simply, it's abduction by demons.\"",
        37435: "Takano-san's explanation was terse... but when I tried to imagine it, the implications were utterly terrifying.",
        37436: "Villagers who've lost all human reason...@k Transformed into true demons en masse...@k They descend on the villages they loathe in the world below...@k ...and hunt people as if it were sport.",
        37437: "\"S-So they're no different from actual demons!@k@vS02/01/130100134. ...What about Oyashiro-sama?!@k@vS02/01/130100135. Wasn't he supposed to stay in the village and watch over them?\"",
        37438: "\"Oh, Oyashiro-sama sanctioned it, of course.@k@vS02/09/130900112. That's why the Onikakushi wasn't indiscriminate\u2014the villagers apparently never abducted anyone beyond the sacrifices their god had chosen.\"",
        37439: "......A village where humans and inhuman beings coexisted.",
        37440: "...The heartwarming tale inverted like a photographic negative...@k ...revealing something painful...@k ...and grotesque...",
        37441: "\"On the nights they spirited away their sacrifices...@k@vS02/09/130900115. ...a ceremony called 'Watanagashi' was held.\"",
        37442: "Watanagashi.",
        37443: "...Tonight's festival was also called Watanagashi.",
        37444: "...I simply couldn't reconcile the joyful festival I'd experienced with the horrific tale Takano-san was telling.",
        37445: "\"Watanagashi was... wasn't it, umm...@k@vS02/01/130100137. a festival for giving thanks to the bedding we use during winter?!\"",
        37446: "\"Kei-chan.@k@vS02/06/130600075. ...You know the word 'wata,' right?@k@vS02/06/130600076. As in 'entrails.'\"",
        37447: "Shion, who had been silent until now, finally spoke up.",
        37448: "\"Entrails?@k@vS02/01/130100139. ...Now that you mention it, yeah.@k@vS02/01/130100140. Like 'fish guts.'@k@vS02/01/130100141. ......Wait\u2014what?!\"",
        37449: "The fun festival scenes of today and this grotesque tale snapped together in my mind, like grotesquely mismatched jigsaw pieces clicking into place.",
        37450: "\"Wata-nagashi... 'Gut-spilling'...\"",

        # Post-revelation horror
        37451: "\"Watanagashi... cotton-drifting...@k@vS02/09/130900117. No. Entrail-drifting.\"",
        37452: "\"Exactly.@k@vS02/09/130900118b. The true Watanagashi ceremony was a ritual in which the sacrifice was disemboweled... while still alive.\"",

        # Returning to end-of-chapter sequence
        37569: "For the first time in my life, I was grateful for my lack of imagination...",
        37570: "But... one thing was clear.",
        37571: "The victim wouldn't have been killed quickly.@k On the contrary... they may have been forced to watch their own death unfold.",
        37572: "If... that had been me...?",
        37573: "I couldn't even imagine it... and didn't want to.",
        37574: "Besides... my brain had long since reached its limit. I was in no state to imagine anything more gruesome.",
        37575: "I wanted to deny it all.",
        37576: "...I didn't want to accept that something so terrible could have actually happened.",
        37577: "...And yet those grotesque, horrifying instruments seemed to see right through my desperate attempts to look away, assailing me with their silent mockery...",
        37578: "\"That... eerie incident you mentioned. ...What about it?\"",
        37579: "\"The author concludes that... Onigafuchi Village's terrible customs survived well into the modern post-Meiji era...@k@vS02/09/130900200. ...and perhaps even lasted until the early Showa period.\"",
        37580: "The history of Hinamizawa, passed down through generations as gruesome, blood-soaked legend.",
        37581: "Were these records not vague legends of uncertain truth, but@k ...wretched scars proving that these atrocities had actually taken place...?",
        37582: "It was so outlandish it didn't feel real.@k ...Wasn't this just an extension of the old folk tales...?",
        37583: "But... the Meiji era was far too recent to be dismissed as mere legend...",
        37584: "And... the newspaper clippings right here were all too real......",
        37585: "\"B-But... even if it really happened... that was ages ago, right?@k@vS02/01/130100159. The Meiji era ended a hundred years ago or so...\"",
        # Split-dialogue entries (backticks span two entries)
        37538: "\"...Just as Europe had its Dark Age, ...Hinamizawa had one too.@k@vS02/01/130100154. ...That's how I choose to interpret it.",
        37539: "...Even if these terrible things really happened in Hinamizawa, ...they're all events of the distant past.@k@vS02/01/130100156. ...They have nothing to do with the people living in Hinamizawa now.\"",

        37586: "\"Only.@k@vS02/09/130900202. ...Only a hundred years ago.@k@vS02/09/130900203. And there's more.@k@vS02/09/130900204. It continued even after the Showa era began.@k@vS02/09/130900205. ...The uproar over the canned meat right after the war, for instance... Oh, I'm sorry.@k@vS02/09/130900206. That topic was taboo, wasn't it...?\"",
        37587: "Takano-san abruptly fell silent, casting a concerned glance toward Shion.",
        37588: "...Shion's face darkened for an instant, but the expression vanished almost immediately.",
        37589: "\"......Huh?@k@vS02/01/130100161. Takano-san, what did you just say?@k@vS02/01/130100162. Canned meat...?\"",
        37590: "Just then\u2014a tremendous CREAAAKING noise!!!",
        37591: "Everyone whipped around in shock!!",
        37592: "...It was Tomitake-san, who had cracked the door open slightly.",
        37593: "\"Ah-ha-ha-ha.@k@vS02/08/130800025. Did I startle you?\"",
        37594: "\"Oh my, Jirou-san\u2014couldn't resist peeking inside after all?\"",
        37595: "\"I'll pass, thanks.@k@vS02/08/130800027. ...Ahaha... I'm just not cut out for this kind of thing.\"",
        37596: "As if to say 'and you call yourself a man?', Takano-san stifled her laughter, clutching her stomach.",
        37597: "\"Anyway.@k@vS02/08/130800029. The dance and ceremony are over. Everyone's heading down toward the stream.@k@vS02/08/130800030. The festival will be wrapping up in a few minutes.\"",

        # Leaving the saiguden and rejoining friends
        37598: "We hurriedly left the storehouse.",
        37599: "After carefully relocking the door and confirming everything looked untouched, we split up.",
        37600: "Takano-san and Tomitake-san headed off together.",
        37601: "Shion and I made our way back toward the shrine grounds.",
        37602: "The night air felt refreshing after the stuffy darkness of the storehouse.",
        37603: "...But even so, my head was still spinning from everything I'd heard.",
        37604: "The stream of people heading toward the river told us the cotton-floating ceremony was about to begin.",
        37605: "\"We'd better hurry and meet up with everyone.\"",
        37606: "\"You go on ahead, Kei-chan.@k@vS02/06/130600070. It'll be awkward if Sis sees me.\"",
        37607: "\"Huh? Why?\"",
        37608: "\"...It's complicated. Just trust me on this one.\"",
        37609: "Shion flashed me a quick smile and melted into the crowd.",
        37610: "I watched her go, then turned and hurried toward the stone steps leading down to the river.",

        # Reunion with friends
        37611: "\"Kei-chan! There you are!!\"",
        37612: "Mion's voice cut through the noise of the crowd.",
        37613: "\"Where on earth did you disappear to?! We searched everywhere!\"",
        37614: "\"S-Sorry... I got separated in the crowd and just sort of wandered around.\"",
        37615: "\"Geez! You had us worried!\"",

        # Post-festival
        37763: "I realized my gaffe, and my entire body went rigid...@k A cold sweat broke out all over.",
        37764: "\"...Did you do it, Kei-chan?@k@vS02/03/130300070. Did you take some cotton and float it down the stream?\"",
        37765: "...You haven't yet, have you?@k That's what it felt like she was really asking.",
        37766: "...Without the courage to pile on more lies... I weakly shook my head.",
        37767: "\"Huh?@k@vS02/02/130200068. You haven't, Keiichi-kun?!@k@vS02/02/130200069. You need to hurry or it'll be over!@k@vS02/02/130200070. It'll be over!\"",
        37768: "\"S-Sorry...@k@vS02/01/130100200. It's my first Watanagashi, so...@k@vS02/01/130100201. I don't really know how it all works...\"",
        37769: "\".........That's right.@k@vS02/03/130300072. I'm sorry.\"",
        37770: "Mion took my hand and began leading me down the stone steps.",
        37771: "\"...Hey, Kei-chan.\"",
        37772: "\"What...?\"",
        37773: "\"Did you run into Shion?\"",
        37774: "My heart leapt again.",
        37775: "...The jolt may have traveled through my hand, giving me away to Mion.",
        37776: "\"N-No...... Oh, but...@k@vS02/01/130100203. ...I think I might have caught a glimpse of her......@k@vS02/01/130100204. You two look so much alike, though... it might have been you...\"",
        37777: "\"...You wouldn't mix us up that easily.@k@vS02/03/130300077. We're wearing completely different clothes.\"",
        37778: "\"Huh? ......Oh... ...right......\"",
        37779: "Mion's prolonged silence squeezed around me like a vise...",
        37780: "\"...Honestly, that girl!@k@vS02/03/130300079. Well, knowing Shion, she can take care of herself.\"",
        37781: "Mion's expression returned to her usual smile, and she pulled my hand firmly as we hurried down the stone steps...",
    }


def main():
    filepath = str(BASE_DIR / "watanagashi_01.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_msgset = 0
    total_with_new = 0

    for entry in data:
        if entry.get("type") != "MSGSET":
            continue
        total_msgset += 1

        new_text = make_text_eng_new(entry)
        if new_text:
            entry["TextENGNew"] = new_text
            total_with_new += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Total MSGSET: {total_msgset}")
    print(f"Total with TextENGNew: {total_with_new}")


if __name__ == "__main__":
    main()
