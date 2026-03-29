from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import (
    ArticleEntry,
    AuditLog,
    ClassicalAuthor,
    ClassicalWork,
    DictionaryEntry,
    EngagementKPI,
    IdiomEntry,
    PoetryNode,
    PoetryTypeRegistry,
    User,
    UserInteraction,
    WorkChapter,
)
from app.db.session import SessionLocal, engine


RANDOM_SEED = 20260329
MIN_DICTIONARY_ENTRIES = 600
IDIOM_COUNT = 110
ARTICLE_COUNT = 5
INTERACTION_TARGET = 9000
AUDIT_LOG_TARGET = 2500


AUTHORS = [
    "Malik Muhammad Jayasi",
    "Goswami Tulsidas",
    "Mulla Daud",
    "Qutban",
    "Manjhan",
    "Usman",
    "Sheikh Nabi",
    "Qasim Shah",
    "Nur Muhammad",
    "Baba Raghunath Das",
    "Lal Das",
    "Sabal Singh Chauhan",
    "Ramai Kaka",
    "Balbhadra Prasad Dixit 'Padis'",
    "Rafiq Sadani",
    "Bansidhar Shukla",
    "Pandit Dwarika Prasad Mishra",
    "Trilochan Shastri",
    "Jumai Khan Azad",
    "Vikal Gondaivi",
    "Shiv Saran 'Almast'",
    "Ram Naresh Tripathi",
    "Jagdish Piyush",
    "Dr. Vidya Vindu Singh",
    "Krishnanand 'Krishn'",
    "Guru Prasad Singh 'Mrigesh'",
    "Vikramaditya Singh",
    "Manohar Lal Shukla",
    "Brajendra Awasthi",
    "Ashrafi Lal Misra",
    "Ramvallabh Mishra",
    "Shivakant Mishra 'Vidrohi'",
    "Saraswati Prasad 'Saras'",
    "Rajendra Singh 'Raj'",
    "Kamal Piyush",
    "Ram Kishore Tiwari",
    "Girija Shankar Shukla",
    "Parameshwar Dutt Shukl",
    "Dr. Ram Bahadur Mishra",
    "Ramkrishna Tripathi",
]


POETRY_TYPES = [
    ("doha", "Doha", "classical-couplet"),
    ("chaupai", "Chaupai", "classical-quatrain"),
    ("sorath", "Sorath", "classical-metre"),
    ("ghanakshari", "Ghanakshari", "lyrical-metre"),
    ("chappay", "Chappay", "lyrical-metre"),
    ("jhulana", "Jhulana", "folk-lyrical"),
    ("savaiya", "Savaiya", "court-metre"),
    ("other_poetry", "Other Poetry", "mixed"),
]


