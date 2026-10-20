"""Per-language page plan for the $49/mo organic Instagram growth product -> keywords/instagram_growth_pages.csv"""
import csv, sys

# lang: (base slug, {page: sub-slug}, {page: (primary keyword, secondary, title, description)})
P = {}

P["en"] = ("instagram-followers", {"pricing": "pricing", "guide_buy": "should-you-buy-instagram-followers", "guide_speed": "how-fast-can-you-grow"}, {
 "main": ("buy real instagram followers", "buy instagram followers real (14.8K) · organic · active · that engage · targeted · gradual · no drop · reviews",
          "Real Instagram Followers, Grown Organically | No Bots, $49/mo",
          "Stop buying bots. Get 900–3,000 real, organic Instagram followers a month, targeted to your location. Nothing that risks a ban. $49/month."),
 "pricing": ("cheap instagram followers", "buy instagram followers cheap (4.4K) · price · cost · how much · paypal · apple pay · credit card",
          "Cheap Instagram Followers? Real Organic Growth for $49/mo",
          "Cheap followers are bots that vanish. $49 a month brings 900–3,000 real, organic followers from the places you choose. Card, Apple Pay, Google Pay."),
 "guide_buy": ("can you buy instagram followers", "do you buy instagram followers (5.4K) · does it work · get banned · legal · safe · worth it",
          "Should You Buy Instagram Followers? Risks & the Organic Way",
          "Can you buy Instagram followers, does it work, can you get banned? Honest answers, and how to grow real followers organically instead."),
 "guide_speed": ("how to get 1k instagram followers", "buy instagram followers 1k/10k/100k · 500 · 1000 · instant · fast · quick",
          "How Fast Can You Grow Instagram Followers Organically?",
          "From 1k to 10k: realistic organic growth numbers. Our clients average 900–3,000 real followers a month, with no bots and no ban risk."),
})
GEO_EN = {
 "usa": ("buy instagram followers usa", "buy ig followers usa", "Real Instagram Followers in the USA, Grown Organically", "USA"),
 "uk": ("buy instagram followers uk", "real uk · best uk · in the uk", "Real Instagram Followers in the UK, Grown Organically", "UK"),
 "australia": ("buy instagram followers australia", "aud · in australia", "Real Instagram Followers in Australia, Grown Organically", "Australian"),
 "europe": ("buy instagram followers europe", "germany · romania · real europe", "Real Instagram Followers in Europe, Grown Organically", "European"),
 "uae": ("buy instagram followers uae", "dubai", "Real Instagram Followers in the UAE & Dubai, Grown Organically", "UAE"),
}

