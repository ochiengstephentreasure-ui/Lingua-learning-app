from flask import Flask, jsonify, request, send_from_directory
import json
import os
import re
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

app = Flask(__name__, static_folder=".", static_url_path="")

LANGUAGES = {
    "en": "English",
    "sw": "Kiswahili",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "lg": "Luganda",
    "ach": "Acholi",
    "luo": "Luo",
    "rw": "Kinyarwanda",
    "ar": "Arabic",
    "hi": "Hindi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

ONLINE_TIMEOUT = 20
MAX_LENGTH = 5000

# Complete phrases are checked before individual words. This gives the
# offline fallback more natural results for common sentences.
PHRASES = {
    "sw": {
        "good morning": "habari za asubuhi",
        "good afternoon": "habari za mchana",
        "good evening": "habari za jioni",
        "good night": "usiku mwema",
        "how are you": "habari yako",
        "i am fine": "niko salama",
        "thank you very much": "asante sana",
        "you are welcome": "karibu",
        "please help me": "tafadhali nisaidie",
        "i need help": "nahitaji msaada",
        "i do not understand": "sielewi",
        "please speak slowly": "tafadhali zungumza polepole",
        "where is the bathroom": "choo kiko wapi",
        "how much does it cost": "inagharimu kiasi gani",
        "i would like some water": "ningependa maji",
        "i am hungry": "nina njaa",
        "the food is delicious": "chakula ni kitamu",
        "i am sorry": "samahani",
        "what time is it": "saa ngapi",
        "have a nice day": "uwe na siku njema",
        "see you soon": "tutaonana hivi karibuni",
        "i love you": "nakupenda",
        "i like coding": "napenda kuandika msimbo",
        "i love coding": "napenda sana kuandika msimbo",
        "i am learning to code": "ninajifunza kuandika msimbo",
        "i am a software developer": "mimi ni msanidi wa programu",
        "i am working from home": "ninafanya kazi kutoka nyumbani",
        "i will call you later": "nitakupigia simu baadaye",
        "everything is ready": "kila kitu kiko tayari",
        "let us go": "twende",
        "come and eat": "njoo ule",
        "come and drink": "njoo unywe",
        "come and sit down": "njoo ukae",
        "go and eat": "enda ule",
        "go and drink water": "enda unywe maji",
        "eat and drink": "kula na kunywa",
        "please come and eat": "tafadhali njoo ule",
        "come eat": "njoo ule",
        "come and have some food": "njoo ule chakula",
        "please come and have some food": "tafadhali njoo ule chakula",
        "please come inside": "tafadhali ingia ndani",
        "wait a moment": "subiri kidogo",
        "good luck": "bahati njema",
        "can you repeat that": "unaweza kurudia hiyo",
        "please write it down": "tafadhali iandike",
        "i speak a little swahili": "nazungumza Kiswahili kidogo",
        "do you speak english": "unaongea Kiingereza",
        "i am looking for the hotel": "natafuta hoteli",
        "where can i buy a ticket": "naweza kununua tiketi wapi",
        "i would like to order": "ningependa kuagiza",
        "the bill please": "hesabu tafadhali",
        "i have a reservation": "nina nafasi iliyowekwa",
        "is there wifi": "kuna Wi-Fi",
        "i need a doctor": "nahitaji daktari",
        "call the police": "piga polisi",
        "i am lost": "nimepotea",
        "what do you recommend": "unapendekeza nini",
        "i am just looking": "natazama tu",
        "how long will it take": "itachukua muda gani",
        "can i pay by card": "naweza kulipa kwa kadi",
        "i do not eat meat": "sili nyama",
        "this is delicious": "hii ni tamu",
        "see you later": "tutaonana baadaye",
    },
    "es": {
        "good morning": "buenos días", "good afternoon": "buenas tardes", "good evening": "buenas noches",
        "good night": "buenas noches", "how are you": "¿cómo estás?", "i am fine": "estoy bien",
        "thank you very much": "muchas gracias", "you are welcome": "de nada", "please help me": "por favor, ayúdame",
        "i need help": "necesito ayuda", "i do not understand": "no entiendo", "please speak slowly": "por favor, habla despacio",
        "where is the bathroom": "¿dónde está el baño?", "how much does it cost": "¿cuánto cuesta?", "i would like some water": "quisiera un poco de agua",
        "i am hungry": "tengo hambre", "the food is delicious": "la comida está deliciosa", "i am sorry": "lo siento",
        "what time is it": "¿qué hora es?", "have a nice day": "que tengas un buen día", "see you soon": "hasta pronto",
        "i love you": "te quiero", "i like coding": "me gusta programar", "i love coding": "me encanta programar",
        "i am learning to code": "estoy aprendiendo a programar", "i am a software developer": "soy desarrollador de software",
        "i am working from home": "trabajo desde casa", "i will call you later": "te llamaré más tarde", "everything is ready": "todo está listo",
        "let us go": "vámonos", "come and eat": "ven a comer", "come eat": "ven a comer", "come and have some food": "ven a comer algo", "please come and have some food": "por favor, ven a comer algo", "come and drink": "ven a beber", "go and eat": "ve a comer", "eat and drink": "come y bebe", "please come and eat": "por favor, ven a comer", "wait a moment": "espera un momento", "good luck": "buena suerte", "can you repeat that": "¿puedes repetir eso?", "please write it down": "por favor, escríbelo", "do you speak english": "¿hablas inglés?", "i am looking for the hotel": "busco el hotel", "where can i buy a ticket": "¿dónde puedo comprar un billete?", "i would like to order": "quisiera pedir", "the bill please": "la cuenta, por favor", "i have a reservation": "tengo una reserva", "is there wifi": "¿hay wifi?", "i need a doctor": "necesito un médico", "i am lost": "estoy perdido", "what do you recommend": "¿qué recomiendas?", "i am just looking": "solo estoy mirando", "how long will it take": "¿cuánto tardará?", "can i pay by card": "¿puedo pagar con tarjeta?", "i do not eat meat": "no como carne", "this is delicious": "esto está delicioso", "see you later": "hasta luego",
    },
    "fr": {
        "good morning": "bonjour", "good afternoon": "bon après-midi", "good evening": "bonsoir", "good night": "bonne nuit",
        "how are you": "comment allez-vous", "i am fine": "je vais bien", "thank you very much": "merci beaucoup", "you are welcome": "de rien",
        "please help me": "aidez-moi, s'il vous plaît", "i need help": "j'ai besoin d'aide", "i do not understand": "je ne comprends pas",
        "please speak slowly": "parlez lentement, s'il vous plaît", "where is the bathroom": "où sont les toilettes ?", "how much does it cost": "combien ça coûte ?",
        "i would like some water": "je voudrais de l'eau", "i am hungry": "j'ai faim", "the food is delicious": "la nourriture est délicieuse",
        "i am sorry": "je suis désolé", "what time is it": "quelle heure est-il ?", "have a nice day": "bonne journée", "see you soon": "à bientôt",
        "i love you": "je t'aime", "i like coding": "j'aime programmer", "i love coding": "j'adore programmer", "i am learning to code": "j'apprends à programmer",
        "i am a software developer": "je suis développeur de logiciels", "i am working from home": "je travaille à domicile", "everything is ready": "tout est prêt",
        "let us go": "allons-y", "come and eat": "viens manger", "come eat": "viens manger", "come and have some food": "viens manger quelque chose", "please come and have some food": "viens manger quelque chose, s'il te plaît", "come and drink": "viens boire", "go and eat": "va manger", "eat and drink": "mange et bois", "please come and eat": "viens manger, s'il te plaît", "wait a moment": "attendez un instant", "good luck": "bonne chance",
    },
    "de": {
        "good morning": "guten Morgen", "good afternoon": "guten Tag", "good evening": "guten Abend", "good night": "gute Nacht",
        "how are you": "wie geht es dir", "i am fine": "mir geht es gut", "thank you very much": "vielen Dank", "you are welcome": "gern geschehen",
        "please help me": "bitte helfen Sie mir", "i need help": "ich brauche Hilfe", "i do not understand": "ich verstehe nicht", "please speak slowly": "bitte sprechen Sie langsam",
        "where is the bathroom": "wo ist die Toilette?", "how much does it cost": "wie viel kostet das?", "i would like some water": "ich möchte etwas Wasser",
        "i am hungry": "ich habe Hunger", "the food is delicious": "das Essen ist köstlich", "i am sorry": "es tut mir leid", "what time is it": "wie spät ist es?",
        "have a nice day": "einen schönen Tag noch", "see you soon": "bis bald", "i love you": "ich liebe dich", "i like coding": "ich programmiere gerne",
        "i love coding": "ich liebe das Programmieren", "i am learning to code": "ich lerne programmieren", "i am a software developer": "ich bin Softwareentwickler",
        "i am working from home": "ich arbeite von zu Hause", "everything is ready": "alles ist bereit",         "let us go": "lass uns gehen", "come and eat": "komm essen", "come eat": "komm essen", "come and have some food": "komm etwas essen", "please come and have some food": "komm bitte etwas essen", "come and drink": "komm trinken", "go and eat": "geh essen", "eat and drink": "iss und trink", "please come and eat": "komm bitte essen", "wait a moment": "warte einen Moment", "good luck": "viel Glück",
    },
    "it": {
        "good morning": "buongiorno", "good afternoon": "buon pomeriggio", "good evening": "buonasera", "good night": "buonanotte",
        "how are you": "come stai", "i am fine": "sto bene", "thank you very much": "grazie mille", "you are welcome": "prego",
        "please help me": "aiutami, per favore", "i need help": "ho bisogno di aiuto", "i do not understand": "non capisco", "please speak slowly": "parla lentamente, per favore",
        "where is the bathroom": "dov'è il bagno?", "how much does it cost": "quanto costa?", "i would like some water": "vorrei dell'acqua",
        "i am hungry": "ho fame", "the food is delicious": "il cibo è delizioso", "i am sorry": "mi dispiace", "what time is it": "che ore sono?",
        "have a nice day": "buona giornata", "see you soon": "a presto", "i love you": "ti amo", "i like coding": "mi piace programmare",
        "i love coding": "adoro programmare", "i am learning to code": "sto imparando a programmare", "i am a software developer": "sono uno sviluppatore software",
        "i am working from home": "lavoro da casa", "everything is ready": "è tutto pronto",         "let us go": "andiamo", "come and eat": "vieni a mangiare", "come eat": "vieni a mangiare", "come and have some food": "vieni a mangiare qualcosa", "please come and have some food": "vieni a mangiare qualcosa, per favore", "come and drink": "vieni a bere", "go and eat": "vai a mangiare", "eat and drink": "mangia e bevi", "please come and eat": "vieni a mangiare, per favore", "wait a moment": "aspetta un momento", "good luck": "buona fortuna",
    },
}

# The categories make the local fallback easy to extend and cover grammar
# words as well as everyday vocabulary. Keys are English source words.
COMMON = {
    "pronouns": "i you he she we they me him her us them my your his our their this that these those",
    "prepositions": "and or but because if with without for from to in on under near before after about between through",
    "verbs": "be am is are was were have has do does can will want need like love go come eat drink see know understand speak write read learn work call help wait start finish make use find give take tell ask think feel live play try remember",
    "nouns": "hello goodbye please thanks yes no friend family person people child man woman name home house school office work book meeting message phone computer code coding language word sentence question answer water food coffee money time day morning night place city country road station bathroom job teacher student idea story problem solution",
    "adjectives": "good bad new old big small easy difficult important ready happy sad beautiful fast slow hot cold clean busy free safe useful different same better best true open closed kind young long short early late",
    "other": "very more most now today tomorrow later here there not never always also really",
}

TRANSLATIONS = {
    "sw": "mimi wewe yeye yeye sisi wao mimi yeye yeye sisi wao yangu yako yake yetu yao hii hiyo hizi hizo na au lakini kwa sababu ikiwa na bila kwa kutoka kwa katika juu ya chini ya karibu na kabla ya baada ya kuhusu kati ya kupitia kuwa ni ni ni alikuwa walikuwa kuwa na ana fanya anafanya weza nitakuwa taka hitaji penda penda enda kuja kula kunywa ona jua elewa zungumza andika soma jifunza fanya kazi piga simu saidia subiri anza maliza tengeneza tumia tafuta toa chukua ambia uliza fikiri hisi ishi cheza jaribu kumbuka habari kwaheri tafadhali asante ndiyo hapana rafiki familia mtu watu mtoto mwanaume mwanamke jina nyumbani nyumba shule ofisi kazi kitabu mkutano ujumbe simu kompyuta msimbo kuandika msimbo lugha neno sentensi swali jibu maji chakula kahawa pesa wakati siku asubuhi usiku mahali jiji nchi barabara kituo choo kazi mwalimu mwanafunzi wazo hadithi tatizo suluhisho nzuri mbaya mpya zamani kubwa ndogo rahisi ngumu muhimu tayari furaha huzuni nzuri haraka polepole moto baridi safi mwenye shughuli huru salama muhimu tofauti sawa bora bora kweli wazi imefungwa mkarimu mchanga ndefu fupi mapema kuchelewa sana zaidi zaidi sasa leo kesho baadaye hapa huko si kamwe kila mara pia kweli",
    "es": "yo tú él ella nosotros ellos me él ella nosotros ellos mi tu su nuestro su esto eso estos esos y o pero porque si con sin para de a en sobre debajo de cerca de antes de después de sobre entre a través de ser soy es son era eran tener tiene hacer hace poder querer necesitar gustar amar ir venir comer beber ver saber entender hablar escribir leer aprender trabajar llamar ayudar esperar empezar terminar hacer usar encontrar dar tomar decir preguntar pensar sentir vivir jugar intentar recordar hola adiós por favor gracias sí no amigo familia persona gente niño hombre mujer nombre casa casa escuela oficina trabajo libro reunión mensaje teléfono computadora código programar idioma palabra oración pregunta respuesta agua comida café dinero tiempo día mañana noche lugar ciudad país camino estación baño empleo profesor estudiante idea historia problema solución bueno malo nuevo viejo grande pequeño fácil difícil importante listo feliz triste hermoso rápido lento caliente frío limpio ocupado libre seguro útil diferente mismo mejor mejor verdadero abierto cerrado amable joven largo corto temprano tarde muy más la mayoría ahora hoy mañana después aquí allí no nunca siempre también realmente",
    "fr": "je vous il elle nous ils me lui elle nous eux mon votre son notre leur ceci cela ceux celles et ou mais parce que si avec sans pour de à dans sur sous près de avant après au sujet de entre à travers être suis est sont était étaient avoir a faire fait pouvoir vouloir avoir besoin aimer aimer aller venir manger boire voir savoir comprendre parler écrire lire apprendre travailler appeler aider attendre commencer finir faire utiliser trouver donner prendre dire demander penser sentir vivre jouer essayer se souvenir bon mauvais nouveau vieux grand petit facile difficile important prêt heureux triste beau rapide lent chaud froid propre occupé libre sûr utile différent même meilleur meilleur vrai ouvert fermé gentil jeune long court tôt tard très plus la plupart maintenant aujourd'hui demain plus tard ici là ne jamais toujours aussi vraiment bonjour au revoir s'il vous plaît merci oui non ami famille personne gens enfant homme femme nom maison maison école bureau travail livre réunion message téléphone ordinateur code programmer langue mot phrase question réponse eau nourriture café argent temps jour matin nuit endroit ville pays route gare toilettes emploi professeur étudiant idée histoire problème solution",
    "de": "ich du er sie wir sie mich ihn ihr uns sie mein dein sein unser ihr dies das diese jene und oder aber weil wenn mit ohne für von zu in auf unter nahe vor nach über zwischen durch sein bin ist sind war waren haben hat tun tut können wollen brauchen mögen lieben gehen kommen essen trinken sehen wissen verstehen sprechen schreiben lesen lernen arbeiten anrufen helfen warten beginnen beenden machen benutzen finden geben nehmen sagen fragen denken fühlen leben spielen versuchen erinnern hallo auf Wiedersehen bitte danke ja nein Freund Familie Person Menschen Kind Mann Frau Name Zuhause Haus Schule Büro Arbeit Buch Treffen Nachricht Telefon Computer Code programmieren Sprache Wort Satz Frage Antwort Wasser Essen Kaffee Geld Zeit Tag Morgen Nacht Ort Stadt Land Straße Bahnhof Toilette Beruf Lehrer Schüler Idee Geschichte Problem Lösung gut schlecht neu alt groß klein einfach schwierig wichtig bereit glücklich traurig schön schnell langsam heiß kalt sauber beschäftigt frei sicher nützlich anders gleich besser beste wahr offen geschlossen freundlich jung lang kurz früh spät sehr mehr am meisten jetzt heute morgen später hier dort nicht nie immer auch wirklich",
    "it": "io tu lui lei noi loro me lui lei noi loro mio tuo suo nostro loro questo quello questi quelli e o ma perché se con senza per da a in su sotto vicino prima dopo riguardo tra attraverso essere sono è sono era erano avere ha fare fa potere volere avere bisogno piacere amare andare venire mangiare bere vedere sapere capire parlare scrivere leggere imparare lavorare chiamare aiutare aspettare iniziare finire fare usare trovare dare prendere dire chiedere pensare sentire vivere giocare provare ricordare ciao arrivederci per favore grazie sì no amico famiglia persona persone bambino uomo donna nome casa casa scuola ufficio lavoro libro riunione messaggio telefono computer codice programmare lingua parola frase domanda risposta acqua cibo caffè denaro tempo giorno mattina notte posto città paese strada stazione bagno lavoro insegnante studente idea storia problema soluzione buono cattivo nuovo vecchio grande piccolo facile difficile importante pronto felice triste bello veloce lento caldo freddo pulito occupato libero sicuro utile diverso stesso migliore migliore vero aperto chiuso gentile giovane lungo corto presto tardi molto più maggior parte ora oggi domani dopo qui lì non mai sempre anche davvero",
}


# Additional everyday phrases are kept separate from the grammar maps so complete
# expressions always win over word-by-word translation.
MULTILINGUAL_PHRASES = {
    "sw": {
        "come and eat": "njoo ule", "come eat": "njoo ule", "please come and eat": "tafadhali njoo ule",
        "come and drink": "njoo unywe", "come and sit down": "njoo ukae", "go and eat": "enda ule",
        "eat and drink": "kula na kunywa", "welcome home": "karibu nyumbani", "see you tomorrow": "tutaonana kesho",
        "what is your name": "jina lako nani", "my name is": "jina langu ni", "where are you going": "unaenda wapi",
        "what are you doing": "unafanya nini", "i need help": "nahitaji msaada", "can you help me": "unaweza kunisaidia",
        "i do not know": "sijui", "i understand": "ninaelewa", "i do not understand": "sielewi",
        "have a nice day": "uwe na siku njema", "good night": "usiku mwema", "how much is this": "hii ni bei gani",
        "where is the bathroom": "choo kiko wapi", "i am hungry": "nina njaa", "i am thirsty": "nina kiu",
        "i love you": "nakupenda", "thank you very much": "asante sana", "you are welcome": "karibu",
        "please wait": "tafadhali subiri", "wait a moment": "subiri kidogo", "let us go": "twende"
    },
    "es": {
        "come and eat": "ven a comer", "come eat": "ven a comer", "please come and eat": "por favor, ven a comer",
        "come and drink": "ven a beber", "come and sit down": "ven a sentarte", "go and eat": "ve a comer",
        "eat and drink": "come y bebe", "welcome home": "bienvenido a casa", "see you tomorrow": "nos vemos mañana",
        "what is your name": "¿cómo te llamas?", "my name is": "me llamo", "where are you going": "¿adónde vas?",
        "what are you doing": "¿qué estás haciendo?", "i need help": "necesito ayuda", "can you help me": "¿puedes ayudarme?",
        "i do not know": "no lo sé", "i understand": "entiendo", "i do not understand": "no entiendo",
        "have a nice day": "que tengas un buen día", "good night": "buenas noches", "how much is this": "¿cuánto cuesta esto?",
        "where is the bathroom": "¿dónde está el baño?", "i am hungry": "tengo hambre", "i am thirsty": "tengo sed",
        "i love you": "te quiero", "thank you very much": "muchas gracias", "you are welcome": "de nada",
        "please wait": "por favor, espera", "wait a moment": "espera un momento", "let us go": "vámonos"
    },
    "fr": {
        "come and eat": "viens manger", "come eat": "viens manger", "please come and eat": "viens manger, s'il te plaît",
        "come and drink": "viens boire", "come and sit down": "viens t'asseoir", "go and eat": "va manger",
        "eat and drink": "mange et bois", "welcome home": "bienvenue à la maison", "see you tomorrow": "à demain",
        "what is your name": "comment t'appelles-tu ?", "my name is": "je m'appelle", "where are you going": "où vas-tu ?",
        "what are you doing": "qu'est-ce que tu fais ?", "i need help": "j'ai besoin d'aide", "can you help me": "peux-tu m'aider ?",
        "i do not know": "je ne sais pas", "i understand": "je comprends", "i do not understand": "je ne comprends pas",
        "have a nice day": "bonne journée", "good night": "bonne nuit", "how much is this": "combien ça coûte ?",
        "where is the bathroom": "où sont les toilettes ?", "i am hungry": "j'ai faim", "i am thirsty": "j'ai soif",
        "i love you": "je t'aime", "thank you very much": "merci beaucoup", "you are welcome": "de rien",
        "please wait": "attends, s'il te plaît", "wait a moment": "attends un instant", "let us go": "allons-y"
    },
    "de": {
        "come and eat": "komm essen", "come eat": "komm essen", "please come and eat": "komm bitte essen",
        "come and drink": "komm trinken", "come and sit down": "komm und setz dich", "go and eat": "geh essen",
        "eat and drink": "iss und trink", "welcome home": "willkommen zu Hause", "see you tomorrow": "bis morgen",
        "what is your name": "wie heißt du?", "my name is": "ich heiße", "where are you going": "wo gehst du hin?",
        "what are you doing": "was machst du?", "i need help": "ich brauche Hilfe", "can you help me": "kannst du mir helfen?",
        "i do not know": "ich weiß es nicht", "i understand": "ich verstehe", "i do not understand": "ich verstehe nicht",
        "have a nice day": "einen schönen Tag noch", "good night": "gute Nacht", "how much is this": "wie viel kostet das?",
        "where is the bathroom": "wo ist die Toilette?", "i am hungry": "ich habe Hunger", "i am thirsty": "ich habe Durst",
        "i love you": "ich liebe dich", "thank you very much": "vielen Dank", "you are welcome": "gern geschehen",
        "please wait": "warte bitte", "wait a moment": "warte einen Moment", "let us go": "lass uns gehen"
    },
    "it": {
        "come and eat": "vieni a mangiare", "come eat": "vieni a mangiare", "please come and eat": "vieni a mangiare, per favore",
        "come and drink": "vieni a bere", "come and sit down": "vieni a sederti", "go and eat": "vai a mangiare",
        "eat and drink": "mangia e bevi", "welcome home": "benvenuto a casa", "see you tomorrow": "a domani",
        "what is your name": "come ti chiami?", "my name is": "mi chiamo", "where are you going": "dove vai?",
        "what are you doing": "cosa stai facendo?", "i need help": "ho bisogno di aiuto", "can you help me": "puoi aiutarmi?",
        "i do not know": "non lo so", "i understand": "capisco", "i do not understand": "non capisco",
        "have a nice day": "buona giornata", "good night": "buonanotte", "how much is this": "quanto costa questo?",
        "where is the bathroom": "dov'è il bagno?", "i am hungry": "ho fame", "i am thirsty": "ho sete",
        "i love you": "ti amo", "thank you very much": "grazie mille", "you are welcome": "prego",
        "please wait": "aspetta, per favore", "wait a moment": "aspetta un momento", "let us go": "andiamo"
    }
}

# A broad, stable vocabulary fallback for sentences not found in the phrasebook.
MULTILINGUAL_WORDS = {
    "sw": {"please":"tafadhali","hello":"habari","goodbye":"kwaheri","i":"mimi","you":"wewe","he":"yeye","she":"yeye","we":"sisi","they":"wao","my":"yangu","your":"yako","our":"yetu","and":"na","or":"au","but":"lakini","because":"kwa sababu","with":"na","without":"bila","from":"kutoka","to":"kwa","in":"katika","on":"juu ya","under":"chini ya","near":"karibu na","before":"kabla ya","after":"baada ya","be":"kuwa","am":"ni","is":"ni","are":"ni","have":"kuwa na","do":"fanya","can":"weza","want":"taka","need":"hitaji","like":"penda","love":"penda","go":"enda","come":"kuja","eat":"kula","drink":"kunywa","see":"ona","know":"jua","understand":"elewa","speak":"zungumza","write":"andika","read":"soma","learn":"jifunza","work":"fanya kazi","help":"saidia","find":"tafuta","give":"toa","take":"chukua","think":"fikiri","feel":"hisi","friend":"rafiki","family":"familia","person":"mtu","people":"watu","child":"mtoto","man":"mwanaume","woman":"mwanamke","name":"jina","home":"nyumbani","house":"nyumba","school":"shule","office":"ofisi","work":"kazi","book":"kitabu","message":"ujumbe","phone":"simu","computer":"kompyuta","code":"msimbo","coding":"kuandika msimbo","language":"lugha","word":"neno","sentence":"sentensi","question":"swali","answer":"jibu","water":"maji","food":"chakula","coffee":"kahawa","money":"pesa","time":"wakati","day":"siku","morning":"asubuhi","night":"usiku","place":"mahali","city":"jiji","country":"nchi","good":"nzuri","bad":"mbaya","new":"mpya","old":"zamani","big":"kubwa","small":"ndogo","easy":"rahisi","difficult":"ngumu","important":"muhimu","ready":"tayari","happy":"furaha","sad":"huzuni","beautiful":"nzuri","fast":"haraka","slow":"polepole","hot":"moto","cold":"baridi","clean":"safi","busy":"mwenye shughuli","safe":"salama","different":"tofauti","same":"sawa","better":"bora","true":"kweli","open":"wazi","closed":"imefungwa","young":"mchanga","long":"ndefu","short":"fupi","early":"mapema","late":"kuchelewa"},
    "es": {"please":"por favor","hello":"hola","goodbye":"adiós","i":"yo","you":"tú","he":"él","she":"ella","we":"nosotros","they":"ellos","my":"mi","your":"tu","our":"nuestro","and":"y","or":"o","but":"pero","because":"porque","with":"con","without":"sin","from":"de","to":"a","in":"en","on":"sobre","under":"debajo de","near":"cerca de","before":"antes de","after":"después de","be":"ser","am":"soy","is":"es","are":"son","have":"tener","do":"hacer","can":"poder","want":"querer","need":"necesitar","like":"gustar","love":"amar","go":"ir","come":"venir","eat":"comer","drink":"beber","see":"ver","know":"saber","understand":"entender","speak":"hablar","write":"escribir","read":"leer","learn":"aprender","work":"trabajar","help":"ayudar","find":"encontrar","give":"dar","take":"tomar","think":"pensar","feel":"sentir","friend":"amigo","family":"familia","person":"persona","people":"gente","child":"niño","man":"hombre","woman":"mujer","name":"nombre","home":"casa","house":"casa","school":"escuela","office":"oficina","book":"libro","message":"mensaje","phone":"teléfono","computer":"computadora","code":"código","coding":"programar","language":"idioma","word":"palabra","sentence":"oración","question":"pregunta","answer":"respuesta","water":"agua","food":"comida","coffee":"café","money":"dinero","time":"tiempo","day":"día","morning":"mañana","night":"noche","place":"lugar","city":"ciudad","country":"país","good":"bueno","bad":"malo","new":"nuevo","old":"viejo","big":"grande","small":"pequeño","easy":"fácil","difficult":"difícil","important":"importante","ready":"listo","happy":"feliz","sad":"triste","beautiful":"hermoso","fast":"rápido","slow":"lento","hot":"caliente","cold":"frío","clean":"limpio","busy":"ocupado","safe":"seguro","different":"diferente","same":"mismo","better":"mejor","true":"verdadero","open":"abierto","closed":"cerrado","young":"joven","long":"largo","short":"corto","early":"temprano","late":"tarde"}
}

# Use the existing explicit maps as the base, then enrich them with the stable
# additions above. This keeps all earlier translations backward compatible.
EXPLICIT_WORDS = {
    "sw": {
        "i": "mimi", "you": "wewe", "he": "yeye", "she": "yeye", "we": "sisi", "they": "wao", "me": "mimi", "him": "yeye", "her": "yeye", "us": "sisi", "them": "wao", "my": "yangu", "your": "yako", "his": "yake", "our": "yetu", "their": "yao",
        "and": "na", "or": "au", "but": "lakini", "because": "kwa sababu", "if": "ikiwa", "with": "na", "without": "bila", "for": "kwa", "from": "kutoka", "to": "kwa", "in": "katika", "on": "juu ya", "under": "chini ya", "near": "karibu na", "before": "kabla ya", "after": "baada ya", "about": "kuhusu", "between": "kati ya", "through": "kupitia",
        "be": "kuwa", "am": "ni", "is": "ni", "are": "ni", "was": "alikuwa", "were": "walikuwa", "have": "kuwa na", "has": "ana", "do": "fanya", "can": "weza", "will": "takuwa", "want": "taka", "need": "hitaji", "like": "penda", "love": "penda", "go": "enda", "come": "kuja", "eat": "kula", "drink": "kunywa", "see": "ona", "know": "jua", "understand": "elewa", "speak": "zungumza", "write": "andika", "read": "soma", "learn": "jifunza", "work": "fanya kazi", "help": "saidia", "find": "tafuta", "give": "toa", "take": "chukua", "think": "fikiri", "feel": "hisi",
        "friend": "rafiki", "family": "familia", "person": "mtu", "people": "watu", "child": "mtoto", "name": "jina", "home": "nyumbani", "house": "nyumba", "school": "shule", "office": "ofisi", "meeting": "mkutano", "message": "ujumbe", "phone": "simu", "computer": "kompyuta", "code": "msimbo", "coding": "kuandika msimbo", "language": "lugha", "word": "neno", "sentence": "sentensi", "question": "swali", "answer": "jibu", "water": "maji", "food": "chakula", "coffee": "kahawa", "money": "pesa", "time": "wakati", "day": "siku", "morning": "asubuhi", "night": "usiku", "city": "jiji", "country": "nchi",
        "good": "nzuri", "bad": "mbaya", "new": "mpya", "old": "zamani", "big": "kubwa", "small": "ndogo", "easy": "rahisi", "difficult": "ngumu", "important": "muhimu", "ready": "tayari", "happy": "furaha", "sad": "huzuni", "beautiful": "nzuri", "fast": "haraka", "slow": "polepole", "hot": "moto", "cold": "baridi", "clean": "safi", "busy": "mwenye shughuli", "safe": "salama", "different": "tofauti", "same": "sawa", "better": "bora", "true": "kweli", "open": "wazi", "closed": "imefungwa", "kind": "mkarimu", "young": "mchanga", "long": "ndefu", "short": "fupi", "early": "mapema", "late": "kuchelewa"
    },
    "es": {
        "i": "yo", "you": "tú", "he": "él", "she": "ella", "we": "nosotros", "they": "ellos", "me": "me", "him": "lo", "her": "la", "us": "nos", "them": "los", "my": "mi", "your": "tu", "his": "su", "our": "nuestro", "their": "su", "and": "y", "or": "o", "but": "pero", "because": "porque", "if": "si", "with": "con", "without": "sin", "for": "para", "from": "de", "to": "a", "in": "en", "on": "sobre", "under": "debajo de", "near": "cerca de", "before": "antes de", "after": "después de", "about": "sobre", "between": "entre", "through": "a través de",
        "be": "ser", "am": "soy", "is": "es", "are": "son", "have": "tener", "has": "tiene", "do": "hacer", "can": "poder", "will": "hará", "want": "querer", "need": "necesitar", "like": "gustar", "love": "amar", "go": "ir", "come": "venir", "eat": "comer", "drink": "beber", "see": "ver", "know": "saber", "understand": "entender", "speak": "hablar", "write": "escribir", "read": "leer", "learn": "aprender", "work": "trabajar", "help": "ayudar", "find": "encontrar", "give": "dar", "take": "tomar", "think": "pensar", "feel": "sentir",
        "friend": "amigo", "family": "familia", "person": "persona", "people": "gente", "child": "niño", "name": "nombre", "home": "casa", "house": "casa", "school": "escuela", "office": "oficina", "meeting": "reunión", "message": "mensaje", "phone": "teléfono", "computer": "computadora", "code": "código", "coding": "programar", "language": "idioma", "word": "palabra", "sentence": "oración", "question": "pregunta", "answer": "respuesta", "water": "agua", "food": "comida", "coffee": "café", "money": "dinero", "time": "tiempo", "day": "día", "morning": "mañana", "night": "noche", "city": "ciudad", "country": "país",
        "good": "bueno", "bad": "malo", "new": "nuevo", "old": "viejo", "big": "grande", "small": "pequeño", "easy": "fácil", "difficult": "difícil", "important": "importante", "ready": "listo", "happy": "feliz", "sad": "triste", "beautiful": "hermoso", "fast": "rápido", "slow": "lento", "hot": "caliente", "cold": "frío", "clean": "limpio", "busy": "ocupado", "safe": "seguro", "different": "diferente", "same": "mismo", "better": "mejor", "true": "verdadero", "open": "abierto", "closed": "cerrado", "kind": "amable", "young": "joven", "long": "largo", "short": "corto", "early": "temprano", "late": "tarde"
    },
    "fr": {
        "i": "je", "you": "vous", "he": "il", "she": "elle", "we": "nous", "they": "ils", "my": "mon", "your": "votre", "his": "son", "our": "notre", "their": "leur", "and": "et", "or": "ou", "but": "mais", "because": "parce que", "if": "si", "with": "avec", "without": "sans", "for": "pour", "from": "de", "to": "à", "in": "dans", "on": "sur", "under": "sous", "near": "près de", "before": "avant", "after": "après", "about": "au sujet de", "between": "entre", "through": "à travers", "be": "être", "am": "suis", "is": "est", "are": "sont", "have": "avoir", "has": "a", "can": "pouvoir", "want": "vouloir", "need": "avoir besoin", "like": "aimer", "love": "aimer", "go": "aller", "come": "venir", "eat": "manger", "drink": "boire", "see": "voir", "know": "savoir", "understand": "comprendre", "speak": "parler", "write": "écrire", "read": "lire", "learn": "apprendre", "work": "travailler", "help": "aider", "friend": "ami", "family": "famille", "person": "personne", "people": "gens", "child": "enfant", "name": "nom", "home": "maison", "school": "école", "office": "bureau", "meeting": "réunion", "message": "message", "phone": "téléphone", "computer": "ordinateur", "code": "code", "coding": "programmer", "language": "langue", "word": "mot", "sentence": "phrase", "question": "question", "answer": "réponse", "water": "eau", "food": "nourriture", "coffee": "café", "money": "argent", "time": "temps", "day": "jour", "morning": "matin", "night": "nuit", "city": "ville", "country": "pays", "good": "bon", "bad": "mauvais", "new": "nouveau", "old": "vieux", "big": "grand", "small": "petit", "easy": "facile", "difficult": "difficile", "important": "important", "ready": "prêt", "happy": "heureux", "sad": "triste", "beautiful": "beau", "fast": "rapide", "slow": "lent", "hot": "chaud", "cold": "froid", "clean": "propre", "busy": "occupé", "safe": "sûr", "different": "différent", "same": "même", "better": "meilleur", "true": "vrai", "open": "ouvert", "closed": "fermé", "kind": "gentil", "young": "jeune", "long": "long", "short": "court", "early": "tôt", "late": "tard"
    },
    "de": {
        "i": "ich", "you": "du", "he": "er", "she": "sie", "we": "wir", "they": "sie", "my": "mein", "your": "dein", "his": "sein", "our": "unser", "their": "ihr", "and": "und", "or": "oder", "but": "aber", "because": "weil", "if": "wenn", "with": "mit", "without": "ohne", "for": "für", "from": "von", "to": "zu", "in": "in", "on": "auf", "under": "unter", "near": "nahe", "before": "vor", "after": "nach", "about": "über", "between": "zwischen", "through": "durch", "be": "sein", "am": "bin", "is": "ist", "are": "sind", "have": "haben", "has": "hat", "can": "können", "want": "wollen", "need": "brauchen", "like": "mögen", "love": "lieben", "go": "gehen", "come": "kommen", "eat": "essen", "drink": "trinken", "see": "sehen", "know": "wissen", "understand": "verstehen", "speak": "sprechen", "write": "schreiben", "read": "lesen", "learn": "lernen", "work": "arbeiten", "help": "helfen", "friend": "Freund", "family": "Familie", "person": "Person", "people": "Menschen", "child": "Kind", "name": "Name", "home": "Zuhause", "school": "Schule", "office": "Büro", "meeting": "Treffen", "message": "Nachricht", "phone": "Telefon", "computer": "Computer", "code": "Code", "coding": "programmieren", "language": "Sprache", "word": "Wort", "sentence": "Satz", "question": "Frage", "answer": "Antwort", "water": "Wasser", "food": "Essen", "coffee": "Kaffee", "money": "Geld", "time": "Zeit", "day": "Tag", "morning": "Morgen", "night": "Nacht", "city": "Stadt", "country": "Land", "good": "gut", "bad": "schlecht", "new": "neu", "old": "alt", "big": "groß", "small": "klein", "easy": "einfach", "difficult": "schwierig", "important": "wichtig", "ready": "bereit", "happy": "glücklich", "sad": "traurig", "beautiful": "schön", "fast": "schnell", "slow": "langsam", "hot": "heiß", "cold": "kalt", "clean": "sauber", "busy": "beschäftigt", "safe": "sicher", "different": "anders", "same": "gleich", "better": "besser", "true": "wahr", "open": "offen", "closed": "geschlossen", "kind": "freundlich", "young": "jung", "long": "lang", "short": "kurz", "early": "früh", "late": "spät"
    },
    "it": {
        "i": "io", "you": "tu", "he": "lui", "she": "lei", "we": "noi", "they": "loro", "my": "mio", "your": "tuo", "his": "suo", "our": "nostro", "their": "loro", "and": "e", "or": "o", "but": "ma", "because": "perché", "if": "se", "with": "con", "without": "senza", "for": "per", "from": "da", "to": "a", "in": "in", "on": "su", "under": "sotto", "near": "vicino a", "before": "prima", "after": "dopo", "about": "riguardo a", "between": "tra", "through": "attraverso", "be": "essere", "am": "sono", "is": "è", "are": "sono", "have": "avere", "has": "ha", "can": "potere", "want": "volere", "need": "avere bisogno", "like": "piacere", "love": "amare", "go": "andare", "come": "venire", "eat": "mangiare", "drink": "bere", "see": "vedere", "know": "sapere", "understand": "capire", "speak": "parlare", "write": "scrivere", "read": "leggere", "learn": "imparare", "work": "lavorare", "help": "aiutare", "friend": "amico", "family": "famiglia", "person": "persona", "people": "persone", "child": "bambino", "name": "nome", "home": "casa", "school": "scuola", "office": "ufficio", "meeting": "riunione", "message": "messaggio", "phone": "telefono", "computer": "computer", "code": "codice", "coding": "programmare", "language": "lingua", "word": "parola", "sentence": "frase", "question": "domanda", "answer": "risposta", "water": "acqua", "food": "cibo", "coffee": "caffè", "money": "denaro", "time": "tempo", "day": "giorno", "morning": "mattina", "night": "notte", "city": "città", "country": "paese", "good": "buono", "bad": "cattivo", "new": "nuovo", "old": "vecchio", "big": "grande", "small": "piccolo", "easy": "facile", "difficult": "difficile", "important": "importante", "ready": "pronto", "happy": "felice", "sad": "triste", "beautiful": "bello", "fast": "veloce", "slow": "lento", "hot": "caldo", "cold": "freddo", "clean": "pulito", "busy": "occupato", "safe": "sicuro", "different": "diverso", "same": "stesso", "better": "migliore", "true": "vero", "open": "aperto", "closed": "chiuso", "kind": "gentile", "young": "giovane", "long": "lungo", "short": "corto", "early": "presto", "late": "tardi"
    },
}


# Categorized offline vocabulary. Complete phrases are handled separately below;
# these word maps provide dependable coverage when a sentence is not in the phrasebook.
CATEGORY_WORDS = {
    "sw": {
        "pronouns": {"i": "mimi", "you": "wewe", "he": "yeye", "she": "yeye", "we": "sisi", "they": "wao", "me": "mimi", "my": "yangu", "your": "yako", "our": "yetu", "their": "yao"},
        "verbs": {"be": "kuwa", "am": "ni", "is": "ni", "are": "ni", "have": "kuwa na", "do": "fanya", "can": "weza", "want": "taka", "need": "hitaji", "go": "enda", "come": "kuja", "eat": "kula", "drink": "kunywa", "learn": "jifunza", "work": "fanya kazi", "write": "andika", "read": "soma", "help": "saidia", "find": "tafuta", "give": "toa", "take": "chukua", "speak": "zungumza", "understand": "elewa"},
        "nouns": {"person": "mtu", "people": "watu", "family": "familia", "child": "mtoto", "friend": "rafiki", "name": "jina", "house": "nyumba", "home": "nyumbani", "school": "shule", "teacher": "mwalimu", "student": "mwanafunzi", "book": "kitabu", "water": "maji", "food": "chakula", "coffee": "kahawa", "language": "lugha", "word": "neno", "question": "swali", "answer": "jibu", "computer": "kompyuta", "phone": "simu", "code": "msimbo", "office": "ofisi", "job": "kazi", "city": "jiji", "country": "nchi", "road": "barabara", "hotel": "hoteli", "airport": "uwanja wa ndege", "time": "wakati", "day": "siku", "morning": "asubuhi", "evening": "jioni", "night": "usiku"},
        "prepositions": {"and": "na", "with": "na", "without": "bila", "for": "kwa", "from": "kutoka", "to": "kwa", "in": "katika", "on": "juu ya", "under": "chini ya", "near": "karibu na", "before": "kabla ya", "after": "baada ya", "between": "kati ya"},
        "conjunctions": {"and": "na", "or": "au", "but": "lakini", "because": "kwa sababu", "if": "ikiwa", "so": "kwa hiyo"},
        "adjectives": {"good": "nzuri", "bad": "mbaya", "new": "mpya", "old": "ya zamani", "big": "kubwa", "small": "ndogo", "easy": "rahisi", "difficult": "ngumu", "important": "muhimu", "happy": "furaha", "beautiful": "nzuri", "fast": "haraka", "slow": "polepole", "safe": "salama", "ready": "tayari"},
        "adverbs": {"very": "sana", "more": "zaidi", "now": "sasa", "today": "leo", "tomorrow": "kesho", "later": "baadaye", "here": "hapa", "there": "huko", "always": "kila mara", "never": "kamwe"},
        "food_drinks": {"breakfast": "kifungua kinywa", "lunch": "chakula cha mchana", "dinner": "chakula cha jioni", "bread": "mkate", "rice": "mchele", "meat": "nyama", "fruit": "matunda", "milk": "maziwa", "tea": "chai", "juice": "juisi"},
        "travel_places": {"station": "kituo", "bus": "basi", "train": "treni", "ticket": "tiketi", "map": "ramani", "bathroom": "choo", "market": "soko", "bank": "benki", "hospital": "hospitali", "restaurant": "mkahawa"},
    },
    "es": {"pronouns": {"i":"yo", "you":"tú", "he":"él", "she":"ella", "we":"nosotros", "they":"ellos", "my":"mi", "your":"tu", "our":"nuestro", "their":"su"}, "verbs": {"be":"ser", "am":"soy", "is":"es", "are":"son", "have":"tener", "do":"hacer", "can":"poder", "want":"querer", "need":"necesitar", "go":"ir", "come":"venir", "eat":"comer", "drink":"beber", "learn":"aprender", "work":"trabajar", "write":"escribir", "read":"leer", "help":"ayudar", "find":"encontrar", "give":"dar", "take":"tomar", "speak":"hablar", "understand":"entender"}, "nouns": {"person":"persona", "people":"gente", "family":"familia", "child":"niño", "friend":"amigo", "name":"nombre", "house":"casa", "home":"casa", "school":"escuela", "teacher":"profesor", "student":"estudiante", "book":"libro", "water":"agua", "food":"comida", "coffee":"café", "language":"idioma", "word":"palabra", "question":"pregunta", "answer":"respuesta", "computer":"computadora", "phone":"teléfono", "code":"código", "office":"oficina", "job":"trabajo", "city":"ciudad", "country":"país", "road":"carretera", "hotel":"hotel", "airport":"aeropuerto", "time":"tiempo", "day":"día", "morning":"mañana", "evening":"tarde", "night":"noche"}, "prepositions": {"with":"con", "without":"sin", "for":"para", "from":"de", "to":"a", "in":"en", "on":"sobre", "under":"debajo de", "near":"cerca de", "before":"antes de", "after":"después de", "between":"entre"}, "conjunctions": {"and":"y", "or":"o", "but":"pero", "because":"porque", "if":"si", "so":"así que"}, "adjectives": {"good":"bueno", "bad":"malo", "new":"nuevo", "old":"viejo", "big":"grande", "small":"pequeño", "easy":"fácil", "difficult":"difícil", "important":"importante", "happy":"feliz", "beautiful":"hermoso", "fast":"rápido", "slow":"lento", "safe":"seguro", "ready":"listo"}, "adverbs": {"very":"muy", "more":"más", "now":"ahora", "today":"hoy", "tomorrow":"mañana", "later":"después", "here":"aquí", "there":"allí", "always":"siempre", "never":"nunca"}, "food_drinks": {"breakfast":"desayuno", "lunch":"almuerzo", "dinner":"cena", "bread":"pan", "rice":"arroz", "meat":"carne", "fruit":"fruta", "milk":"leche", "tea":"té", "juice":"jugo"}, "travel_places": {"station":"estación", "bus":"autobús", "train":"tren", "ticket":"billete", "map":"mapa", "bathroom":"baño", "market":"mercado", "bank":"banco", "hospital":"hospital", "restaurant":"restaurante"}},
}

# The remaining languages use the same complete categorized structure, with
# natural everyday equivalents for the same high-value vocabulary.
CATEGORY_WORDS.update({
    "fr": {"pronouns": {"i":"je", "you":"vous", "he":"il", "she":"elle", "we":"nous", "they":"ils", "my":"mon", "your":"votre", "our":"notre", "their":"leur"}, "verbs": {"be":"être", "am":"suis", "is":"est", "are":"sont", "have":"avoir", "do":"faire", "can":"pouvoir", "want":"vouloir", "need":"avoir besoin", "go":"aller", "come":"venir", "eat":"manger", "drink":"boire", "learn":"apprendre", "work":"travailler", "write":"écrire", "read":"lire", "help":"aider", "find":"trouver", "give":"donner", "take":"prendre", "speak":"parler", "understand":"comprendre"}, "nouns": {"person":"personne", "people":"gens", "family":"famille", "child":"enfant", "friend":"ami", "name":"nom", "house":"maison", "home":"maison", "school":"école", "teacher":"professeur", "student":"étudiant", "book":"livre", "water":"eau", "food":"nourriture", "coffee":"café", "language":"langue", "word":"mot", "question":"question", "answer":"réponse", "computer":"ordinateur", "phone":"téléphone", "code":"code", "office":"bureau", "job":"emploi", "city":"ville", "country":"pays", "road":"route", "hotel":"hôtel", "airport":"aéroport", "time":"temps", "day":"jour", "morning":"matin", "evening":"soir", "night":"nuit"}, "prepositions": {"with":"avec", "without":"sans", "for":"pour", "from":"de", "to":"à", "in":"dans", "on":"sur", "under":"sous", "near":"près de", "before":"avant", "after":"après", "between":"entre"}, "conjunctions": {"and":"et", "or":"ou", "but":"mais", "because":"parce que", "if":"si", "so":"donc"}, "adjectives": {"good":"bon", "bad":"mauvais", "new":"nouveau", "old":"vieux", "big":"grand", "small":"petit", "easy":"facile", "difficult":"difficile", "important":"important", "happy":"heureux", "beautiful":"beau", "fast":"rapide", "slow":"lent", "safe":"sûr", "ready":"prêt"}, "adverbs": {"very":"très", "more":"plus", "now":"maintenant", "today":"aujourd'hui", "tomorrow":"demain", "later":"plus tard", "here":"ici", "there":"là", "always":"toujours", "never":"jamais"}, "food_drinks": {"breakfast":"petit-déjeuner", "lunch":"déjeuner", "dinner":"dîner", "bread":"pain", "rice":"riz", "meat":"viande", "fruit":"fruit", "milk":"lait", "tea":"thé", "juice":"jus"}, "travel_places": {"station":"gare", "bus":"bus", "train":"train", "ticket":"billet", "map":"carte", "bathroom":"toilettes", "market":"marché", "bank":"banque", "hospital":"hôpital", "restaurant":"restaurant"}},
    "de": {"pronouns": {"i":"ich", "you":"du", "he":"er", "she":"sie", "we":"wir", "they":"sie", "my":"mein", "your":"dein", "our":"unser", "their":"ihr"}, "verbs": {"be":"sein", "am":"bin", "is":"ist", "are":"sind", "have":"haben", "do":"tun", "can":"können", "want":"wollen", "need":"brauchen", "go":"gehen", "come":"kommen", "eat":"essen", "drink":"trinken", "learn":"lernen", "work":"arbeiten", "write":"schreiben", "read":"lesen", "help":"helfen", "find":"finden", "give":"geben", "take":"nehmen", "speak":"sprechen", "understand":"verstehen"}, "nouns": {"person":"Person", "people":"Menschen", "family":"Familie", "child":"Kind", "friend":"Freund", "name":"Name", "house":"Haus", "home":"Zuhause", "school":"Schule", "teacher":"Lehrer", "student":"Schüler", "book":"Buch", "water":"Wasser", "food":"Essen", "coffee":"Kaffee", "language":"Sprache", "word":"Wort", "question":"Frage", "answer":"Antwort", "computer":"Computer", "phone":"Telefon", "code":"Code", "office":"Büro", "job":"Beruf", "city":"Stadt", "country":"Land", "road":"Straße", "hotel":"Hotel", "airport":"Flughafen", "time":"Zeit", "day":"Tag", "morning":"Morgen", "evening":"Abend", "night":"Nacht"}, "prepositions": {"with":"mit", "without":"ohne", "for":"für", "from":"von", "to":"zu", "in":"in", "on":"auf", "under":"unter", "near":"nahe", "before":"vor", "after":"nach", "between":"zwischen"}, "conjunctions": {"and":"und", "or":"oder", "but":"aber", "because":"weil", "if":"wenn", "so":"also"}, "adjectives": {"good":"gut", "bad":"schlecht", "new":"neu", "old":"alt", "big":"groß", "small":"klein", "easy":"einfach", "difficult":"schwierig", "important":"wichtig", "happy":"glücklich", "beautiful":"schön", "fast":"schnell", "slow":"langsam", "safe":"sicher", "ready":"bereit"}, "adverbs": {"very":"sehr", "more":"mehr", "now":"jetzt", "today":"heute", "tomorrow":"morgen", "later":"später", "here":"hier", "there":"dort", "always":"immer", "never":"nie"}, "food_drinks": {"breakfast":"Frühstück", "lunch":"Mittagessen", "dinner":"Abendessen", "bread":"Brot", "rice":"Reis", "meat":"Fleisch", "fruit":"Obst", "milk":"Milch", "tea":"Tee", "juice":"Saft"}, "travel_places": {"station":"Bahnhof", "bus":"Bus", "train":"Zug", "ticket":"Fahrkarte", "map":"Karte", "bathroom":"Toilette", "market":"Markt", "bank":"Bank", "hospital":"Krankenhaus", "restaurant":"Restaurant"}},
    "it": {"pronouns": {"i":"io", "you":"tu", "he":"lui", "she":"lei", "we":"noi", "they":"loro", "my":"mio", "your":"tuo", "our":"nostro", "their":"loro"}, "verbs": {"be":"essere", "am":"sono", "is":"è", "are":"sono", "have":"avere", "do":"fare", "can":"potere", "want":"volere", "need":"avere bisogno", "go":"andare", "come":"venire", "eat":"mangiare", "drink":"bere", "learn":"imparare", "work":"lavorare", "write":"scrivere", "read":"leggere", "help":"aiutare", "find":"trovare", "give":"dare", "take":"prendere", "speak":"parlare", "understand":"capire"}, "nouns": {"person":"persona", "people":"persone", "family":"famiglia", "child":"bambino", "friend":"amico", "name":"nome", "house":"casa", "home":"casa", "school":"scuola", "teacher":"insegnante", "student":"studente", "book":"libro", "water":"acqua", "food":"cibo", "coffee":"caffè", "language":"lingua", "word":"parola", "question":"domanda", "answer":"risposta", "computer":"computer", "phone":"telefono", "code":"codice", "office":"ufficio", "job":"lavoro", "city":"città", "country":"paese", "road":"strada", "hotel":"hotel", "airport":"aeroporto", "time":"tempo", "day":"giorno", "morning":"mattina", "evening":"sera", "night":"notte"}, "prepositions": {"with":"con", "without":"senza", "for":"per", "from":"da", "to":"a", "in":"in", "on":"su", "under":"sotto", "near":"vicino a", "before":"prima", "after":"dopo", "between":"tra"}, "conjunctions": {"and":"e", "or":"o", "but":"ma", "because":"perché", "if":"se", "so":"quindi"}, "adjectives": {"good":"buono", "bad":"cattivo", "new":"nuovo", "old":"vecchio", "big":"grande", "small":"piccolo", "easy":"facile", "difficult":"difficile", "important":"importante", "happy":"felice", "beautiful":"bello", "fast":"veloce", "slow":"lento", "safe":"sicuro", "ready":"pronto"}, "adverbs": {"very":"molto", "more":"più", "now":"ora", "today":"oggi", "tomorrow":"domani", "later":"dopo", "here":"qui", "there":"lì", "always":"sempre", "never":"mai"}, "food_drinks": {"breakfast":"colazione", "lunch":"pranzo", "dinner":"cena", "bread":"pane", "rice":"riso", "meat":"carne", "fruit":"frutta", "milk":"latte", "tea":"tè", "juice":"succo"}, "travel_places": {"station":"stazione", "bus":"autobus", "train":"treno", "ticket":"biglietto", "map":"mappa", "bathroom":"bagno", "market":"mercato", "bank":"banca", "hospital":"ospedale", "restaurant":"ristorante"}}
})


# Additional reverse phrase coverage for English-target translations. These
# entries use the foreign expression as the key and the English meaning as the
# value, so common phrases are recognized even when source detection is used.
REVERSE_EXTRA_PHRASES = {
    "sw": {
        "por favor": "please",
        "tafadhali": "please",
        "asante sana": "thank you very much",
        "habari yako": "how are you",
        "habari za asubuhi": "good morning",
        "usiku mwema": "good night",
        "njoo ule": "come and eat",
        "tafadhali njoo ule": "please come and eat",
        "njoo unywe": "come and drink",
        "enda ule": "go and eat",
        "kula na kunywa": "eat and drink",
        "jina lako nani": "what is your name",
        "unaenda wapi": "where are you going",
        "unafanya nini": "what are you doing",
        "unaweza kunisaidia": "can you help me",
        "nahitaji msaada": "i need help",
        "sielewi": "i do not understand",
        "ninaelewa": "i understand",
        "choo kiko wapi": "where is the bathroom",
        "nina njaa": "i am hungry",
        "nina kiu": "i am thirsty",
        "karibu": "you are welcome",
        "tafadhali subiri": "please wait",
        "subiri kidogo": "wait a moment",
        "twende": "let us go",
        "tutaonana kesho": "see you tomorrow",
        "ninafanya kazi kutoka nyumbani": "i am working from home",
    },
    "es": {
        "por favor": "please",
        "muchas gracias": "thank you very much",
        "buenos días": "good morning",
        "buenas noches": "good night",
        "ven a comer": "come and eat",
        "por favor, ven a comer": "please come and eat",
        "ven a beber": "come and drink",
        "ve a comer": "go and eat",
        "come y bebe": "eat and drink",
        "cómo te llamas": "what is your name",
        "adónde vas": "where are you going",
        "qué estás haciendo": "what are you doing",
        "puedes ayudarme": "can you help me",
        "necesito ayuda": "i need help",
        "no lo sé": "i do not know",
        "no entiendo": "i do not understand",
        "¿dónde está el baño?": "where is the bathroom",
        "tengo hambre": "i am hungry",
        "tengo sed": "i am thirsty",
        "de nada": "you are welcome",
        "por favor, espera": "please wait",
        "espera un momento": "wait a moment",
        "vámonos": "let us go",
        "nos vemos mañana": "see you tomorrow",
    },
    "fr": {
        "s'il vous plaît": "please",
        "merci beaucoup": "thank you very much",
        "bonjour": "hello",
        "bonne nuit": "good night",
        "viens manger": "come and eat",
        "viens manger, s'il te plaît": "please come and eat",
        "viens boire": "come and drink",
        "va manger": "go and eat",
        "mange et bois": "eat and drink",
        "comment t'appelles-tu": "what is your name",
        "où vas-tu": "where are you going",
        "qu'est-ce que tu fais": "what are you doing",
        "peux-tu m'aider": "can you help me",
        "j'ai besoin d'aide": "i need help",
        "je ne sais pas": "i do not know",
        "je ne comprends pas": "i do not understand",
        "où sont les toilettes": "where is the bathroom",
        "j'ai faim": "i am hungry",
        "j'ai soif": "i am thirsty",
        "de rien": "you are welcome",
        "attends un instant": "wait a moment",
        "allons-y": "let us go",
        "à demain": "see you tomorrow",
    },
    "de": {
        "bitte": "please",
        "vielen dank": "thank you very much",
        "guten morgen": "good morning",
        "gute nacht": "good night",
        "komm essen": "come and eat",
        "komm bitte essen": "please come and eat",
        "komm trinken": "come and drink",
        "geh essen": "go and eat",
        "iss und trink": "eat and drink",
        "wie heißt du": "what is your name",
        "wo gehst du hin": "where are you going",
        "was machst du": "what are you doing",
        "kannst du mir helfen": "can you help me",
        "ich brauche hilfe": "i need help",
        "ich weiß es nicht": "i do not know",
        "ich verstehe nicht": "i do not understand",
        "wo ist die toilette": "where is the bathroom",
        "ich habe hunger": "i am hungry",
        "ich habe durst": "i am thirsty",
        "gern geschehen": "you are welcome",
        "warte einen moment": "wait a moment",
        "lass uns gehen": "let us go",
        "bis morgen": "see you tomorrow",
    },
    "it": {
        "per favore": "please",
        "grazie mille": "thank you very much",
        "buongiorno": "good morning",
        "buonanotte": "good night",
        "vieni a mangiare": "come and eat",
        "vieni a mangiare, per favore": "please come and eat",
        "vieni a bere": "come and drink",
        "vai a mangiare": "go and eat",
        "mangia e bevi": "eat and drink",
        "come ti chiami": "what is your name",
        "dove vai": "where are you going",
        "cosa stai facendo": "what are you doing",
        "puoi aiutarmi": "can you help me",
        "ho bisogno di aiuto": "i need help",
        "non lo so": "i do not know",
        "non capisco": "i do not understand",
        "dov'è il bagno": "where is the bathroom",
        "ho fame": "i am hungry",
        "ho sete": "i am thirsty",
        "prego": "you are welcome",
        "aspetta un momento": "wait a moment",
        "andiamo": "let us go",
        "a domani": "see you tomorrow",
    },
}

# High-value complete expressions. These are checked before the categorized
# vocabulary so natural phrases such as “come and eat” stay intact.
CATEGORY_PHRASES = {
    "sw": {
        "come and eat": "njoo ule", "come eat": "njoo ule", "please come and eat": "tafadhali njoo ule", "come and drink": "njoo unywe", "go and eat": "enda ule", "eat and drink": "kula na kunywa", "what is your name": "jina lako nani", "where are you going": "unaenda wapi", "what are you doing": "unafanya nini", "can you help me": "unaweza kunisaidia", "i need help": "nahitaji msaada", "i understand": "ninaelewa", "i do not understand": "sielewi", "where is the bathroom": "choo kiko wapi", "how much does it cost": "inagharimu kiasi gani", "i am hungry": "nina njaa", "i am thirsty": "nina kiu", "thank you": "asante", "you are welcome": "karibu", "please wait": "tafadhali subiri", "let us go": "twende", "see you tomorrow": "tutaonana kesho", "good morning": "habari za asubuhi", "good night": "usiku mwema", "i am working from home": "ninafanya kazi kutoka nyumbani"
    },
    "es": {
        "come and eat": "ven a comer", "come eat": "ven a comer", "please come and eat": "por favor, ven a comer", "come and drink": "ven a beber", "go and eat": "ve a comer", "eat and drink": "come y bebe", "what is your name": "¿cómo te llamas?", "where are you going": "¿adónde vas?", "what are you doing": "¿qué estás haciendo?", "can you help me": "¿puedes ayudarme?", "i need help": "necesito ayuda", "i understand": "entiendo", "i do not understand": "no entiendo", "where is the bathroom": "¿dónde está el baño?", "how much does it cost": "¿cuánto cuesta?", "i am hungry": "tengo hambre", "i am thirsty": "tengo sed", "thank you": "gracias", "you are welcome": "de nada", "please wait": "por favor, espera", "let us go": "vámonos", "see you tomorrow": "nos vemos mañana", "good morning": "buenos días", "good night": "buenas noches", "i am working from home": "trabajo desde casa"
    },
    "fr": {
        "come and eat": "viens manger", "come eat": "viens manger", "please come and eat": "viens manger, s'il te plaît", "come and drink": "viens boire", "go and eat": "va manger", "eat and drink": "mange et bois", "what is your name": "comment t'appelles-tu ?", "where are you going": "où vas-tu ?", "what are you doing": "qu'est-ce que tu fais ?", "can you help me": "peux-tu m'aider ?", "i need help": "j'ai besoin d'aide", "i understand": "je comprends", "i do not understand": "je ne comprends pas", "where is the bathroom": "où sont les toilettes ?", "how much does it cost": "combien ça coûte ?", "i am hungry": "j'ai faim", "i am thirsty": "j'ai soif", "thank you": "merci", "you are welcome": "de rien", "please wait": "attends, s'il te plaît", "let us go": "allons-y", "see you tomorrow": "à demain", "good morning": "bonjour", "good night": "bonne nuit", "i am working from home": "je travaille à domicile"
    },
    "de": {
        "come and eat": "komm essen", "come eat": "komm essen", "please come and eat": "komm bitte essen", "come and drink": "komm trinken", "go and eat": "geh essen", "eat and drink": "iss und trink", "what is your name": "wie heißt du?", "where are you going": "wo gehst du hin?", "what are you doing": "was machst du?", "can you help me": "kannst du mir helfen?", "i need help": "ich brauche Hilfe", "i understand": "ich verstehe", "i do not understand": "ich verstehe nicht", "where is the bathroom": "wo ist die Toilette?", "how much does it cost": "wie viel kostet das?", "i am hungry": "ich habe Hunger", "i am thirsty": "ich habe Durst", "thank you": "danke", "you are welcome": "gern geschehen", "please wait": "warte bitte", "let us go": "lass uns gehen", "see you tomorrow": "bis morgen", "good morning": "guten Morgen", "good night": "gute Nacht", "i am working from home": "ich arbeite von zu Hause"
    },
    "it": {
        "come and eat": "vieni a mangiare", "come eat": "vieni a mangiare", "please come and eat": "vieni a mangiare, per favore", "come and drink": "vieni a bere", "go and eat": "vai a mangiare", "eat and drink": "mangia e bevi", "what is your name": "come ti chiami?", "where are you going": "dove vai?", "what are you doing": "cosa stai facendo?", "can you help me": "puoi aiutarmi?", "i need help": "ho bisogno di aiuto", "i understand": "capisco", "i do not understand": "non capisco", "where is the bathroom": "dov'è il bagno?", "how much does it cost": "quanto costa?", "i am hungry": "ho fame", "i am thirsty": "ho sete", "thank you": "grazie", "you are welcome": "prego", "please wait": "aspetta, per favore", "let us go": "andiamo", "see you tomorrow": "a domani", "good morning": "buongiorno", "good night": "buonanotte", "i am working from home": "lavoro da casa"
    }
}


# Extra high-frequency vocabulary used when a complete phrase is not available.
# Phrase dictionaries are still checked first, so natural expressions remain intact.
EXTENDED_WORDS = {
    "sw": {
        "a": "moja", "an": "moja", "the": "", "this": "hii", "that": "hiyo", "these": "hizi", "those": "hizo", "all": "zote", "some": "baadhi ya", "any": "yoyote", "each": "kila", "which": "gani", "who": "nani", "what": "nini", "where": "wapi", "when": "lini", "why": "kwa nini", "how": "vipi", "whose": "ya nani", "not": "si", "never": "kamwe", "again": "tena", "already": "tayari", "only": "tu", "also": "pia", "maybe": "labda", "please": "tafadhali", "thanks": "asante", "sorry": "samahani", "welcome": "karibu", "must": "lazima", "should": "inapaswa", "would": "ange", "could": "ingeweza", "make": "tengeneza", "start": "anza", "stop": "simama", "bring": "leta", "send": "tuma", "buy": "nunua", "sell": "uza", "pay": "lipa", "open": "fungua", "close": "funga", "show": "onyesha", "tell": "ambia", "ask": "uliza", "answer": "jibu", "remember": "kumbuka", "forget": "sahau", "play": "cheza", "try": "jaribu", "use": "tumia", "phone": "simu", "email": "barua pepe", "internet": "intaneti", "website": "tovuti", "file": "faili", "app": "programu", "screen": "skrini", "keyboard": "kibodi", "meeting": "mkutano", "project": "mradi", "team": "timu", "company": "kampuni", "customer": "mteja", "mother": "mama", "father": "baba", "brother": "kaka", "sister": "dada", "son": "mwana", "daughter": "binti", "parent": "mzazi", "baby": "mtoto mchanga", "teacher": "mwalimu", "student": "mwanafunzi", "class": "darasa", "lesson": "somo", "homework": "kazi ya nyumbani", "room": "chumba", "door": "mlango", "window": "dirisha", "bed": "kitanda", "chair": "kiti", "table": "meza", "kitchen": "jikoni", "market": "soko", "shop": "duka", "hotel": "hoteli", "airport": "uwanja wa ndege", "bus": "basi", "train": "treni", "ticket": "tiketi", "map": "ramani", "left": "kushoto", "right": "kulia", "breakfast": "kifungua kinywa", "lunch": "chakula cha mchana", "dinner": "chakula cha jioni", "bread": "mkate", "rice": "mchele", "meat": "nyama", "fruit": "matunda", "milk": "maziwa", "tea": "chai", "coffee": "kahawa", "juice": "juisi", "week": "wiki", "month": "mwezi", "year": "mwaka", "hour": "saa", "minute": "dakika", "soon": "hivi karibuni", "yesterday": "jana", "appointment": "miadi", "schedule": "ratiba", "today": "leo", "tomorrow": "kesho", "later": "baadaye"
    },
    "es": {
        "a": "un", "an": "un", "the": "el", "this": "esto", "that": "eso", "these": "estos", "those": "esos", "all": "todo", "some": "algún", "any": "cualquier", "each": "cada", "which": "cuál", "who": "quién", "what": "qué", "where": "dónde", "when": "cuándo", "why": "por qué", "how": "cómo", "whose": "de quién", "not": "no", "again": "otra vez", "already": "ya", "only": "solo", "also": "también", "maybe": "quizás", "sorry": "lo siento", "welcome": "bienvenido", "must": "deber", "should": "debería", "could": "podría", "make": "hacer", "start": "empezar", "stop": "parar", "bring": "traer", "send": "enviar", "buy": "comprar", "sell": "vender", "pay": "pagar", "open": "abrir", "close": "cerrar", "show": "mostrar", "tell": "decir", "ask": "preguntar", "remember": "recordar", "forget": "olvidar", "play": "jugar", "try": "intentar", "use": "usar", "email": "correo electrónico", "internet": "internet", "website": "sitio web", "file": "archivo", "app": "aplicación", "screen": "pantalla", "keyboard": "teclado", "meeting": "reunión", "project": "proyecto", "team": "equipo", "company": "empresa", "customer": "cliente", "mother": "madre", "father": "padre", "brother": "hermano", "sister": "hermana", "son": "hijo", "daughter": "hija", "parent": "padre", "baby": "bebé", "class": "clase", "lesson": "lección", "homework": "tarea", "room": "habitación", "door": "puerta", "window": "ventana", "bed": "cama", "chair": "silla", "table": "mesa", "kitchen": "cocina", "market": "mercado", "shop": "tienda", "hotel": "hotel", "airport": "aeropuerto", "bus": "autobús", "train": "tren", "ticket": "billete", "map": "mapa", "left": "izquierda", "right": "derecha", "breakfast": "desayuno", "lunch": "almuerzo", "dinner": "cena", "bread": "pan", "rice": "arroz", "meat": "carne", "fruit": "fruta", "milk": "leche", "tea": "té", "juice": "jugo", "week": "semana", "month": "mes", "year": "año", "hour": "hora", "minute": "minuto", "soon": "pronto", "yesterday": "ayer", "appointment": "cita", "schedule": "horario", "later": "más tarde"
    },
    "fr": {
        "a": "un", "an": "un", "the": "le", "this": "ceci", "that": "cela", "these": "ceux-ci", "those": "ceux-là", "all": "tout", "some": "quelque", "any": "n'importe quel", "each": "chaque", "which": "lequel", "who": "qui", "what": "quoi", "where": "où", "when": "quand", "why": "pourquoi", "how": "comment", "whose": "à qui", "not": "ne", "again": "encore", "already": "déjà", "only": "seulement", "also": "aussi", "maybe": "peut-être", "sorry": "désolé", "welcome": "bienvenue", "must": "devoir", "should": "devrait", "could": "pourrait", "make": "faire", "start": "commencer", "stop": "arrêter", "bring": "apporter", "send": "envoyer", "buy": "acheter", "sell": "vendre", "pay": "payer", "open": "ouvrir", "close": "fermer", "show": "montrer", "tell": "dire", "ask": "demander", "remember": "se souvenir", "forget": "oublier", "play": "jouer", "try": "essayer", "use": "utiliser", "email": "e-mail", "internet": "internet", "website": "site web", "file": "fichier", "app": "application", "screen": "écran", "keyboard": "clavier", "meeting": "réunion", "project": "projet", "team": "équipe", "company": "entreprise", "customer": "client", "mother": "mère", "father": "père", "brother": "frère", "sister": "sœur", "son": "fils", "daughter": "fille", "parent": "parent", "baby": "bébé", "class": "classe", "lesson": "leçon", "homework": "devoirs", "room": "chambre", "door": "porte", "window": "fenêtre", "bed": "lit", "chair": "chaise", "table": "table", "kitchen": "cuisine", "market": "marché", "shop": "magasin", "hotel": "hôtel", "airport": "aéroport", "bus": "bus", "train": "train", "ticket": "billet", "map": "carte", "left": "gauche", "right": "droite", "breakfast": "petit-déjeuner", "lunch": "déjeuner", "dinner": "dîner", "bread": "pain", "rice": "riz", "meat": "viande", "fruit": "fruit", "milk": "lait", "tea": "thé", "juice": "jus", "week": "semaine", "month": "mois", "year": "an", "hour": "heure", "minute": "minute", "soon": "bientôt", "yesterday": "hier", "appointment": "rendez-vous", "schedule": "emploi du temps", "later": "plus tard"
    },
    "de": {
        "a": "ein", "an": "ein", "the": "der", "this": "dies", "that": "das", "these": "diese", "those": "jene", "all": "alle", "some": "einige", "any": "irgendein", "each": "jeder", "which": "welcher", "who": "wer", "what": "was", "where": "wo", "when": "wann", "why": "warum", "how": "wie", "whose": "wessen", "not": "nicht", "again": "wieder", "already": "schon", "only": "nur", "also": "auch", "maybe": "vielleicht", "sorry": "Entschuldigung", "welcome": "willkommen", "must": "müssen", "should": "sollte", "could": "könnte", "make": "machen", "start": "beginnen", "stop": "stoppen", "bring": "bringen", "send": "senden", "buy": "kaufen", "sell": "verkaufen", "pay": "bezahlen", "open": "öffnen", "close": "schließen", "show": "zeigen", "tell": "sagen", "ask": "fragen", "remember": "sich erinnern", "forget": "vergessen", "play": "spielen", "try": "versuchen", "use": "benutzen", "email": "E-Mail", "internet": "Internet", "website": "Webseite", "file": "Datei", "app": "App", "screen": "Bildschirm", "keyboard": "Tastatur", "meeting": "Besprechung", "project": "Projekt", "team": "Team", "company": "Unternehmen", "customer": "Kunde", "mother": "Mutter", "father": "Vater", "brother": "Bruder", "sister": "Schwester", "son": "Sohn", "daughter": "Tochter", "parent": "Elternteil", "baby": "Baby", "class": "Klasse", "lesson": "Lektion", "homework": "Hausaufgaben", "room": "Zimmer", "door": "Tür", "window": "Fenster", "bed": "Bett", "chair": "Stuhl", "table": "Tisch", "kitchen": "Küche", "market": "Markt", "shop": "Geschäft", "hotel": "Hotel", "airport": "Flughafen", "bus": "Bus", "train": "Zug", "ticket": "Fahrkarte", "map": "Karte", "left": "links", "right": "rechts", "breakfast": "Frühstück", "lunch": "Mittagessen", "dinner": "Abendessen", "bread": "Brot", "rice": "Reis", "meat": "Fleisch", "fruit": "Obst", "milk": "Milch", "tea": "Tee", "juice": "Saft", "week": "Woche", "month": "Monat", "year": "Jahr", "hour": "Stunde", "minute": "Minute", "soon": "bald", "yesterday": "gestern", "appointment": "Termin", "schedule": "Zeitplan", "later": "später"
    },
    "it": {
        "a": "un", "an": "un", "the": "il", "this": "questo", "that": "quello", "these": "questi", "those": "quelli", "all": "tutto", "some": "alcuni", "any": "qualsiasi", "each": "ogni", "which": "quale", "who": "chi", "what": "cosa", "where": "dove", "when": "quando", "why": "perché", "how": "come", "whose": "di chi", "not": "non", "again": "di nuovo", "already": "già", "only": "solo", "also": "anche", "maybe": "forse", "sorry": "scusa", "welcome": "benvenuto", "must": "dovere", "should": "dovrebbe", "could": "potrebbe", "make": "fare", "start": "iniziare", "stop": "fermare", "bring": "portare", "send": "inviare", "buy": "comprare", "sell": "vendere", "pay": "pagare", "open": "aprire", "close": "chiudere", "show": "mostrare", "tell": "dire", "ask": "chiedere", "remember": "ricordare", "forget": "dimenticare", "play": "giocare", "try": "provare", "use": "usare", "email": "e-mail", "internet": "internet", "website": "sito web", "file": "file", "app": "applicazione", "screen": "schermo", "keyboard": "tastiera", "meeting": "riunione", "project": "progetto", "team": "squadra", "company": "azienda", "customer": "cliente", "mother": "madre", "father": "padre", "brother": "fratello", "sister": "sorella", "son": "figlio", "daughter": "figlia", "parent": "genitore", "baby": "bambino", "class": "classe", "lesson": "lezione", "homework": "compiti", "room": "stanza", "door": "porta", "window": "finestra", "bed": "letto", "chair": "sedia", "table": "tavolo", "kitchen": "cucina", "market": "mercato", "shop": "negozio", "hotel": "hotel", "airport": "aeroporto", "bus": "autobus", "train": "treno", "ticket": "biglietto", "map": "mappa", "left": "sinistra", "right": "destra", "breakfast": "colazione", "lunch": "pranzo", "dinner": "cena", "bread": "pane", "rice": "riso", "meat": "carne", "fruit": "frutta", "milk": "latte", "tea": "tè", "juice": "succo", "week": "settimana", "month": "mese", "year": "anno", "hour": "ora", "minute": "minuto", "soon": "presto", "yesterday": "ieri", "appointment": "appuntamento", "schedule": "programma", "later": "più tardi"
    }
}


def build_dictionary(target):
    if target == "en":
        return {word: word for group in COMMON.values() for word in group.split()}
    dictionary = dict(EXPLICIT_WORDS.get(target, {}))
    for category in CATEGORY_WORDS.get(target, {}).values():
        dictionary.update(category)
    dictionary.update(EXTENDED_WORDS.get(target, {}))
    return dictionary


def preserve_case(source, translated):
    if source.isupper():
        return translated.upper()
    if source[:1].isupper():
        return translated[:1].upper() + translated[1:]
    return translated


REVERSE_EXTRA_WORDS = {
    "sw": {
        "tafadhali": "please", "asante": "thank you", "samahani": "sorry", "karibu": "welcome",
        "mama": "mother", "baba": "father", "kaka": "brother", "dada": "sister", "mzazi": "parent",
        "chumba": "room", "mlango": "door", "dirisha": "window", "kitanda": "bed", "kiti": "chair", "meza": "table",
        "jikoni": "kitchen", "darasa": "class", "somo": "lesson", "mwalimu": "teacher", "mwanafunzi": "student",
        "barua pepe": "email", "intaneti": "internet", "tovuti": "website", "faili": "file", "skrini": "screen", "kibodi": "keyboard",
        "mradi": "project", "timu": "team", "kampuni": "company", "mteja": "customer", "soko": "market", "duka": "shop",
        "hoteli": "hotel", "uwanja wa ndege": "airport", "basi": "bus", "treni": "train", "tiketi": "ticket", "ramani": "map",
        "kifungua kinywa": "breakfast", "chakula cha mchana": "lunch", "chakula cha jioni": "dinner", "mkate": "bread", "mchele": "rice", "nyama": "meat", "matunda": "fruit", "maziwa": "milk", "chai": "tea", "juisi": "juice",
        "wiki": "week", "mwezi": "month", "mwaka": "year", "saa": "hour", "dakika": "minute", "jana": "yesterday", "miadi": "appointment", "ratiba": "schedule",
    },
    "es": {
        "gracias": "thank you", "hola": "hello", "adiós": "goodbye", "perdón": "sorry", "bienvenido": "welcome",
        "madre": "mother", "padre": "father", "hermano": "brother", "hermana": "sister", "hijo": "son", "hija": "daughter",
        "habitación": "room", "puerta": "door", "ventana": "window", "cama": "bed", "silla": "chair", "mesa": "table", "cocina": "kitchen",
        "clase": "class", "lección": "lesson", "profesor": "teacher", "estudiante": "student", "correo electrónico": "email", "sitio web": "website", "archivo": "file", "pantalla": "screen", "teclado": "keyboard",
        "proyecto": "project", "equipo": "team", "empresa": "company", "cliente": "customer", "mercado": "market", "tienda": "shop", "aeropuerto": "airport", "autobús": "bus", "tren": "train", "billete": "ticket", "mapa": "map",
        "desayuno": "breakfast", "almuerzo": "lunch", "cena": "dinner", "pan": "bread", "arroz": "rice", "carne": "meat", "fruta": "fruit", "leche": "milk", "té": "tea", "jugo": "juice", "semana": "week", "mes": "month", "año": "year", "hora": "hour", "minuto": "minute", "ayer": "yesterday", "cita": "appointment", "horario": "schedule",
    },
    "fr": {
        "merci": "thank you", "bonjour": "hello", "au revoir": "goodbye", "désolé": "sorry", "bienvenue": "welcome",
        "mère": "mother", "père": "father", "frère": "brother", "sœur": "sister", "fils": "son", "fille": "daughter",
        "chambre": "room", "porte": "door", "fenêtre": "window", "lit": "bed", "chaise": "chair", "table": "table", "cuisine": "kitchen", "classe": "class", "leçon": "lesson", "professeur": "teacher", "étudiant": "student",
        "e-mail": "email", "site web": "website", "fichier": "file", "écran": "screen", "clavier": "keyboard", "projet": "project", "équipe": "team", "entreprise": "company", "client": "customer", "marché": "market", "magasin": "shop", "aéroport": "airport", "billet": "ticket", "carte": "map",
        "petit-déjeuner": "breakfast", "déjeuner": "lunch", "dîner": "dinner", "pain": "bread", "riz": "rice", "viande": "meat", "fruit": "fruit", "lait": "milk", "thé": "tea", "jus": "juice", "semaine": "week", "mois": "month", "an": "year", "heure": "hour", "minute": "minute", "hier": "yesterday", "rendez-vous": "appointment", "emploi du temps": "schedule",
    },
    "de": {
        "danke": "thank you", "hallo": "hello", "auf wiedersehen": "goodbye", "entschuldigung": "sorry", "willkommen": "welcome",
        "mutter": "mother", "vater": "father", "bruder": "brother", "schwester": "sister", "sohn": "son", "tochter": "daughter", "zimmer": "room", "tür": "door", "fenster": "window", "bett": "bed", "stuhl": "chair", "tisch": "table", "küche": "kitchen", "klasse": "class", "lektion": "lesson", "lehrer": "teacher", "schüler": "student",
        "e-mail": "email", "webseite": "website", "datei": "file", "bildschirm": "screen", "tastatur": "keyboard", "projekt": "project", "team": "team", "unternehmen": "company", "kunde": "customer", "markt": "market", "geschäft": "shop", "flughafen": "airport", "fahrkarte": "ticket", "karte": "map",
        "frühstück": "breakfast", "mittagessen": "lunch", "abendessen": "dinner", "brot": "bread", "reis": "rice", "fleisch": "meat", "obst": "fruit", "milch": "milk", "tee": "tea", "saft": "juice", "woche": "week", "monat": "month", "jahr": "year", "stunde": "hour", "minute": "minute", "gestern": "yesterday", "termin": "appointment", "zeitplan": "schedule",
    },
    "it": {
        "grazie": "thank you", "ciao": "hello", "arrivederci": "goodbye", "scusa": "sorry", "benvenuto": "welcome",
        "madre": "mother", "padre": "father", "fratello": "brother", "sorella": "sister", "figlio": "son", "figlia": "daughter", "stanza": "room", "porta": "door", "finestra": "window", "letto": "bed", "sedia": "chair", "tavolo": "table", "cucina": "kitchen", "classe": "class", "lezione": "lesson", "insegnante": "teacher", "studente": "student",
        "e-mail": "email", "sito web": "website", "file": "file", "schermo": "screen", "tastiera": "keyboard", "progetto": "project", "squadra": "team", "azienda": "company", "cliente": "customer", "mercato": "market", "negozio": "shop", "aeroporto": "airport", "biglietto": "ticket", "mappa": "map",
        "colazione": "breakfast", "pranzo": "lunch", "cena": "dinner", "pane": "bread", "riso": "rice", "carne": "meat", "frutta": "fruit", "latte": "milk", "tè": "tea", "succo": "juice", "settimana": "week", "mese": "month", "anno": "year", "ora": "hour", "minuto": "minute", "ieri": "yesterday", "appuntamento": "appointment", "programma": "schedule",
    },
}


def build_reverse_dictionary(source):
    """Build a foreign-language to English dictionary for offline translation."""
    if source == "en":
        return {}

    reverse = {}
    source_maps = [
        REVERSE_EXTRA_WORDS.get(source, {}),
        EXPLICIT_WORDS.get(source, {}),
        EXTENDED_WORDS.get(source, {}),
    ]

    for category in CATEGORY_WORDS.get(source, {}).values():
        source_maps.append(category)

    # Prefer the most specific/common English key when several English words
    # share one translated value. Phrase matching below handles expressions.
    for dictionary in source_maps:
        for english_word, translated_word in dictionary.items():
            if translated_word and translated_word.lower() not in reverse:
                reverse[translated_word.lower()] = english_word

    return reverse


def build_reverse_phrases(source):
    """Build complete foreign-language expressions mapped back to English."""
    if source == "en":
        return {}

    reverse = {}
    phrase_maps = [
        REVERSE_EXTRA_PHRASES.get(source, {}),
        CATEGORY_PHRASES.get(source, {}),
        MULTILINGUAL_PHRASES.get(source, {}),
        PHRASES.get(source, {}),
    ]

    for dictionary in phrase_maps:
        for english_phrase, translated_phrase in dictionary.items():
            if translated_phrase and translated_phrase.lower() not in reverse:
                reverse[translated_phrase.lower()] = english_phrase

    return reverse


def detect_offline_source(text):
    """Best-effort source detection for common offline dictionary terms."""
    normalized = text.lower().strip()
    scores = {}

    for language in LANGUAGES:
        if language == "en":
            continue
        score = 0
        for phrase in build_reverse_phrases(language):
            if re.search(
                r"(?i)(?<![A-Za-zÀ-ÿ])" + re.escape(phrase) + r"(?![A-Za-zÀ-ÿ])",
                normalized,
            ):
                score += max(3, len(phrase.split()))

        reverse_dictionary = build_reverse_dictionary(language)
        for word in re.findall(r"[A-Za-zÀ-ÿ']+", normalized):
            if word in reverse_dictionary:
                score += 1

        scores[language] = score

    best_language = max(scores, key=scores.get, default="en")
    return best_language if scores.get(best_language, 0) else "en"


def offline_translate(text, target, source="auto"):
    # When translating into English, use the source language's reverse maps.
    if target == "en" and source == "auto":
        source = detect_offline_source(text)
    # This handles inputs such as "por favor" instead of treating them as
    # unknown text simply because the normal dictionaries are English-based.
    if target == "en" and source not in ("auto", "en"):
        result = text
        phrases = build_reverse_phrases(source)
        protected_phrases = []

        for translated_phrase, english_phrase in sorted(
            phrases.items(), key=lambda item: len(item[0]), reverse=True
        ):
            pattern = r"(?i)(?<![A-Za-zÀ-ÿ])" + re.escape(translated_phrase) + r"(?![A-Za-zÀ-ÿ])"

            def replace_reverse_phrase(match, value=english_phrase):
                replacement = preserve_case(match.group(0), value)
                protected_phrases.append(replacement)
                return f"\\x00{len(protected_phrases) - 1}\\x00"

            result = re.sub(pattern, replace_reverse_phrase, result)

        reverse_dictionary = build_reverse_dictionary(source)
        result = re.sub(
            r"[A-Za-zÀ-ÿ']+",
            lambda match: preserve_case(
                match.group(0),
                reverse_dictionary.get(match.group(0).lower(), match.group(0)),
            ),
            result,
        )

        for index, phrase in enumerate(protected_phrases):
            result = result.replace(f"\\x00{index}\\x00", phrase)

        return result

    if target == "en":
        return text

    result = text
    protected_phrases = []
    phrases = {**CATEGORY_PHRASES.get(target, {}), **MULTILINGUAL_PHRASES.get(target, {}), **PHRASES.get(target, {})}

    # Match longer expressions first and temporarily protect their output.
    # This prevents a translated phrase from being altered by the word map.
    for source, translated in sorted(phrases.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = r"(?i)(?<![A-Za-zÀ-ÿ])" + re.escape(source) + r"(?![A-Za-zÀ-ÿ])"

        def replace_phrase(match, value=translated):
            replacement = preserve_case(match.group(0), value)
            protected_phrases.append(replacement)
            return f"\x00{len(protected_phrases) - 1}\x00"

        result = re.sub(pattern, replace_phrase, result)

    dictionary = build_dictionary(target)
    result = re.sub(
        r"[A-Za-zÀ-ÿ']+",
        lambda match: preserve_case(match.group(0), dictionary.get(match.group(0).lower(), match.group(0))),
        result,
    )

    for index, phrase in enumerate(protected_phrases):
        result = result.replace(f"\x00{index}\x00", phrase)

    return result


def extract_translation(data):
    """Read common translation response shapes without accepting empty input."""
    if isinstance(data, str) and data.strip():
        return data.strip()

    if isinstance(data, list):
        for item in data:
            translation = extract_translation(item)
            if translation:
                return translation
        return None

    if not isinstance(data, dict):
        return None

    fields = (
        "translatedText",
        "translated_text",
        "translation",
        "text",
    )
    for field in fields:
        translation = data.get(field)
        if isinstance(translation, str) and translation.strip():
            return translation.strip()

    for field in ("result", "data", "response"):
        translation = extract_translation(data.get(field))
        if translation:
            return translation

    return None


def online_translate(text, source, target):
    """Call the configured provider; never use the source text as a result."""
    endpoint = os.getenv("TRANSLATION_API_URL", "").strip()
    if not endpoint:
        return None

    # This is the standard LibreTranslate-compatible JSON request format.
    # Configure TRANSLATION_API_URL for the provider's POST translation endpoint;
    # no provider URL is assumed or hard-coded here.
    payload = {
        "q": text,
        "source": "auto" if source == "auto" else source,
        "target": target,
        "format": "text",
    }
    api_key = os.getenv("TRANSLATION_API_KEY", "").strip()
    if api_key:
        payload["api_key"] = api_key

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urlrequest.urlopen(req, timeout=ONLINE_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))

        return extract_translation(data)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return None


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


# PWA/static assets are served explicitly so they work reliably under Gunicorn
# on Render, regardless of Flask's static-folder configuration.
@app.get("/manifest.json")
def manifest():
    return send_from_directory(".", "manifest.json", mimetype="application/manifest+json")


@app.get("/icon.svg")
def icon():
    return send_from_directory(".", "icon.svg", mimetype="image/svg+xml")


@app.get("/favicon.ico")
def favicon():
    # Browsers commonly request /favicon.ico even when the PWA manifest uses
    # an SVG icon. Returning the SVG keeps the request successful without
    # requiring a binary favicon file.
    return send_from_directory(".", "icon.svg", mimetype="image/svg+xml")


@app.get("/audio/manifest.json")
def audio_manifest():
    path = os.path.join(app.root_path, "audio", "manifest.json")
    if not os.path.isfile(path):
        return jsonify({"version": 1, "languages": {}})
    return send_from_directory(os.path.join(app.root_path, "audio"), "manifest.json", mimetype="application/json")


@app.get("/audio/<path:filename>")
def course_audio(filename):
    return send_from_directory(os.path.join(app.root_path, "audio"), filename)


@app.get("/sw.js")
def service_worker():
    return send_from_directory(".", "sw.js", mimetype="application/javascript")


@app.errorhandler(404)
def page_not_found(error):
    # Never reference a missing 404.html: that can turn a normal 404 into a
    # misleading 500. Return a small JSON response for API-style requests and
    # the main app for browser navigation.
    if request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json":
        return jsonify({"error": "Not found", "path": request.path}), 404
    return send_from_directory(".", "index.html"), 404


@app.get("/languages")
def languages():
    return jsonify(LANGUAGES)


@app.get("/health")
def health():
    return jsonify({"ok": True, "translation_configured": bool(os.getenv("TRANSLATION_API_URL", "").strip()), "ai_configured": bool(os.getenv("AI_API_URL", "").strip())})


@app.post("/assist")
def assist_endpoint():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    action = str(data.get("action", "natural")).strip().lower()
    if not text:
        return jsonify({"error": "Please enter a phrase for the assistant."}), 400
    if len(text) > MAX_LENGTH:
        return jsonify({"error": f"Please keep your text under {MAX_LENGTH:,} characters."}), 400
    if action not in {"natural", "polite", "shorter", "explain"}:
        return jsonify({"error": "Please choose a supported assistant action."}), 400

    endpoint = os.getenv("AI_API_URL", "").strip()
    if endpoint:
        prompt = {
            "natural": "Rewrite this phrase so it sounds natural while preserving its meaning.",
            "polite": "Rewrite this phrase to sound warm and polite while preserving its meaning.",
            "shorter": "Make this phrase shorter and clear while preserving its meaning.",
            "explain": "Explain the tone, meaning, and best everyday use of this phrase in a concise way.",
        }[action]
        payload = json.dumps({"prompt": f"{prompt}\\n\\nPhrase: {text}", "text": text, "action": action}).encode("utf-8")
        try:
            req = urlrequest.Request(endpoint, data=payload, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
            with urlrequest.urlopen(req, timeout=ONLINE_TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
            answer = extract_translation(result)
            if isinstance(result, dict):
                answer = answer or result.get("response") or result.get("output")
                if not answer and isinstance(result.get("choices"), list) and result["choices"]:
                    choice = result["choices"][0]
                    answer = choice.get("text") if isinstance(choice, dict) else None
                    if isinstance(choice, dict) and isinstance(choice.get("message"), dict):
                        answer = choice["message"].get("content")
            if isinstance(answer, str) and answer.strip():
                return jsonify({"response": answer.strip(), "suggestion": answer.strip(), "provider": "ai"})
        except (HTTPError, URLError, TimeoutError, ValueError, OSError, KeyError, TypeError):
            pass

    return jsonify({"response": "Here’s a built-in suggestion based on your phrase.", "suggestion": text, "provider": "guide"})



def offline_tutor_reply(language, level, scenario, message):
    prompts = {
        "es": "¡Muy bien! Sigue practicando. ¿Puedes añadir un poco más de información?",
        "fr": "Très bien ! Continuez à pratiquer. Pouvez-vous ajouter un peu plus d’information ?",
        "sw": "Vizuri sana! Endelea kufanya mazoezi. Unaweza kuongeza maelezo kidogo?",
        "de": "Sehr gut! Übe weiter. Kannst du noch ein bisschen mehr sagen?",
        "it": "Molto bene! Continua a praticare. Puoi aggiungere qualche dettaglio?",
    }
    corrections = ""
    clean = re.sub(r"\s+", " ", message.strip())
    if len(clean.split()) < 2:
        corrections = "Try a complete sentence with at least two words."
    elif level in {"B1", "B2"} and len(clean.split()) < 4:
        corrections = "Good start. At this level, try adding one reason, detail, or time expression."
    return {"response": prompts.get(language, "Great job! Keep practising. Can you add one more detail?"), "correction": corrections, "provider": "offline", "xp": 4}

@app.post("/tutor")
def tutor_endpoint():
    data = request.get_json(silent=True) or {}
    language = str(data.get("language", "es")).strip().lower()
    level = str(data.get("level", "A1")).strip().upper()
    scenario = str(data.get("scenario", "free")).strip().lower()
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])
    if language not in LANGUAGES:
        return jsonify({"error": "Unsupported language."}), 400
    if level not in {"A1", "A2", "B1", "B2"}:
        return jsonify({"error": "Unsupported level."}), 400
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if len(message) > 2000:
        return jsonify({"error": "Please keep the tutor message under 2,000 characters."}), 400
    endpoint = os.getenv("AI_API_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    if endpoint:
        system = (f"You are Lingua, a safe language-learning tutor. Teach {LANGUAGES[language]} at CEFR-style level {level}. "
                  f"Scenario: {scenario}. Reply mainly in the target language, keep explanations simple, gently correct important errors, "
                  "and ask one useful follow-up question. Never pretend to be a human or romantic companion.")
        payload = {"prompt": system + "\n\nConversation history:\n" + json.dumps(history[-8:], ensure_ascii=False) + "\n\nLearner message: " + message,
                   "text": message, "language": language, "level": level, "scenario": scenario, "history": history[-8:]}
        try:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            req = urlrequest.Request(endpoint, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers, method="POST")
            with urlrequest.urlopen(req, timeout=ONLINE_TIMEOUT) as response:
                result = json.loads(response.read().decode("utf-8"))
            answer = extract_translation(result)
            if isinstance(result, dict):
                answer = answer or result.get("response") or result.get("output") or result.get("message")
                if not answer and isinstance(result.get("choices"), list) and result["choices"]:
                    choice = result["choices"][0]
                    if isinstance(choice, dict):
                        answer = choice.get("text")
                        if isinstance(choice.get("message"), dict):
                            answer = choice["message"].get("content") or answer
            if isinstance(answer, str) and answer.strip():
                return jsonify({"response": answer.strip(), "provider": "ai", "xp": 6})
        except (HTTPError, URLError, TimeoutError, ValueError, OSError, KeyError, TypeError):
            pass
    return jsonify(offline_tutor_reply(language, level, scenario, message))

@app.post("/translate")
def translate_endpoint():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    source = str(data.get("source", "auto")).strip().lower()
    target = str(data.get("target", "")).strip().lower()
    if not text:
        return jsonify({"error": "Please enter text to translate."}), 400
    if len(text) > MAX_LENGTH:
        return jsonify({"error": f"Please keep your text under {MAX_LENGTH:,} characters."}), 400
    if source != "auto" and source not in LANGUAGES:
        return jsonify({"error": "Please choose a supported source language."}), 400
    if target not in LANGUAGES:
        return jsonify({"error": "Please choose a supported target language."}), 400

    use_offline = bool(data.get("use_offline", False))
    translation = None
    provider = "offline" if use_offline else "online"

    # Offline mode must never contact an external provider. This keeps the
    # phrasebook private and makes it useful when the network is unavailable.
    if use_offline:
        translation = offline_translate(text, target, source)
    else:
        translation = online_translate(text, source, target)

        # Render deployments do not have a translation provider unless the
        # owner adds TRANSLATION_API_URL. Do not make the entire translator
        # appear broken in that situation: fall back to Lingua's built-in
        # phrasebook/dictionary for supported offline content.
        if not translation:
            translation = offline_translate(text, target, source)
            if translation and translation.strip().lower() != text.strip().lower():
                provider = "offline-fallback"
            else:
                translation = None

    if not translation:
        return jsonify({
            "error": "No online translation provider is configured or the phrase is not in Lingua's offline phrasebook yet. Enable Offline phrasebook for supported starter phrases, or configure TRANSLATION_API_URL on Render for full online translation."
        }), 503

    return jsonify({
        "translation": translation,
        "detected_source": "en" if source == "auto" else source,
        "provider": provider,
        "offline_fallback": provider == "offline-fallback",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