HANUMAN_CHALISA_NODES = [
    {
        "poetry_type": "doha",
        "main_text": "श्रीगुरु चरन सरोज रज निज मनु मुकुरु सुधारि\nबरनउं रघुबर बिमल जसु जो दायकु फल चारि",
        "text_romanized": "shri guru charan saroj raj nij manu mukuru sudhari / baranau raghubar bimal jasu jo dayaku phal chari",
        "meaning": "गुरुचरणों की वंदना के साथ मन को निर्मल कर राम के यश का स्मरण।",
    },
    {
        "poetry_type": "doha",
        "main_text": "बुद्धिहीन तनु जानिके सुमिरौं पवन कुमार\nबल बुद्धि विद्या देहु मोहिं हरहु कलेस बिकार",
        "text_romanized": "buddhihin tanu janike sumirau pavan kumar / bal buddhi vidya dehu mohi harahu kalesh bikar",
        "meaning": "हनुमान से बल, बुद्धि, विद्या और क्लेश-निवारण की प्रार्थना।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जय हनुमान ज्ञान गुन सागर\nजय कपीस तिहुँ लोक उजागर",
        "text_romanized": "jai hanuman gyan gun sagar / jai kapis tihun lok ujagar",
        "meaning": "हनुमान को ज्ञान-गुण-सागर और त्रिलोक-प्रकाशक कहा गया है।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "राम दूत अतुलित बल धामा\nअंजनि पुत्र पवनसुत नामा",
        "text_romanized": "ram dut atulit bal dhama / anjani putra pavansut nama",
        "meaning": "हनुमान की दूत-भूमिका और दैवी बल का वर्णन।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "महाबीर बिक्रम बजरंगी\nकुमति निवार सुमति के संगी",
        "text_romanized": "mahabir bikram bajrangi / kumati nivar sumati ke sangi",
        "meaning": "हनुमान दुष्बुद्धि हरते और सद्बुद्धि के साथी हैं।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "कंचन बरन बिराज सुबेसा\nकानन कुंडल कुंचित केसा",
        "text_romanized": "kanchan baran बिराज subesa / kanan kundal kunchit kesa",
        "meaning": "हनुमान के तेजस्वी रूप और आभूषणों का चित्रण।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "हाथ बज्र औ ध्वजा बिराजै\nकांधे मूँज जनेऊ साजै",
        "text_romanized": "hath bajra au dhvaja बिराजै / kandhe moonj janeu sajai",
        "meaning": "वज्र, ध्वजा और यज्ञोपवीत सहित वीर छवि।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "शंकर सुवन केसरी नंदन\nतेज प्रताप महा जग वंदन",
        "text_romanized": "shankar suvan kesari nandan / tej pratap maha jag vandan",
        "meaning": "हनुमान की दिव्यता और विश्वव्यापी वंदना।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "विद्यावान गुनी अति चातुर\nराम काज करिबे को आतुर",
        "text_romanized": "vidyavan guni ati chatur / ram kaj karibe ko atur",
        "meaning": "ज्ञान, गुण और रामकार्य के प्रति तत्परता।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "प्रभु चरित्र सुनिबे को रसिया\nराम लखन सीता मन बसिया",
        "text_romanized": "prabhu charitra sunibe ko rasiya / ram lakhan sita man basiya",
        "meaning": "रामचरित-प्रेम और राम-सीता-लखन का अंतःस्थ निवास।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "सूक्ष्म रूप धरि सियहिं दिखावा\nबिकट रूप धरि लंक जरावा",
        "text_romanized": "sukshma roop dhari siyahi dikhava / bikat roop dhari lank jarava",
        "meaning": "सीता-साक्षात्कार और लंका-दहन की लीला।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "भीम रूप धरि असुर संहारे\nरामचंद्र के काज संवारे",
        "text_romanized": "bhim roop dhari asur sanhare / ramchandra ke kaj sanvare",
        "meaning": "असुर-विनाश और रामकार्य-सिद्धि।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "लाय सजीवन लखन जियाए\nश्रीरघुबीर हरषि उर लाए",
        "text_romanized": "lay sanjivan lakhan jiyaye / shriraghubir harashi ur laye",
        "meaning": "संजीवनी लाकर लक्ष्मण को जीवित करना।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "रघुपति कीन्ही बहुत बड़ाई\nतुम मम प्रिय भरतहि सम भाई",
        "text_romanized": "raghupati kinhi bahut badai / tum mam priya bharatahi sam bhai",
        "meaning": "राम द्वारा हनुमान की अतिशय प्रशंसा।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "सहस बदन तुम्हरो जस गावैं\nअस कहि श्रीपति कंठ लगावैं",
        "text_romanized": "sahas badan tumharo jas gavai / as kahi shripati kanth lagavai",
        "meaning": "अनंत मुख भी यश का पूरा वर्णन नहीं कर सकते।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "सनकादिक ब्रह्मादि मुनीसा\nनारद सारद सहित अहीसा",
        "text_romanized": "sanakadik brahmadi munisa / narad sarad sahit ahisa",
        "meaning": "ऋषि, देव और विद्या-देवी भी स्तुति करते हैं।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जम कुबेर दिगपाल जहाँ ते\nकबि कोबिद कहि सके कहाँ ते",
        "text_romanized": "yam kuber digpal jahan te / kavi kobid kahi sake kahan te",
        "meaning": "देवगण और कवि भी यश का पार नहीं पाते।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "तुम उपकार सुग्रीवहिं कीन्हा\nराम मिलाय राज पद दीन्हा",
        "text_romanized": "tum upkar sugrivahin kinha / ram milay raj pad dinha",
        "meaning": "सुग्रीव को राम से मिलाकर राज्य-प्राप्ति कराई।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "तुम्हरो मंत्र बिभीषन माना\nलंकेश्वर भए सब जग जाना",
        "text_romanized": "tumharo mantra vibhishan mana / lankeshvar bhaye sab jag jana",
        "meaning": "विभीषण ने परामर्श मानकर लंका का राज्य पाया।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जुग सहस्र जोजन पर भानू\nलील्यो ताहि मधुर फल जानू",
        "text_romanized": "jug sahastra jojan par bhanu / lilyo tahi madhur phal janu",
        "meaning": "बाल्यकाल की असाधारण शक्ति का संकेत।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "प्रभु मुद्रिका मेलि मुख माहीं\nजलधि लांघि गए अचरज नाहीं",
        "text_romanized": "prabhu mudrika meli mukh mahi / jaladhi langhi gaye acharaj nahi",
        "meaning": "राम-मुद्रिका लेकर समुद्र लांघना।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "दुर्गम काज जगत के जेते\nसुगम अनुग्रह तुम्हरे तेते",
        "text_romanized": "durgam kaj jagat ke jete / sugam anugrah tumhare tete",
        "meaning": "हनुमान-कृपा से कठिन कार्य सुगम होते हैं।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "राम दुआरे तुम रखवारे\nहोत न आज्ञा बिनु पैसारे",
        "text_romanized": "ram duare tum rakhvare / hot na agya binu paisare",
        "meaning": "राम-द्वार के रक्षक रूप में हनुमान।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "सब सुख लहै तुम्हारी सरना\nतुम रक्षक काहू को डरना",
        "text_romanized": "sab sukh lahai tumhari sarna / tum rakshak kahu ko darna",
        "meaning": "शरणागत को निर्भयता और सुख।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "आपन तेज सम्हारो आपै\nतीनों लोक हांक ते काँपै",
        "text_romanized": "apan tej samharo apai / tino lok hank te kampai",
        "meaning": "दैवी तेज का स्वनियंत्रण और त्रिलोक-विभीषिका।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "भूत पिशाच निकट नहिं आवै\nमहावीर जब नाम सुनावै",
        "text_romanized": "bhoot pishach nikat nahin avai / mahavir jab nam sunavai",
        "meaning": "हनुमान-स्मरण से भय और नकारात्मकता दूर।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "नासै रोग हरै सब पीरा\nजपत निरंतर हनुमत बीरा",
        "text_romanized": "nasai rog harai sab pira / japat nirantar hanumat bira",
        "meaning": "जप से रोग-पीड़ा का क्षय।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "संकट तें हनुमान छुड़ावै\nमन क्रम वचन ध्यान जो लावै",
        "text_romanized": "sankat ten hanuman chhudavai / man kram vachan dhyan jo lavai",
        "meaning": "पूर्ण समर्पण से संकट-मुक्ति।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "सब पर राम तपस्वी राजा\nतिन के काज सकल तुम साजा",
        "text_romanized": "sab par ram tapasvi raja / tin ke kaj sakal tum saja",
        "meaning": "राम की मर्यादा-राजनीति में हनुमान की अनिवार्य भूमिका।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "और मनोरथ जो कोई लावै\nसोइ अमित जीवन फल पावै",
        "text_romanized": "aur manorath jo koi lavai / soi amit jivan phal pavai",
        "meaning": "सच्चे मनोरथों की सिद्धि।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "चारों जुग परताप तुम्हारा\nहै परसिद्ध जगत उजियारा",
        "text_romanized": "charon jug pratap tumhara / hai parasiddh jagat ujiyara",
        "meaning": "युगान्तरों में प्रसिद्ध पराक्रम।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "साधु संत के तुम रखवारे\nअसुर निकंदन राम दुलारे",
        "text_romanized": "sadhu sant ke tum rakhvare / asur nikandan ram dulare",
        "meaning": "संत-रक्षा और दुष्ट-विनाश।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "अष्ट सिद्धि नौ निधि के दाता\nअस बर दीन जानकी माता",
        "text_romanized": "asht siddhi nau nidhi ke data / as bar din janaki mata",
        "meaning": "सीता-वरणित कृपा और सिद्धि-निधि दान।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "राम रसायन तुम्हरे पासा\nसदा रहो रघुपति के दासा",
        "text_romanized": "ram rasayan tumhare pasa / sada raho raghupati ke dasa",
        "meaning": "राम-नाम का अमृत और दास्य-भाव।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "तुम्हरे भजन राम को पावै\nजनम जनम के दुख बिसरावै",
        "text_romanized": "tumhare bhajan ram ko pavai / janam janam ke dukh bisaravai",
        "meaning": "हनुमान-भक्ति से राम-प्राप्ति और दुःख-निवारण।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "अंतकाल रघुबर पुर जाई\nजहाँ जन्म हरि भक्त कहाई",
        "text_romanized": "antkal raghubar pur jai / jahan janm hari bhakt kahai",
        "meaning": "मुक्ति और भक्त-जन्म की कामना।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "और देवता चित्त न धरई\nहनुमत सेइ सर्व सुख करई",
        "text_romanized": "aur devata chitt na dharai / hanumat sei sarv sukh karai",
        "meaning": "एकनिष्ठ भक्ति से सर्वसुख प्राप्ति।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "संकट कटै मिटै सब पीरा\nजो सुमिरै हनुमत बलबीरा",
        "text_romanized": "sankat katai mitai sab pira / jo sumirai hanumat balbira",
        "meaning": "स्मरण से संकट और पीड़ा का क्षय।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जै जै जै हनुमान गोसाईं\nकृपा करहु गुरुदेव की नाईं",
        "text_romanized": "jai jai jai hanuman gosai / kripa karahu gurudev ki nai",
        "meaning": "हनुमान से गुरु-तुल्य कृपा की विनती।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जो सत बार पाठ कर कोई\nछूटहि बंदि महा सुख होई",
        "text_romanized": "jo sat bar path kar koi / chhutahi bandi maha sukh hoi",
        "meaning": "नियमित पाठ से बंधन-मोचन।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "जो यह पढ़ै हनुमान चालीसा\nहोय सिद्धि साखी गौरीसा",
        "text_romanized": "jo yah padhai hanuman chalisa / hoy siddhi sakhi gaurisa",
        "meaning": "चालीसा-पाठ की सिद्धि पर शिव-साक्ष्य।",
    },
    {
        "poetry_type": "chaupai",
        "main_text": "तुलसीदास सदा हरि चेरा\nकीजै नाथ हृदय महँ डेरा",
        "text_romanized": "tulsidas sada hari chera / kijai nath hriday mah dera",
        "meaning": "तुलसी की विनम्र प्रार्थना कि प्रभु हृदय में वास करें।",
    },
    {
        "poetry_type": "doha",
        "main_text": "पवन तनय संकट हरन मंगल मूरति रूप\nराम लखन सीता सहित हृदय बसहु सुर भूप",
        "text_romanized": "pavan tanay sankat haran mangal murti roop / ram lakhan sita sahit hriday basahu sur bhoop",
        "meaning": "हनुमान से अंतःकरण में राम-परिवार सहित निवास की प्रार्थना।",
    },
]