P["tr"] = ("instagram-takipci", {"pricing": "fiyat", "guide_buy": "satin-almak-guvenli-mi", "guide_speed": "ayda-kac-takipci"}, {
 "main": ("instagram takipçi satın al", "gerçek takipçi satın al · organik takipçi · türk takipçi · aktif takipçi · düşmeyen takipçi",
          "Gerçek Instagram Takipçisi, Organik Büyüme | Bot Yok, 49$/ay",
          "Bot takipçi almayın. Ayda ortalama 900–3.000 gerçek, organik Instagram takipçisi; konumunuza göre hedefli. Ban riskine sokan hiçbir şey yok. Aylık 49$."),
 "pricing": ("ucuz instagram takipçi", "instagram takipçi fiyatları · takipçi paketleri · kredi kartı",
          "Ucuz Instagram Takipçi mi? Organik Büyüme Aylık 49$",
          "Ucuz takipçi bottur, düşer. Aylık 49$ ile seçtiğiniz konumlardan ayda 900–3.000 gerçek, organik takipçi. Kart, Apple Pay, Google Pay."),
 "guide_buy": ("instagram takipçi satın almak güvenli mi", "takipçi satın almak yasak mı · ban yer miyim · işe yarar mı",
          "Instagram Takipçi Satın Almak Güvenli mi? Organik Alternatif",
          "Takipçi satın alınır mı, işe yarar mı, ban yer misiniz? Dürüst cevaplar ve gerçek takipçiyi organik olarak büyütmenin yolu."),
 "guide_speed": ("instagram takipçi nasıl artırılır", "1000 takipçi · 10 bin takipçi · hızlı takipçi",
          "Instagram'da Ayda Kaç Takipçi Organik Olarak Kazanılır?",
          "1.000'den 10.000'e gerçekçi organik büyüme rakamları. Müşterilerimiz ayda ortalama 900–3.000 gerçek takipçi kazanıyor; bot yok, ban riski yok."),
})
P["de"] = ("instagram-follower", {"pricing": "preise", "guide_buy": "follower-kaufen-sinnvoll", "guide_speed": "wie-schnell-wachsen"}, {
 "main": ("instagram follower kaufen", "echte instagram follower kaufen · organische follower · deutsche follower · aktive follower",
          "Echte Instagram Follower, organisch gewachsen | Keine Bots, 49 $",
          "Keine Bots kaufen: monatlich 900–3.000 echte, organische Instagram Follower, gezielt nach Standort. Nichts, was einen Bann riskiert. 49 $/Monat."),
 "pricing": ("instagram follower günstig", "instagram follower kaufen preis · paypal · kreditkarte",
          "Instagram Follower günstig? Echtes organisches Wachstum, 49 $",
          "Billige Follower sind Bots, die wieder verschwinden. Für 49 $ im Monat: 900–3.000 echte, organische Follower aus Ihren Zielorten."),
 "guide_buy": ("instagram follower kaufen legal", "follower kaufen sinnvoll · sperre · bringt es etwas",
          "Instagram Follower kaufen – sinnvoll? Die organische Alternative",
          "Kann man Instagram Follower kaufen, bringt es etwas, droht ein Bann? Ehrliche Antworten und wie Sie echte Follower organisch aufbauen."),
 "guide_speed": ("mehr instagram follower bekommen", "1000 follower · 10k follower · schnell follower bekommen",
          "Wie schnell wachsen Instagram Follower organisch?",
          "Von 1.000 auf 10.000: realistische Zahlen für organisches Wachstum. Unsere Kunden gewinnen im Schnitt 900–3.000 echte Follower pro Monat, ohne Bots."),
})
P["nl"] = ("instagram-volgers", {"pricing": "prijzen", "guide_buy": "volgers-kopen-veilig", "guide_speed": "hoe-snel-groeien"}, {
 "main": ("instagram volgers kopen", "echte instagram volgers kopen · nederlandse volgers · organische volgers",
          "Echte Instagram volgers, organisch gegroeid | Geen bots, $49",
          "Koop geen bots. Elke maand 900–3.000 echte, organische Instagram volgers, gericht op uw locatie. Niets wat een ban riskeert. $49 per maand."),
 "pricing": ("goedkope instagram volgers", "instagram volgers kopen prijs · ideal · creditcard",
          "Goedkope Instagram volgers? Echte organische groei voor $49",
          "Goedkope volgers zijn bots die weer verdwijnen. Voor $49 per maand: 900–3.000 echte, organische volgers uit de plaatsen die u kiest."),
 "guide_buy": ("instagram volgers kopen veilig", "volgers kopen legaal · ban · werkt het",
          "Instagram volgers kopen: veilig? Het organische alternatief",
          "Kun je Instagram volgers kopen, werkt het, riskeer je een ban? Eerlijke antwoorden en hoe u echte volgers organisch laat groeien."),
 "guide_speed": ("meer instagram volgers krijgen", "1000 volgers · 10k volgers · snel volgers",
          "Hoe snel groeien Instagram volgers organisch?",
          "Van 1.000 naar 10.000: realistische cijfers voor organische groei. Onze klanten krijgen gemiddeld 900–3.000 echte volgers per maand, zonder bots."),
})
P["fr"] = ("abonnes-instagram", {"pricing": "tarifs", "guide_buy": "acheter-des-abonnes-risques", "guide_speed": "combien-par-mois"}, {
 "main": ("acheter des abonnés instagram", "acheter des followers instagram · vrais abonnés · abonnés français · organiques",
          "Vrais abonnés Instagram, croissance organique | Sans bots, 49 $",
          "N'achetez pas de bots. 900 à 3 000 vrais abonnés Instagram organiques par mois, ciblés selon votre zone. Rien qui risque un ban. 49 $/mois."),
 "pricing": ("abonnés instagram pas cher", "prix abonnés instagram · paypal · carte bancaire",
          "Abonnés Instagram pas cher ? Croissance organique à 49 $/mois",
          "Les abonnés pas chers sont des bots qui disparaissent. Pour 49 $ par mois : 900 à 3 000 vrais abonnés organiques des zones que vous choisissez."),
 "guide_buy": ("acheter des abonnés instagram est-ce légal", "risques · ban · est-ce que ça marche",
          "Acheter des abonnés Instagram : risques et alternative organique",
          "Peut-on acheter des abonnés Instagram, est-ce utile, risque-t-on un ban ? Des réponses honnêtes et comment gagner de vrais abonnés organiquement."),
 "guide_speed": ("gagner des abonnés instagram", "1000 abonnés · 10k abonnés · rapidement",
          "Combien d'abonnés Instagram gagner par mois, organiquement ?",
          "De 1 000 à 10 000 : des chiffres réalistes de croissance organique. Nos clients gagnent en moyenne 900 à 3 000 vrais abonnés par mois, sans bots."),
})
P["it"] = ("follower-instagram", {"pricing": "prezzi", "guide_buy": "comprare-follower-conviene", "guide_speed": "quanti-al-mese"}, {
 "main": ("comprare follower instagram", "follower instagram reali · follower italiani · organici · attivi",
          "Follower Instagram reali, crescita organica | Niente bot, 49 $",
          "Non comprare bot. Da 900 a 3.000 follower Instagram reali e organici al mese, mirati sulla tua zona. Niente che rischi un ban. 49 $ al mese."),
 "pricing": ("follower instagram economici", "prezzo follower instagram · paypal · carta",
          "Follower Instagram economici? Crescita organica a 49 $/mese",
          "I follower economici sono bot che spariscono. Con 49 $ al mese: da 900 a 3.000 follower reali e organici dalle zone che scegli."),
 "guide_buy": ("comprare follower instagram è legale", "conviene · ban · funziona",
          "Comprare follower Instagram conviene? L'alternativa organica",
          "Si possono comprare follower Instagram, funziona, si rischia il ban? Risposte oneste e come far crescere follower reali in modo organico."),
 "guide_speed": ("aumentare follower instagram", "1000 follower · 10k follower · velocemente",
          "Quanti follower Instagram al mese, in modo organico?",
          "Da 1.000 a 10.000: numeri realistici di crescita organica. I nostri clienti ottengono in media da 900 a 3.000 follower reali al mese, senza bot."),
})
P["es"] = ("seguidores-instagram", {"pricing": "precios", "guide_buy": "comprar-seguidores-es-seguro", "guide_speed": "cuantos-al-mes"}, {
 "main": ("comprar seguidores instagram", "comprar seguidores reales · seguidores españoles · orgánicos · activos",
          "Seguidores reales en Instagram, crecimiento orgánico | Sin bots",
          "No compres bots. Entre 900 y 3.000 seguidores reales y orgánicos al mes, segmentados por ubicación. Nada que arriesgue un baneo. 49 $ al mes."),
 "pricing": ("seguidores instagram baratos", "precio seguidores instagram · paypal · tarjeta",
          "¿Seguidores de Instagram baratos? Crecimiento orgánico por 49 $",
          "Los seguidores baratos son bots que desaparecen. Por 49 $ al mes: entre 900 y 3.000 seguidores reales y orgánicos de las zonas que elijas."),
 "guide_buy": ("es seguro comprar seguidores en instagram", "es legal · baneo · funciona",
          "¿Es seguro comprar seguidores de Instagram? La vía orgánica",
          "¿Se pueden comprar seguidores, funciona, te pueden banear? Respuestas honestas y cómo ganar seguidores reales de forma orgánica."),
 "guide_speed": ("ganar seguidores en instagram", "1000 seguidores · 10k seguidores · rápido",
          "¿Cuántos seguidores de Instagram se ganan al mes orgánicamente?",
          "De 1.000 a 10.000: cifras realistas de crecimiento orgánico. Nuestros clientes ganan de media entre 900 y 3.000 seguidores reales al mes, sin bots."),
})
P["pl"] = ("obserwujacy-instagram", {"pricing": "cennik", "guide_buy": "czy-warto-kupowac", "guide_speed": "ilu-miesiecznie"}, {
 "main": ("kupić obserwujących instagram", "prawdziwi obserwujący · polscy obserwujący · organiczni · aktywni",
          "Prawdziwi obserwujący na Instagramie, organicznie | Bez botów",
          "Nie kupuj botów. 900–3000 prawdziwych, organicznych obserwujących miesięcznie, z wybranej lokalizacji. Nic, co grozi banem. 49 $ miesięcznie."),
 "pricing": ("tani obserwujący instagram", "cena obserwujących · blik · karta",
          "Tani obserwujący na Instagramie? Organiczny wzrost za 49 $",
          "Tani obserwujący to boty, które znikają. Za 49 $ miesięcznie: 900–3000 prawdziwych, organicznych obserwujących z wybranych miejsc."),
 "guide_buy": ("czy warto kupować obserwujących", "czy to legalne · ban · czy działa",
          "Kupować obserwujących na Instagramie? Organiczna alternatywa",
          "Czy można kupić obserwujących, czy to działa, czy grozi ban? Szczere odpowiedzi i jak organicznie zdobywać prawdziwych obserwujących."),
 "guide_speed": ("jak zdobyć obserwujących na instagramie", "1000 obserwujących · 10k · szybko",
          "Ilu obserwujących na Instagramie miesięcznie, organicznie?",
          "Od 1000 do 10 000: realne liczby wzrostu organicznego. Nasi klienci zyskują średnio 900–3000 prawdziwych obserwujących miesięcznie, bez botów."),
})
P["ru"] = ("podpischiki-instagram", {"pricing": "ceny", "guide_buy": "stoit-li-pokupat", "guide_speed": "skolko-v-mesyac"}, {
 "main": ("купить подписчиков в инстаграм", "живые подписчики · реальные подписчики · органический рост · активные",
          "Живые подписчики в Instagram, органический рост | Без ботов",
          "Не покупайте ботов. 900–3000 живых органических подписчиков в месяц с таргетингом по локации. Ничего, что грозит баном. 49 $ в месяц."),
 "pricing": ("дешёвые подписчики инстаграм", "цена подписчиков · оплата картой",
          "Дешёвые подписчики Instagram? Органический рост за 49 $",
          "Дешёвые подписчики — это боты, которые отписываются. За 49 $ в месяц: 900–3000 живых органических подписчиков из выбранных вами мест."),
 "guide_buy": ("стоит ли покупать подписчиков", "можно ли · бан · работает ли",
          "Стоит ли покупать подписчиков в Instagram? Органический путь",
          "Можно ли купить подписчиков, работает ли это, будет ли бан? Честные ответы и как органически набирать живых подписчиков."),
 "guide_speed": ("как набрать подписчиков в инстаграм", "1000 подписчиков · 10к · быстро",
          "Сколько подписчиков в Instagram можно набрать органически?",
          "От 1000 до 10 000: реальные цифры органического роста. Наши клиенты получают в среднем 900–3000 живых подписчиков в месяц, без ботов."),
})
P["uk"] = ("pidpysnyky-instagram", {"pricing": "tsiny", "guide_buy": "chy-varto-kupuvaty", "guide_speed": "skilky-na-misyats"}, {
 "main": ("купити підписників інстаграм", "живі підписники · реальні підписники · органічне зростання · активні",
          "Живі підписники в Instagram, органічне зростання | Без ботів",
          "Не купуйте ботів. 900–3000 живих органічних підписників на місяць із таргетингом за локацією. Нічого, що загрожує баном. 49 $ на місяць."),
 "pricing": ("дешеві підписники інстаграм", "ціна підписників · оплата карткою",
          "Дешеві підписники Instagram? Органічне зростання за 49 $",
          "Дешеві підписники — це боти, які відписуються. За 49 $ на місяць: 900–3000 живих органічних підписників із вибраних вами місць."),
 "guide_buy": ("чи варто купувати підписників", "чи можна · бан · чи працює",
          "Чи варто купувати підписників в Instagram? Органічний шлях",
          "Чи можна купити підписників, чи це працює, чи буде бан? Чесні відповіді та як органічно набирати живих підписників."),
 "guide_speed": ("як набрати підписників в інстаграм", "1000 підписників · 10к · швидко",
          "Скільки підписників в Instagram можна набрати органічно?",
          "Від 1000 до 10 000: реальні цифри органічного зростання. Наші клієнти отримують у середньому 900–3000 живих підписників на місяць, без ботів."),
})
P["ar"] = ("mutabieen-instagram", {"pricing": "asaar", "guide_buy": "hal-shiraa-mutabieen-aman", "guide_speed": "kam-mutabie-shahriyan"}, {
 "main": ("شراء متابعين انستقرام", "متابعين حقيقيين · متابعين عرب · نمو طبيعي · متابعين نشطين",
          "متابعين انستقرام حقيقيين بنمو طبيعي | بدون بوتات، 49$ شهريًا",
          "لا تشترِ بوتات. من 900 إلى 3000 متابع حقيقي على انستقرام شهريًا بنمو طبيعي، موجّه حسب موقعك. لا شيء يعرّضك للحظر. 49$ شهريًا."),
 "pricing": ("متابعين انستقرام رخيص", "سعر متابعين انستقرام · الدفع بالبطاقة",
          "متابعين انستقرام رخيص؟ نمو طبيعي حقيقي بـ49$ شهريًا",
          "المتابعون الرخيصون بوتات تختفي. بـ49$ شهريًا تحصل على 900 إلى 3000 متابع حقيقي بنمو طبيعي من المواقع التي تختارها."),
 "guide_buy": ("هل شراء متابعين انستقرام آمن", "هل هو قانوني · الحظر · هل ينجح",
          "هل شراء متابعين انستقرام آمن؟ البديل الطبيعي",
          "هل يمكن شراء متابعين، هل ينجح ذلك، هل قد تتعرض للحظر؟ إجابات صريحة وكيف تنمّي متابعين حقيقيين بشكل طبيعي."),
 "guide_speed": ("زيادة متابعين انستقرام", "1000 متابع · 10 آلاف متابع · بسرعة",
          "كم متابعًا على انستقرام يمكن كسبه شهريًا بشكل طبيعي؟",
          "من 1000 إلى 10000: أرقام واقعية للنمو الطبيعي. يكسب عملاؤنا في المتوسط من 900 إلى 3000 متابع حقيقي شهريًا، بدون بوتات."),
})
P["sv"] = ("instagram-foljare", {"pricing": "priser", "guide_buy": "ar-det-sakert-att-kopa", "guide_speed": "hur-snabbt-vaxa"}, {
 "main": ("köpa instagram följare", "äkta följare · svenska följare · organiska följare · aktiva",
          "Äkta Instagram-följare, organisk tillväxt | Inga bottar, 49 $",
          "Köp inte bottar. 900–3 000 äkta, organiska Instagram-följare i månaden, riktade mot din plats. Inget som riskerar avstängning. 49 $/månad."),
 "pricing": ("billiga instagram följare", "pris följare · kort · swish",
          "Billiga Instagram-följare? Organisk tillväxt för 49 $/mån",
          "Billiga följare är bottar som försvinner. För 49 $ i månaden: 900–3 000 äkta, organiska följare från platserna du väljer."),
 "guide_buy": ("är det lagligt att köpa följare", "säkert · avstängning · fungerar det",
          "Köpa Instagram-följare – är det säkert? Det organiska alternativet",
          "Kan man köpa följare, fungerar det, kan kontot stängas av? Ärliga svar och hur du växer med äkta följare organiskt."),
 "guide_speed": ("få fler följare på instagram", "1000 följare · 10k · snabbt",
          "Hur snabbt växer Instagram-följare organiskt?",
          "Från 1 000 till 10 000: realistiska siffror för organisk tillväxt. Våra kunder får i snitt 900–3 000 äkta följare i månaden, utan bottar."),
})
P["da"] = ("instagram-folgere", {"pricing": "priser", "guide_buy": "er-det-sikkert-at-kobe", "guide_speed": "hvor-hurtigt-vokse"}, {
 "main": ("købe instagram følgere", "ægte følgere · danske følgere · organiske følgere · aktive",
          "Ægte Instagram-følgere, organisk vækst | Ingen bots, 49 $",
          "Køb ikke bots. 900–3.000 ægte, organiske Instagram-følgere om måneden, målrettet din placering. Intet, der risikerer udelukkelse. 49 $/md."),
 "pricing": ("billige instagram følgere", "pris følgere · kort · mobilepay",
          "Billige Instagram-følgere? Organisk vækst for 49 $/md.",
          "Billige følgere er bots, der forsvinder. For 49 $ om måneden: 900–3.000 ægte, organiske følgere fra de steder, du vælger."),
 "guide_buy": ("er det lovligt at købe følgere", "sikkert · udelukkelse · virker det",
          "Købe Instagram-følgere – er det sikkert? Det organiske alternativ",
          "Kan man købe følgere, virker det, risikerer man udelukkelse? Ærlige svar og hvordan du vokser med ægte følgere organisk."),
 "guide_speed": ("få flere følgere på instagram", "1000 følgere · 10k · hurtigt",
          "Hvor hurtigt vokser Instagram-følgere organisk?",
          "Fra 1.000 til 10.000: realistiske tal for organisk vækst. Vores kunder får i gennemsnit 900–3.000 ægte følgere om måneden, uden bots."),
})
P["no"] = ("instagram-folgere", {"pricing": "priser", "guide_buy": "er-det-trygt-a-kjope", "guide_speed": "hvor-raskt-vokse"}, {
 "main": ("kjøpe instagram følgere", "ekte følgere · norske følgere · organiske følgere · aktive",
          "Ekte Instagram-følgere, organisk vekst | Ingen bots, 49 $",
          "Ikke kjøp bots. 900–3 000 ekte, organiske Instagram-følgere i måneden, rettet mot stedet ditt. Ingenting som risikerer utestengelse. 49 $/mnd."),
 "pricing": ("billige instagram følgere", "pris følgere · kort · vipps",
          "Billige Instagram-følgere? Organisk vekst for 49 $/mnd",
          "Billige følgere er bots som forsvinner. For 49 $ i måneden: 900–3 000 ekte, organiske følgere fra stedene du velger."),
 "guide_buy": ("er det lov å kjøpe følgere", "trygt · utestengelse · virker det",
          "Kjøpe Instagram-følgere – er det trygt? Det organiske alternativet",
          "Kan man kjøpe følgere, virker det, kan kontoen bli stengt? Ærlige svar og hvordan du vokser med ekte følgere organisk."),
 "guide_speed": ("få flere følgere på instagram", "1000 følgere · 10k · raskt",
          "Hvor raskt vokser Instagram-følgere organisk?",
          "Fra 1 000 til 10 000: realistiske tall for organisk vekst. Kundene våre får i snitt 900–3 000 ekte følgere i måneden, uten bots."),
})
P["ro"] = ("urmaritori-instagram", {"pricing": "preturi", "guide_buy": "merita-sa-cumperi", "guide_speed": "cati-pe-luna"}, {
 "main": ("cumpără urmăritori instagram", "urmăritori reali · urmăritori români · organici · activi",
          "Urmăritori Instagram reali, creștere organică | Fără boți, 49 $",
          "Nu cumpăra boți. 900–3.000 de urmăritori Instagram reali și organici pe lună, țintiți după locație. Nimic care riscă un ban. 49 $/lună."),
 "pricing": ("urmăritori instagram ieftini", "preț urmăritori · card",
          "Urmăritori Instagram ieftini? Creștere organică la 49 $/lună",
          "Urmăritorii ieftini sunt boți care dispar. Cu 49 $ pe lună: 900–3.000 de urmăritori reali și organici din locurile alese de tine."),
 "guide_buy": ("este legal să cumperi urmăritori", "sigur · ban · funcționează",
          "Merită să cumperi urmăritori Instagram? Alternativa organică",
          "Se pot cumpăra urmăritori, funcționează, riști un ban? Răspunsuri sincere și cum crești organic cu urmăritori reali."),
 "guide_speed": ("cum să crești urmăritorii pe instagram", "1000 urmăritori · 10k · rapid",
          "Câți urmăritori Instagram poți câștiga organic pe lună?",
          "De la 1.000 la 10.000: cifre realiste de creștere organică. Clienții noștri câștigă în medie 900–3.000 de urmăritori reali pe lună, fără boți."),
})
P["az"] = ("instagram-izleyici", {"pricing": "qiymetler", "guide_buy": "almaq-tehlukesizdirmi", "guide_speed": "ayda-nece-izleyici"}, {
 "main": ("instagram izləyici almaq", "real izləyici · azərbaycanlı izləyici · orqanik izləyici · aktiv",
          "Real Instagram izləyiciləri, orqanik böyümə | Bot yox, 49 $",
          "Bot almayın. Ayda 900–3.000 real, orqanik Instagram izləyicisi, məkanınıza görə hədəflənmiş. Ban riski yaradan heç nə yoxdur. Ayda 49 $."),
 "pricing": ("ucuz instagram izləyici", "izləyici qiyməti · kartla ödəniş",
          "Ucuz Instagram izləyici? Ayda 49 $-a orqanik böyümə",
          "Ucuz izləyicilər yox olan botlardır. Ayda 49 $ ilə seçdiyiniz yerlərdən 900–3.000 real, orqanik izləyici. Kart, Apple Pay, Google Pay."),
 "guide_buy": ("instagram izləyici almaq təhlükəsizdirmi", "qanunidirmi · ban · işə yarayırmı",
          "Instagram izləyici almaq təhlükəsizdirmi? Orqanik alternativ",
          "İzləyici almaq olarmı, işə yarayırmı, ban riski varmı? Səmimi cavablar və real izləyiciləri orqanik böyütməyin yolu."),
 "guide_speed": ("instagram izləyici artırmaq", "1000 izləyici · 10 min · sürətli",
          "Instagram-da ayda neçə izləyici orqanik qazanmaq olar?",
          "1.000-dən 10.000-ə: orqanik böyümənin real rəqəmləri. Müştərilərimiz ayda orta hesabla 900–3.000 real izləyici qazanır, bot olmadan."),
})