HANUMAN_BAHUK_SEQUENCE = [
    {
        "poetry_type": "doha",
        "main_text": "बाहु बिकल भए दीन हौं, राखहु नाथ अनूप।\nतुलसी के उर बास करि, मिटवहु सकल स्वरूप॥",
        "text_romanized": "bahu bikal bhae din haun, rakhahu nath anoop / tulsi ke ur bas kari, mitavahu sakal swaroop",
        "meaning": "कवि अपनी शारीरिक पीड़ा के बीच आराध्य से शरण मांगते हैं।",
        "prosody": {"note": "opening doha"},
    },
    {
        "poetry_type": "ghanakshari",
        "main_text": "जर्जर तन, जुगुप्सित ज्वर, जड़ बुद्धि, जड़ प्राण।\nनाम तुम्हारो नीक लागै, तजै सकल संत्राण॥",
        "text_romanized": "jarjar tan, jugupsit jvar, jad buddhi, jad pran / nam tumharo nik lagai, tajai sakal santran",
        "meaning": "हनुमान-नाम को रोग-ताप से मुक्ति का औषध माना गया है।",
        "prosody": {"chhand": "ghanakshari"},
    },
    {
        "poetry_type": "chappay",
        "main_text": "काँचहि देह, कराल व्यथा, कंपत कपाल सबै।\nराम-दूत बल-निधान, करुना करहु अबै॥",
        "text_romanized": "kanchahi deh, karal vyatha, kampat kapal sabai / ram-dut bal-nidhan, karuna karahu abai",
        "meaning": "कष्ट के क्षण में दूत-भाव और करुणा-विनय का संगम।",
        "prosody": {"chhand": "chappay"},
    },
    {
        "poetry_type": "savaiya",
        "main_text": "दुःख-दलित मन, दरदित तन, दिन-रैन जपत हनुमान।\nदया दृष्टि दै दास पर, हरि-सेवक करहु सुजान॥",
        "text_romanized": "dukh-dalit man, daradit tan, din-rain japat hanuman / daya drishti dai das par, hari-sevak karahu sujan",
        "meaning": "भक्ति-निरंतरता और कृपा-दृष्टि का आवाहन।",
        "prosody": {"chhand": "savaiya"},
    },
    {
        "poetry_type": "jhulana",
        "main_text": "डोलत पीर, डोलत प्राण, झूलत जग संसार।\nहनुमत नाव सम्हारि लेहु, पार लगावनहार॥",
        "text_romanized": "dolat pir, dolat pran, jhoolat jag sansar / hanumat nav samhri lehu, par lagavanhar",
        "meaning": "पीड़ा-रूपी डोल को भक्ति-नौका से पार लगाने की छवि।",
        "prosody": {"chhand": "jhulana"},
    },
    {
        "poetry_type": "doha",
        "main_text": "रामदूत गुण गाइ कै, तुलसी भरोसनि आय।\nबाहु-विकार बिलोकि प्रभु, संकट सबहि नसाय॥",
        "text_romanized": "ramdut gun gai kai, tulsi bharosani ay / bahu-vikar biloki prabhu, sankat sabahi nasay",
        "meaning": "समापन में आराध्य पर पूर्ण भरोसा व्यक्त होता है।",
        "prosody": {"note": "closing doha"},
    },
]


DICTIONARY_ROOTS = [
    ("अँख", "ankh", "eye"),
    ("अँगना", "angana", "courtyard"),
    ("अइसन", "aisan", "such"),
    ("अउर", "aur", "and/other"),
    ("अंजोर", "anjor", "light"),
    ("अभाव", "abhav", "lack"),
    ("अचरज", "acharaj", "wonder"),
    ("अलस", "alas", "lazy"),
    ("आगर", "agar", "storehouse"),
    ("आँगन", "angan", "yard"),
    ("इहाँ", "ihan", "here"),
    ("इमान", "iman", "integrity"),
    ("इकबाल", "iqbal", "fortune"),
    ("ईमानदारी", "imandari", "honesty"),
    ("उतरन", "utaran", "cast-off cloth"),
    ("उसर", "usar", "barren field"),
    ("ऊसरही", "usarahi", "dry-land region"),
    ("ऋतु", "ritu", "season"),
    ("एहसान", "ehsan", "favor"),
    ("ओसारा", "osara", "verandah"),
    ("कजरौटा", "kajrauta", "kohl box"),
    ("कनक", "kanak", "gold"),
    ("कुवार", "kuwar", "bachelor"),
    ("कुहराम", "kuharam", "outcry"),
    ("कोठार", "kothar", "granary"),
    ("खेतिहा", "khetiha", "farmer"),
    ("खोंइछा", "khoincha", "cloth-fold offering"),
    ("खदर", "khadar", "riverine soil"),
    ("गँवई", "ganwai", "rural"),
    ("गोरस", "goras", "milk essence"),
    ("गिरस्ती", "girasthi", "household life"),
    ("घाम", "gham", "sunlight"),
    ("घुरवा", "ghurwa", "cattle resting ground"),
    ("चउरा", "chaura", "village shrine platform"),
    ("चिरई", "chirai", "bird"),
    ("चिरौंजी", "chironji", "charoli seed"),
    ("छैंहा", "chhaiha", "shade"),
    ("जगतरा", "jagatra", "worldly bustle"),
    ("जुगत", "jugat", "method"),
    ("झिंगुर", "jhingur", "cricket insect"),
    ("टेक", "tek", "support"),
    ("ठठेर", "thather", "coppersmith"),
    ("डगर", "dagar", "path"),
    ("ढेबर", "dhebar", "lump"),
    ("तिरिया", "tiriya", "woman"),
    ("तिराहा", "tiraha", "three-way junction"),
    ("थरिया", "thariya", "metal plate"),
    ("दउरी", "dauri", "bamboo basket"),
    ("दुआरिया", "duariya", "doorway"),
    ("देसज", "desaj", "native/vernacular"),
    ("धरती", "dharti", "earth"),
    ("नदिया", "nadiya", "river"),
    ("निरमल", "nirmal", "pure"),
    ("निहोरा", "nihora", "humble request"),
    ("पगहा", "pagaha", "rope for cattle"),
    ("पनघट", "panghat", "water-drawing place"),
    ("परनवा", "parnawa", "leaf-hut"),
    ("पहरुआ", "paharua", "watchman"),
    ("फगुआ", "phagua", "Holi season song"),
    ("बइठकी", "baithaki", "community sitting"),
    ("बदरिया", "badariya", "cloud"),
    ("बरकहा", "barkaha", "elder"),
    ("बिरवा", "birwa", "sapling"),
    ("बखत", "bakhat", "time"),
    ("भिनुसारे", "bhinusare", "early dawn"),
    ("भाखा", "bhakha", "language"),
    ("माटी", "mati", "soil"),
    ("मनवा", "manwa", "heart"),
    ("मुनरी", "munari", "ear ornament"),
    ("मड़ई", "madai", "hut"),
    ("रउरा", "raura", "you (respectful)"),
    ("रोज़गार", "rozgar", "livelihood"),
    ("रसधर", "rasdhar", "stream of emotion"),
    ("लइका", "laika", "child"),
    ("लहक", "lahak", "fragrance flourish"),
    ("विरहा", "viraha", "separation-longing"),
    ("सिवान", "sivan", "field boundary"),
    ("सुग्गा", "sugga", "parrot"),
    ("सनेस", "sanes", "message"),
    ("हियरा", "hiyara", "heart-core"),
    ("हरियर", "hariyar", "green"),
]


IDIOMS = [
    ("नाक कतराय देब", "nak kataray deb", "बेहद शर्मिंदा कर देना"),
    ("आँखी मिंजाय बैठब", "ankhi minjay baithab", "जानबूझकर अनदेखा करना"),
    ("मनवा डोले", "manwa dole", "अनिश्चितता में रहना"),
    ("कान पर जूँ न रेंगना", "kan par jun na rengna", "कोई असर न होना"),
    ("धरती फाट जाय", "dharti phat jay", "बहुत लज्जित होना"),
    ("हाथ मले रहि जाना", "hath male rahi jana", "अवसर खो देना"),
    ("घाम पियासे चलना", "gham piyase chalna", "कठिन परिश्रम करना"),
    ("दाल गलना", "dal galna", "काम बन जाना"),
    ("पानी-पानी होइ जाना", "pani pani hoi jana", "लज्जित हो जाना"),
    ("गठरी खोल देना", "gathri khol dena", "छिपी बात खोलना"),
    ("हियरा पर पत्थर रखना", "hiyara par patthar rakhna", "मन मार कर निर्णय लेना"),
    ("बात के बतासा बनाना", "bat ke batasa banana", "छोटी बात को बढ़ा देना"),
]