ORDER = ["en", "tr", "de", "nl", "fr", "it", "es", "pl", "ru", "uk", "ar", "sv", "da", "no", "ro", "az"]
rows = []
for lang in ORDER:
    base, subs, pages = P[lang]
    prefix = "" if lang == "tr" else f"/{lang}"
    for page in ("main", "pricing", "guide_buy", "guide_speed"):
        kw, sec, title, desc = pages[page]
        url = f"{prefix}/{base}/" if page == "main" else f"{prefix}/{base}/{subs[page]}/"
        rows.append([lang, page, url, kw, sec, title, len(title), desc, len(desc)])
    if lang == "en":
        for g, (kw, sec, title, adj) in GEO_EN.items():
            desc = f"Location-targeted organic Instagram growth for {adj} accounts: 900–3,000 real followers a month from the audience you choose. No bots. $49/month."
            rows.append([lang, f"geo_{g}", f"/en/{base}/{g}/", kw, sec, title, len(title), desc, len(desc)])
assert len(ORDER) == len(P) == 16
with open(sys.argv[1], "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["lang", "page", "url", "primary_keyword", "secondary_keywords", "meta_title", "title_len", "meta_description", "desc_len"])
    w.writerows(rows)
long_t = [(r[0], r[1], r[6]) for r in rows if r[6] > 66]
long_d = [(r[0], r[1], r[8]) for r in rows if r[8] > 160]
no_org = [(r[0], r[1]) for r in rows if not any(w in (r[5] + r[7]).lower() for w in ("organi", "orgáni", "طبيعي", "органі", "органи", "orqanik"))]
print(len(rows), "pages; long titles", long_t, "; long descs", long_d, "; missing organic", no_org)