ARTICLE_BLUEPRINTS = [
    {
        "title": "The Evolution of Awadhi Sufi Poetry",
        "title_devanagari": "अवधी सूफ़ी काव्य का विकास",
        "title_roman": "Avadhi Sufi Kavya ka Vikas",
        "tags": ["awadhi", "sufi", "history", "poetics"],
        "body": """## प्रस्तावना\nअवधी में सूफ़ी काव्य की परंपरा मध्यकालीन उत्तर भारत की साझा सांस्कृतिक स्मृति का महत्त्वपूर्ण स्रोत है।\n\n## रूपांतरण की तीन धाराएँ\n1. प्रेमाख्यान परंपरा: लोक-कथाओं और आध्यात्मिक प्रतीकों का समावेश।\n2. रूपक-विस्तार: मानवीय प्रेम से ईश्वरीय प्रेम की ओर क्रमिक उन्नयन।\n3. बोलचाल की प्रतिष्ठा: दरबारी भाषा से भिन्न, लोक-प्रचलित अवधी में अभिव्यक्ति।\n\n## लेखक-परंपरा\nमलिक मुहम्मद जायसी, मंझन, कुतुबन, मुल्ला दाऊद जैसे कवियों ने अवधी को बौद्धिक और भावात्मक दोनों स्तरों पर सुदृढ़ किया।\n\n## निष्कर्ष\nसूफ़ी काव्य में अवधी केवल माध्यम नहीं, बल्कि सांस्कृतिक सेतु है जो भक्ति, लोक और दर्शन को जोड़ता है।""",
        "excerpt": "मध्यकालीन अवधी सूफ़ी काव्य की भाषिक और सांस्कृतिक यात्रा का समाहार।",
    },
    {
        "title": "Metrics of the Chaupai",
        "title_devanagari": "चौपाई का मात्रिक विन्यास",
        "title_roman": "Chaupai ka Matrik Vinyas",
        "tags": ["prosody", "chaupai", "metrics"],
        "body": """## छंद और श्रुति\nचौपाई अवधी परंपरा में कथा-विस्तार का सबसे सक्षम छंद है।\n\n## मात्रिक व्यवहार\nयद्यपि व्यवहार में क्षेत्रीय लचीलापन मिलता है, किंतु पाठ-स्मृति में संतुलित गति और अंत्यानुप्रास की अपेक्षा रहती है।\n\n## काव्य-संदर्भ\nरामचरितमानस सहित अनेक अवधी ग्रंथों में चौपाई अर्थ-गहनता और कथानक-प्रवाह के बीच संतुलन बनाती है।\n\n## पाठन-पद्धति\nमंद, मध्यम और तीव्र पाठ में चौपाई का असर बदलता है; शास्त्रीय अध्ययन में तीनों गति का तुलनात्मक अभ्यास आवश्यक है।""",
        "excerpt": "चौपाई के मात्रिक अनुशासन और व्यवहारिक पाठ पर एक तकनीकी लेख।",
    },
    {
        "title": "Jayasi and the Symbolic Landscape of Avadh",
        "title_devanagari": "जायसी और अवध का प्रतीक-परिदृश्य",
        "title_roman": "Jayasi aur Avadh ka Pratik-Paridrishya",
        "tags": ["jayasi", "symbolism", "awadh"],
        "body": """## ऐतिहासिक पृष्ठभूमि\nजायसी का काव्य लोक-इतिहास और आध्यात्मिक बिंबों के अद्वितीय मेल का उदाहरण है।\n\n## प्रतीक-समूह\nवन, जल, किला, यात्रा और विरह के प्रतीक अवधी के भौगोलिक अनुभव को आध्यात्मिक अर्थ देते हैं।\n\n## भाषा और लोक-स्मृति\nअवधी की ध्वन्यात्मक कोमलता जायसी के रूपकों को सहज और स्मरणीय बनाती है।\n\n## निष्कर्ष\nजायसी का परिदृश्य केवल भौगोलिक नहीं, बल्कि सांस्कृतिक-साधना का नक्शा है।""",
        "excerpt": "जायसी के काव्य में अवध-परिदृश्य की प्रतीकात्मक व्याख्या।",
    },
    {
        "title": "From Oral Tradition to Canon: Building Reliable Awadhi Text Archives",
        "title_devanagari": "मौखिक परंपरा से प्रमाणित पाठ तक",
        "title_roman": "Maukhik Parampara se Pramanit Path Tak",
        "tags": ["archive", "textual-criticism", "digitization"],
        "body": """## समस्या\nअवधी रचनाओं की मौखिक परंपरा में पाठ-भेद स्वाभाविक हैं।\n\n## संपादन सिद्धांत\n1. पांडुलिपि-आधार का तुलनात्मक लेखाजोखा\n2. लोक-प्रचलित पाठ का स्वतंत्र उल्लेख\n3. संस्करण-टिप्पणी में पाठांतरों का स्पष्ट वर्गीकरण\n\n## डिजिटल संरचना\npoetry_nodes जैसी क्रमांकित इकाई-रचना पाठ संरक्षण, विश्लेषण और पुनरुत्पादन तीनों में मदद करती है।\n\n## निष्कर्ष\nविश्वसनीय अभिलेखागार के लिए फिलोलॉजी और डेटा इंजीनियरिंग का संयुक्त मॉडल आवश्यक है।""",
        "excerpt": "अवधी पाठ-संरक्षण के लिए फिलोलॉजी और डिजिटल आर्किटेक्चर का संयुक्त दृष्टिकोण।",
    },
    {
        "title": "Awadhi Lexicon Design for Computational Humanities",
        "title_devanagari": "संगणकीय मानवीकी हेतु अवधी शब्द-संसाधन",
        "title_roman": "Sanganakiy Manviki Hetu Avadhi Shabd-Sansadhan",
        "tags": ["dictionary", "nlp", "awadhi"],
        "body": """## क्यों आवश्यक\nभाषाई संसाधन के बिना अवधी पर उच्च-गुणवत्ता शोध और NLP मॉडल दोनों सीमित रह जाते हैं।\n\n## शब्द-प्रविष्टि के घटक\nलेम्मा (देवनागरी), रोमन रूप, मानकीकृत रोमन, बहु-सेंस अर्थ, और उदाहरण वाक्य।\n\n## डेटा गुणवत्ता\nसमानार्थ, उच्चारण-भेद, और क्षेत्रीय रूपों के लिए संरचित JSON-सेंस मॉडल सबसे उपयोगी पाया गया है।\n\n## निष्कर्ष\nएक समृद्ध, सत्यापित अवधी शब्द-संसाधन से साहित्य-अध्ययन और तकनीकी अनुप्रयोग दोनों को गति मिलती है।""",
        "excerpt": "अवधी शब्दकोश की डेटा-आधारित संरचना और उसके संगणकीय लाभ।",
    },
]


@dataclass
class ContentPools:
    poetry_nodes: list[int]
    dictionary_entries: list[int]
    idiom_entries: list[int]
    article_entries: list[int]


def log(message: str) -> None:
    print(f"[seed] {message}")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    slug = value.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def roman_norm(value: str | None) -> str | None:
    if value is None:
        return None
    norm = value.lower().strip()
    norm = re.sub(r"[^a-z0-9\s-]", "", norm)
    norm = re.sub(r"[\s_-]+", " ", norm)
    return norm


def set_fk_checks(db: Session, enabled: bool) -> None:
    dialect = engine.dialect.name
    if dialect == "mysql":
        db.execute(text(f"SET FOREIGN_KEY_CHECKS = {1 if enabled else 0}"))
    elif dialect == "sqlite":
        db.execute(text(f"PRAGMA foreign_keys = {'ON' if enabled else 'OFF'}"))


def safe_surgical_wipe(db: Session) -> None:
    log("Starting surgical wipe with temporary FK disable")
    set_fk_checks(db, enabled=False)
    try:
        ordered_deletes = [
            "user_interactions",
            "engagement_kpis",
            "audit_logs",
            "poetry_nodes",
            "work_chapters",
            "classical_works",
            "classical_authors",
            "dictionary_entries",
            "idiom_entries",
            "article_entries",
        ]
        for table in ordered_deletes:
            db.execute(text(f"DELETE FROM {table}"))

        db.execute(
            text(
                """
                DELETE FROM users
                WHERE LOWER(email) NOT LIKE 'adarsh%'
                  AND LOWER(email) NOT LIKE 'veer%'
                  AND LOWER(email) NOT LIKE 'awadhi%'
                  AND LOWER(COALESCE(username, '')) NOT LIKE 'adarsh%'
                  AND LOWER(COALESCE(username, '')) NOT LIKE 'veer%'
                  AND LOWER(COALESCE(username, '')) NOT LIKE 'awadhi%'
                """
            )
        )
        db.commit()
    finally:
        set_fk_checks(db, enabled=True)
    log("Surgical wipe completed")


def ensure_poetry_registry(db: Session) -> None:
    for ptype, display, family in POETRY_TYPES:
        row = db.query(PoetryTypeRegistry).filter(PoetryTypeRegistry.poetry_type == ptype).first()
        if row:
            row.display_name = display
            row.family = family
            row.is_active = True
        else:
            db.add(
                PoetryTypeRegistry(
                    poetry_type=ptype,
                    display_name=display,
                    family=family,
                    is_user_defined=False,
                    is_active=True,
                )
            )
    db.commit()


def get_preserved_admin_users(db: Session) -> list[User]:
    users = (
        db.query(User)
        .filter(
            (User.email.ilike("adarsh%"))
            | (User.email.ilike("veer%"))
            | (User.email.ilike("awadhi%"))
            | (User.username.ilike("adarsh%"))
            | (User.username.ilike("veer%"))
            | (User.username.ilike("awadhi%"))
        )
        .all()
    )
    if not users:
        raise RuntimeError("No preserved admin users found. Seed aborted to protect access controls.")
    return users


def seed_authors(db: Session) -> dict[str, ClassicalAuthor]:
    log("Seeding exactly 40 authentic Awadhi authors")
    author_map: dict[str, ClassicalAuthor] = {}
    for name in AUTHORS:
        slug = slugify(name)
        author = ClassicalAuthor(
            name=name,
            slug=slug,
            language="Awadhi",
            short_bio=f"{name} is a historically documented contributor to the Awadhi literary tradition.",
            long_bio=(
                f"{name} belongs to the historical continuum of Awadhi literature. "
                "This profile is seeded for canonical archival, analytics realism, and interconnected content modeling."
            ),
        )
        db.add(author)
        author_map[name] = author
    db.commit()
    return author_map


def create_work_with_chapter(
    db: Session,
    author: ClassicalAuthor,
    title: str,
    work_type: str,
    chapter_title: str,
) -> tuple[ClassicalWork, WorkChapter]:
    work = ClassicalWork(
        author_id=author.id,
        slug=slugify(title),
        title=title,
        description=f"Canonical seeded work: {title}",
        work_type=work_type,
        original_script="Devanagari",
    )
    db.add(work)
    db.flush()

    chapter = WorkChapter(
        work_id=work.id,
        slug=slugify(chapter_title),
        title=chapter_title,
        number=1,
    )
    db.add(chapter)
    db.flush()
    return work, chapter


def seed_hanuman_chalisa(
    db: Session,
    admin_user_id: int,
    tulsidas: ClassicalAuthor,
) -> tuple[int, int, int]:
    work, chapter = create_work_with_chapter(
        db,
        author=tulsidas,
        title="Hanuman Chalisa",
        work_type="stotra",
        chapter_title="Mangalacharan and Chalisa",
    )

    if len(HANUMAN_CHALISA_NODES) != 43:
        raise RuntimeError("Hanuman Chalisa payload must contain exactly 43 nodes.")

    opening = HANUMAN_CHALISA_NODES[:2]
    middle = HANUMAN_CHALISA_NODES[2:-1]
    closing = HANUMAN_CHALISA_NODES[-1]
    if any(node["poetry_type"] != "doha" for node in opening):
        raise RuntimeError("Hanuman Chalisa must open with two doha nodes.")
    if len(middle) != 40 or any(node["poetry_type"] != "chaupai" for node in middle):
        raise RuntimeError("Hanuman Chalisa middle sequence must be exactly 40 chaupai nodes.")
    if closing["poetry_type"] != "doha":
        raise RuntimeError("Hanuman Chalisa must end with a doha node.")

    for idx, node in enumerate(HANUMAN_CHALISA_NODES, start=1):
        db.add(
            PoetryNode(
                author_id=tulsidas.id,
                work_id=work.id,
                chapter_id=chapter.id,
                poetry_type=node["poetry_type"],
                sequence_no=idx,
                main_text=node["main_text"],
                text_devanagari=node["main_text"],
                text_romanized=node["text_romanized"],
                meaning=node["meaning"],
                prosody_metadata={"source": "Hanuman Chalisa", "index": idx},
                status="active",
                visibility="public",
                created_by=admin_user_id,
                verified_by=admin_user_id,
                verified_at=now_utc(),
            )
        )

    db.commit()
    log("Seeded Hanuman Chalisa with 43 ordered poetry nodes")
    return work.id, chapter.id, 43


def seed_hanuman_bahuk(
    db: Session,
    admin_user_id: int,
    tulsidas: ClassicalAuthor,
) -> tuple[int, int, int]:
    work, chapter = create_work_with_chapter(
        db,
        author=tulsidas,
        title="Hanuman Bahuk",
        work_type="bhakti-kavya",
        chapter_title="Bahuk Verses",
    )

    required_types = {"ghanakshari", "chappay", "jhulana", "savaiya"}
    present_types = {node["poetry_type"] for node in HANUMAN_BAHUK_SEQUENCE}
    if not required_types.issubset(present_types):
        raise RuntimeError("Hanuman Bahuk sequence is missing required extended poetry types.")

    for idx, node in enumerate(HANUMAN_BAHUK_SEQUENCE, start=1):
        db.add(
            PoetryNode(
                author_id=tulsidas.id,
                work_id=work.id,
                chapter_id=chapter.id,
                poetry_type=node["poetry_type"],
                sequence_no=idx,
                main_text=node["main_text"],
                text_devanagari=node["main_text"],
                text_romanized=node["text_romanized"],
                meaning=node["meaning"],
                prosody_metadata=node.get("prosody", {}),
                status="active",
                visibility="public",
                created_by=admin_user_id,
                verified_by=admin_user_id,
                verified_at=now_utc(),
            )
        )

    db.commit()
    log("Seeded Hanuman Bahuk with mixed poetry types including ghanakshari/chappay/jhulana/savaiya")
    return work.id, chapter.id, len(HANUMAN_BAHUK_SEQUENCE)


def synthetic_verse_line(rng: random.Random) -> tuple[str, str, str]:
    starts = ["मनवा", "धरती", "नदिया", "साँझ", "भोर", "देस", "लोक", "हियरा", "माटी", "सनेस"]
    mids = ["गावे", "कहे", "सुनावे", "रोवे", "झरे", "डोले", "जागे", "बुने", "सँवारे", "दोहरे"]
    ends = ["राम नाम", "प्रेम रस", "लोक सुर", "पीर कथा", "श्रुति परंपरा", "कथा धारा", "विरह अगन", "सुफियाना रंग"]

    line1 = f"{rng.choice(starts)} {rng.choice(mids)} {rng.choice(ends)}"
    line2 = f"{rng.choice(starts)} {rng.choice(mids)} {rng.choice(ends)}"
    devanagari = f"{line1}\n{line2}"
    roman = roman_norm(f"{line1} / {line2}") or ""
    meaning = "लोकानुभव, भक्ति और विरह के संयोग से रचित अवधी पद्य।"
    return devanagari, roman, meaning


def seed_general_poetry(
    db: Session,
    admin_user_id: int,
    authors: dict[str, ClassicalAuthor],
    tulsidas_name: str = "Goswami Tulsidas",
) -> list[int]:
    rng = random.Random(RANDOM_SEED)
    work_counter = 0
    poetry_ids: list[int] = []

    for name in AUTHORS:
        if name == tulsidas_name:
            continue

        author = authors[name]
        work_count = 2 if rng.random() < 0.55 else 3

        for w_idx in range(1, work_count + 1):
            work_title = f"{name} Granth {w_idx}"
            work, chapter = create_work_with_chapter(
                db,
                author=author,
                title=work_title,
                work_type="kavya" if w_idx % 2 else "lok-geet",
                chapter_title="Pratham Adhyay",
            )

            node_count = rng.randint(14, 28)
            for s_idx in range(1, node_count + 1):
                if s_idx % 5 == 0:
                    ptype = "sorath"
                elif s_idx % 2 == 0:
                    ptype = "doha"
                else:
                    ptype = "other_poetry"

                text_dev, text_rom, meaning = synthetic_verse_line(rng)
                node = PoetryNode(
                    author_id=author.id,
                    work_id=work.id,
                    chapter_id=chapter.id,
                    poetry_type=ptype,
                    sequence_no=s_idx,
                    main_text=text_dev,
                    text_devanagari=text_dev,
                    text_romanized=text_rom,
                    meaning=meaning,
                    prosody_metadata={"generator": "seed-general", "meter_hint": ptype},
                    status="active",
                    visibility="public",
                    created_by=admin_user_id,
                    verified_by=admin_user_id,
                    verified_at=now_utc(),
                )
                db.add(node)
                db.flush()
                poetry_ids.append(node.id)

            work_counter += 1
            db.commit()

    log(f"Seeded {work_counter} general works for 38 authors")
    return poetry_ids


def build_dictionary_rows(target: int, rng: random.Random) -> list[tuple[str, str, str, str]]:
    forms = ["", "वा", "इया", "हट", "पन", "इन", "कन", "ई", "उआ", "हिया"]
    semantic_domains = [
        "कृषि", "गृह-जीवन", "ऋतु", "भक्ति", "लोक-नृत्य", "ग्राम-व्यवस्था", "व्यापार", "संबंध", "रीति", "आहार"
    ]

    rows: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()

    while len(rows) < target:
        base_dev, base_rom, base_mean = rng.choice(DICTIONARY_ROOTS)
        suffix = rng.choice(forms)
        lemma_dev = f"{base_dev}{suffix}"
        lemma_rom = f"{base_rom}{suffix}"
        norm = roman_norm(lemma_rom) or lemma_rom.lower()
        if lemma_dev in seen:
            continue
        seen.add(lemma_dev)
        domain = rng.choice(semantic_domains)
        meaning = f"{base_mean}; अवधी {domain} प्रयोग में प्रचलित रूप"
        rows.append((lemma_dev, lemma_rom, norm, meaning))

    return rows


def seed_dictionary(db: Session, admin_user_id: int) -> list[int]:
    rng = random.Random(RANDOM_SEED + 7)
    rows = build_dictionary_rows(MIN_DICTIONARY_ENTRIES, rng)
    dictionary_ids: list[int] = []

    for idx, (lemma_dev, lemma_rom, norm, meaning) in enumerate(rows, start=1):
        examples = [
            {
                "text_devanagari": f"गाँव के बुजुर्ग आज भी '{lemma_dev}' कहत हैं।",
                "text_roman": f"ganv ke bujurg aj bhi '{lemma_rom}' kahat hain.",
            }
        ]
        entry = DictionaryEntry(
            lemma_devanagari=lemma_dev,
            lemma_roman=lemma_rom,
            lemma_roman_norm=norm,
            language="awa",
            senses=[{"gloss": meaning, "domain": "awadhi", "sense_no": 1}],
            pronunciation=lemma_rom,
            examples=examples,
            contributor_id=admin_user_id,
            visibility="public",
            version=1,
        )
        db.add(entry)
        if idx % 100 == 0:
            db.flush()
            db.commit()

    db.commit()
    dictionary_ids = [row.id for row in db.query(DictionaryEntry.id).all()]
    log(f"Seeded {len(dictionary_ids)} dictionary entries")
    return dictionary_ids


def seed_idioms(db: Session, admin_user_id: int) -> list[int]:
    rng = random.Random(RANDOM_SEED + 13)
    idiom_rows: list[tuple[str, str, str]] = list(IDIOMS)
    fillers = [
        "खेत में कागा हँसे", "बिन पानी नाव", "आधी रात परेर", "दू गो नाव पर पाँव", "मन के पंछी", "मुँहवा पे ताला",
        "हाथ में राख", "धान कटे तब जान", "दुआर पर धूप", "नदिया उलटी बहे", "तिनका सम आस", "घाट-घाट पानी"
    ]

    while len(idiom_rows) < IDIOM_COUNT:
        phrase = f"{rng.choice(fillers)} {rng.choice(['रहे', 'पड़े', 'चले', 'देखे'])}"
        roman = roman_norm(phrase) or ""
        meaning = rng.choice([
            "अस्थिर परिस्थिति में सावधानी बरतना",
            "अनुभव के बिना निर्णय न लेना",
            "संकेत समझकर समय पर कार्य करना",
            "सीमित साधनों में संतुलन बनाना",
        ])
        idiom_rows.append((phrase, roman, meaning))

    idiom_ids: list[int] = []
    for idx, (text_dev, text_rom, meaning) in enumerate(idiom_rows, start=1):
        row = IdiomEntry(
            text_devanagari=text_dev,
            text_roman=text_rom,
            text_roman_norm=roman_norm(text_rom),
            meaning=meaning,
            examples=[{"text": f"आज दादी कहिन - {text_dev}", "context": "लोक कथन"}],
            region="Awadh",
            contributor_id=admin_user_id,
            visibility="public",
            version=1,
        )
        db.add(row)
        if idx % 50 == 0:
            db.flush()
            db.commit()

    db.commit()
    idiom_ids = [row.id for row in db.query(IdiomEntry.id).all()]
    log(f"Seeded {len(idiom_ids)} idiom entries")
    return idiom_ids


def seed_articles(db: Session, admin_user_id: int) -> list[int]:
    if not (4 <= ARTICLE_COUNT <= 6):
        raise RuntimeError("Article count must remain in the 4..6 range.")

    for blueprint in ARTICLE_BLUEPRINTS[:ARTICLE_COUNT]:
        db.add(
            ArticleEntry(
                title=blueprint["title"],
                title_devanagari=blueprint["title_devanagari"],
                title_roman=blueprint["title_roman"],
                title_roman_norm=roman_norm(blueprint["title_roman"]),
                body=blueprint["body"],
                excerpt=blueprint["excerpt"],
                tags=blueprint["tags"],
                author_id=admin_user_id,
                contributor_id=admin_user_id,
                visibility="public",
                version=1,
            )
        )
    db.commit()
    article_ids = [row.id for row in db.query(ArticleEntry.id).all()]
    log(f"Seeded {len(article_ids)} article entries")
    return article_ids


def generate_content_pools(db: Session) -> ContentPools:
    poetry_ids = [row.id for row in db.query(PoetryNode.id).all()]
    dictionary_ids = [row.id for row in db.query(DictionaryEntry.id).all()]
    idiom_ids = [row.id for row in db.query(IdiomEntry.id).all()]
    article_ids = [row.id for row in db.query(ArticleEntry.id).all()]
    return ContentPools(
        poetry_nodes=poetry_ids,
        dictionary_entries=dictionary_ids,
        idiom_entries=idiom_ids,
        article_entries=article_ids,
    )


def seed_user_interactions_and_kpis(
    db: Session,
    admins: list[User],
    pools: ContentPools,
) -> None:
    rng = random.Random(RANDOM_SEED + 23)

    content_space: list[tuple[str, int]] = []
    content_space.extend([("poetry_node", cid) for cid in pools.poetry_nodes])
    content_space.extend([("dictionary", cid) for cid in pools.dictionary_entries])
    content_space.extend([("idiom", cid) for cid in pools.idiom_entries])
    content_space.extend([("article", cid) for cid in pools.article_entries])

    if not content_space:
        raise RuntimeError("No seeded content found for interaction simulation.")

    interaction_index: dict[tuple[int, str, int, str], UserInteraction] = {}

    for _ in range(INTERACTION_TARGET):
        admin = rng.choice(admins)
        content_type, content_id = rng.choice(content_space)
        interaction_type = rng.choice(["like", "bookmark", "view"])

        key = (admin.id, content_type, content_id, interaction_type)
        row = interaction_index.get(key)
        if row is None:
            row = UserInteraction(
                user_id=admin.id,
                content_type=content_type,
                content_id=content_id,
                interaction_type=interaction_type,
                is_active=True,
                interaction_metadata={"seed": "kpi-simulation", "source": "dashboard"},
            )
            interaction_index[key] = row
            db.add(row)

    db.flush()

    kpi_map: dict[tuple[str, int], EngagementKPI] = {}
    for content_type, content_id in content_space:
        base_views = rng.randint(120, 900)
        kpi_map[(content_type, content_id)] = EngagementKPI(
            content_type=content_type,
            content_id=content_id,
            views_count=base_views,
            search_hits_count=max(10, int(base_views * rng.uniform(0.1, 0.45))),
            likes_count=0,
            shares_count=rng.randint(3, 90),
            bookmarks_count=0,
            weight_score=0.0,
        )

    for row in interaction_index.values():
        kpi = kpi_map[(row.content_type, row.content_id)]
        if row.interaction_type == "view":
            kpi.views_count += 1
        elif row.interaction_type == "like":
            kpi.likes_count += 1
        elif row.interaction_type == "bookmark":
            kpi.bookmarks_count += 1

    for kpi in kpi_map.values():
        kpi.weight_score = round(
            (kpi.views_count * 0.4)
            + (kpi.search_hits_count * 0.6)
            + (kpi.likes_count * 2.5)
            + (kpi.bookmarks_count * 3.0)
            + (kpi.shares_count * 1.8),
            2,
        )
        db.add(kpi)

    db.commit()
    log(f"Seeded {len(interaction_index)} user interactions and {len(kpi_map)} KPI rows")


def seed_audit_logs(db: Session, admins: list[User], pools: ContentPools) -> None:
    rng = random.Random(RANDOM_SEED + 33)
    actions = ["content.view", "content.like", "content.bookmark", "admin.analytics.refresh", "admin.export"]

    content_space: list[tuple[str, int]] = []
    content_space.extend([("poetry_node", cid) for cid in pools.poetry_nodes])
    content_space.extend([("dictionary", cid) for cid in pools.dictionary_entries])
    content_space.extend([("idiom", cid) for cid in pools.idiom_entries])
    content_space.extend([("article", cid) for cid in pools.article_entries])

    start_ts = now_utc() - timedelta(days=45)

    for idx in range(1, AUDIT_LOG_TARGET + 1):
        admin = rng.choice(admins)
        resource_type, resource_id = rng.choice(content_space)
        action = rng.choice(actions)
        ts = start_ts + timedelta(minutes=idx * rng.randint(1, 8))

        db.add(
            AuditLog(
                actor_user_id=admin.id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                audit_before={"status": "seeded"},
                after={"status": "active", "note": "simulated"},
                audit_metadata={"origin": "seed_script", "timeline": "dashboard-bootstrap"},
                created_at=ts,
            )
        )

        if idx % 300 == 0:
            db.flush()
            db.commit()

    db.commit()
    log(f"Seeded {AUDIT_LOG_TARGET} audit logs")


def run_seed() -> None:
    random.seed(RANDOM_SEED)
    db = SessionLocal()
    try:
        log("Starting production-grade Awadhi seed pipeline")
        safe_surgical_wipe(db)
        ensure_poetry_registry(db)

        admins = get_preserved_admin_users(db)
        primary_admin_id = admins[0].id

        authors = seed_authors(db)
        tulsidas = authors["Goswami Tulsidas"]

        seed_hanuman_chalisa(db, admin_user_id=primary_admin_id, tulsidas=tulsidas)
        seed_hanuman_bahuk(db, admin_user_id=primary_admin_id, tulsidas=tulsidas)

        seed_general_poetry(db, admin_user_id=primary_admin_id, authors=authors)
        seed_dictionary(db, admin_user_id=primary_admin_id)
        seed_idioms(db, admin_user_id=primary_admin_id)
        seed_articles(db, admin_user_id=primary_admin_id)

        pools = generate_content_pools(db)
        seed_user_interactions_and_kpis(db, admins=admins, pools=pools)
        seed_audit_logs(db, admins=admins, pools=pools)

        log("Seed completed successfully")
        log(f"Authors: {db.query(ClassicalAuthor).count()}")
        log(f"Works: {db.query(ClassicalWork).count()}")
        log(f"Chapters: {db.query(WorkChapter).count()}")
        log(f"Poetry nodes: {db.query(PoetryNode).count()}")
        log(f"Dictionary entries: {db.query(DictionaryEntry).count()}")
        log(f"Idioms: {db.query(IdiomEntry).count()}")
        log(f"Articles: {db.query(ArticleEntry).count()}")
        log(f"Interactions: {db.query(UserInteraction).count()}")
        log(f"KPIs: {db.query(EngagementKPI).count()}")
        log(f"Audit logs: {db.query(AuditLog).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
