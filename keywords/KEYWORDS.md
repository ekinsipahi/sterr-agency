# Sterr Agency — Anahtar Kelime Haritası

> Kaynak: Eylül 2026 keyword araştırması (Türkiye, Türkçe). Hacim = aylık arama, CPC = tıklama başı maliyet, PD = ücretli rekabet, SD = SEO zorluğu.
> Araç verileri "Outdated" olarak işaretliydi; yayından sonra Search Console ve Google Ads Keyword Planner ile yeniden doğrulanmalı.

**Strateji tek cümleyle:** Satın alma niyeti taşıyan her keyword'ü **81 il ile çarpıp** kendi landing sayfasına bağlıyoruz; bilgi arayan keyword'leri **rehberlere** topluyoruz; iş arayan ve rakip marka aramalarını **bilerek dışarıda bırakıyoruz**.

| Dosya | İçerik |
|---|---|
| `KEYWORDS.md` | Bu doküman: kümeler, niyet, hedef URL, kurallar |
| `il_keyword_varyasyonlari.csv` | **3.492 satır**: her ticari keyword × 81 il × 3 yazım (keyword + il · il + keyword · Türkçe karaktersiz) → hedef URL |
| `pseo_sayfalar.csv` | **324 sayfa**: URL, meta title, meta description, H1, uzunluklar, hedeflenen keyword'ler |

CSV'leri yeniden üretmek için (canlı domain'le): `SITE_URL=https://alanadiniz.com python manage.py export_keywords`

---

## 1. Keyword kümeleri → hedef sayfa

Niyet: **T** = satın alma (transactional) · **C** = ticari araştırma · **I** = bilgi · **N** = marka/navigasyon

### Küme A — Dijital Pazarlama Ajansı · `/dijital-pazarlama-ajansi/` + 81 il

| Keyword | Hacim | CPC | PD | SD | Niyet | Hedef |
|---|---:|---:|---:|---:|:-:|---|
| **dijital pazarlama ajansı** | **2.4K** | ₺125.32 | 48 | 28 | T | `/dijital-pazarlama-ajansi/` + ana sayfa |
| dijital pazarlama ajansı istanbul | 70 | ₺127.03 | 62 | 24 | T | `/dijital-pazarlama-ajansi/istanbul/` |
| dijital pazarlama ajansı izmir | 30 | — | 4 | 7 | T | `/dijital-pazarlama-ajansi/izmir/` |
| dijital pazarlama ajansı ankara | 20 | ₺105.04 | 60 | 24 | T | `/dijital-pazarlama-ajansi/ankara/` |
| dijital pazarlama ajansı antalya | — | — | — | — | T | `/dijital-pazarlama-ajansi/antalya/` |
| dijital pazarlama ajansı bursa | — | — | — | — | T | `/dijital-pazarlama-ajansi/bursa/` |
| sakarya dijital pazarlama ajansı | — | — | — | — | T | `/dijital-pazarlama-ajansi/sakarya/` |
| mersin dijital pazarlama ajansı | — | — | — | — | T | `/dijital-pazarlama-ajansi/mersin/` |
| dijital pazarlama ajansı fiyatları | — | — | — | — | C | `/rehber/dijital-pazarlama-ajansi-fiyatlari/` + il sayfalarında fiyat bölümü |

### Küme B — Sosyal Medya Ajansı · `/sosyal-medya-ajansi/` + 81 il

| Keyword | Hacim | CPC | PD | SD | Niyet | Hedef |
|---|---:|---:|---:|---:|:-:|---|
| **sosyal medya ajansı** | **2.4K** | ₺115.06 | 44 | 27 | T | `/sosyal-medya-ajansi/` |
| **sosyal medya ajansları** | **2.4K** | ₺115.06 | 44 | 27 | T | `/sosyal-medya-ajansi/` (çoğul, aynı sayfa) |
| sosyal medya ajans | 140 | ₺103.33 | 57 | 31 | T | `/sosyal-medya-ajansi/` |
| sosyal medya ajansı ankara | 70 | **₺189.56** | 48 | 20 | T | `/sosyal-medya-ajansi/ankara/` |
| sosyal medya ajansı istanbul | 70 | ₺95.27 | 56 | 22 | T | `/sosyal-medya-ajansi/istanbul/` |
| sosyal medya ajansı izmir | 50 | ₺148.52 | 46 | 19 | T | `/sosyal-medya-ajansi/izmir/` |
| sosyal medya ajansları istanbul | — | — | — | — | T | `/sosyal-medya-ajansi/istanbul/` |
| ankara sosyal medya ajans | — | — | — | — | T | `/sosyal-medya-ajansi/ankara/` |
| antalya sosyal medya ajans | — | — | — | — | T | `/sosyal-medya-ajansi/antalya/` |
| bursa sosyal medya ajans | — | — | — | — | T | `/sosyal-medya-ajansi/bursa/` |
| eskişehir sosyal medya ajans | — | — | — | — | T | `/sosyal-medya-ajansi/eskisehir/` |
| sosyal medya ajans izmir | — | — | — | — | T | `/sosyal-medya-ajansi/izmir/` |
| sosyal medya ajansı fiyatları | 30 | ₺57.89 | 60 | 24 | C | `/rehber/sosyal-medya-ajansi-fiyatlari/` + il sayfalarında fiyat bölümü |
| sosyal medya ajans fiyatları | — | — | — | — | C | `/rehber/sosyal-medya-ajansi-fiyatlari/` |
| sosyal medya ajans ücretleri | — | — | — | — | C | `/rehber/sosyal-medya-ajansi-fiyatlari/` |

### Küme C — Sosyal Medya Yönetimi Ajansı · `/sosyal-medya-yonetimi-ajansi/` + 81 il

| Keyword | Hacim | CPC | PD | SD | Niyet | Hedef |
|---|---:|---:|---:|---:|:-:|---|
| sosyal medya yönetimi ajans | 30 | ₺84.76 | 69 | 26 | T | `/sosyal-medya-yonetimi-ajansi/` |

### Küme D — Dijital Pazarlama Uzmanı · `/dijital-pazarlama-uzmani/` + 81 il

Bu kümeyi **"tek uzman yerine ekip"** açısıyla işliyoruz: aramayı yapan işletme sahibini yakalıyoruz, iş arayanı değil.

| Keyword | Hacim | CPC | PD | SD | Niyet | Hedef |
|---|---:|---:|---:|---:|:-:|---|
| **dijital pazarlama uzmanı** | **720** | ₺46.17 | 41 | 26 | C | `/dijital-pazarlama-uzmani/` |
| dijital pazarlama uzmani | 720 | ₺46.17 | 41 | 26 | C | aynı sayfa (Türkçe karaktersiz yazım) |
| dijital pazarlama uzmanları | 720 | ₺46.17 | 41 | 26 | C | aynı sayfa (çoğul) |
| dijital pazarlama uzman | 70 | ₺30.05 | 43 | 26 | C | aynı sayfa |

### Küme E — Bilgi niyeti → Rehberler (`/rehber/…`)

| Keyword | Hacim | CPC | Niyet | Hedef rehber |
|---|---:|---:|:-:|---|
| dijital pazarlama uzmanı ne iş yapar | 170 | ₺28.58 | I | `/rehber/dijital-pazarlama-uzmani-nedir/` |
| dijital pazarlama uzmanı nedir | 140 | ₺19.30 | I | `/rehber/dijital-pazarlama-uzmani-nedir/` |
| dijital pazarlama uzmanlığı | 70 | ₺30.05 | I | `/rehber/dijital-pazarlama-uzmani-nedir/` |
| dijital pazarlama uzmanlığı nedir | — | — | I | `/rehber/dijital-pazarlama-uzmani-nedir/` |
| sosyal medya ajansı nedir | 40 | ₺34.93 | I | `/rehber/sosyal-medya-ajansi-nedir/` |
| sosyal medya ajansı ne yapar | — | — | I | `/rehber/sosyal-medya-ajansi-nedir/` |
| sosyal medya ajansı ne demek | — | — | I | `/rehber/sosyal-medya-ajansi-nedir/` |
| dijital pazarlama ajansı ne iş yapar | — | — | I | `/rehber/dijital-pazarlama-ajansi-ne-is-yapar/` |
| sosyal medya ajans sözleşmesi | — | — | C | `/rehber/sosyal-medya-ajans-sozlesmesi/` |

Rehberler il sayfalarına ve paketlere iç link verir; il sayfaları da ilgili rehberlere geri bağlanır.

---

## 2. İl varyasyonları — 81 il × 15 ticari keyword

Aşağıdaki 15 ana keyword, 81 ilin tamamıyla ve 3 yazım biçimiyle çoğaltıldı (`il_keyword_varyasyonlari.csv`, **3.492 satır**; yazımı zaten ASCII olan tekrarlar çıkarıldı).

| # | Ana keyword | Hedef küme sayfası |
|---|---|---|
| 1 | dijital pazarlama ajansı | `/dijital-pazarlama-ajansi/{il}/` |
| 2 | dijital pazarlama ajansları | `/dijital-pazarlama-ajansi/{il}/` |
| 3 | dijital pazarlama ajansı fiyatları | `/dijital-pazarlama-ajansi/{il}/` |
| 4 | dijital ajans | `/dijital-pazarlama-ajansi/{il}/` |
| 5 | sosyal medya ajansı | `/sosyal-medya-ajansi/{il}/` |
| 6 | sosyal medya ajansları | `/sosyal-medya-ajansi/{il}/` |
| 7 | sosyal medya ajans | `/sosyal-medya-ajansi/{il}/` |
| 8 | sosyal medya ajansı fiyatları | `/sosyal-medya-ajansi/{il}/` |
| 9 | sosyal medya ajans fiyatları | `/sosyal-medya-ajansi/{il}/` |
| 10 | sosyal medya ajans ücretleri | `/sosyal-medya-ajansi/{il}/` |
| 11 | sosyal medya yönetimi ajansı | `/sosyal-medya-yonetimi-ajansi/{il}/` |
| 12 | sosyal medya yönetimi | `/sosyal-medya-yonetimi-ajansi/{il}/` |
| 13 | dijital pazarlama uzmanı | `/dijital-pazarlama-uzmani/{il}/` |
| 14 | dijital pazarlama uzmanları | `/dijital-pazarlama-uzmani/{il}/` |
| 15 | dijital pazarlama uzman | `/dijital-pazarlama-uzmani/{il}/` |

### Varyasyon kuralları

| Kural | Örnek | Neden |
|---|---|---|
| keyword + il | sosyal medya ajansı **ankara** | Araştırmadaki en yaygın kalıp |
| il + keyword | **ankara** sosyal medya ajans | Araştırmada ayrıca geçiyor (ankara/antalya/bursa/eskişehir/sakarya/mersin) |
| Türkçe karaktersiz | sosyal medya ajans**i** **eskisehir** | "uzmani", "ajansi" aramaları aynı hacmi taşıyor (720 = 720) |
| Tekil / çoğul | ajans**ı** / ajans**ları** | "sosyal medya ajansları" = 2.4K, tekille aynı |
| Fiyat son eki | … **fiyatları** / **ücretleri** | Aynı il sayfasındaki "{il} … fiyatları" bölümü karşılıyor |

**Yamyamlığı (cannibalization) önleme kuralı:** bir il + küme için **tek sayfa** vardır. Tekil, çoğul, ASCII, sıra ve fiyat varyasyonlarının hepsi o sayfayı hedefler; ayrı sayfa açılmaz.

---

## 3. Programatik SEO — 4 küme × 81 il = 324 landing sayfası

| Küme | Hub | İl sayfası kalıbı |
|---|---|---|
| Dijital Pazarlama Ajansı | `/dijital-pazarlama-ajansi/` | `/dijital-pazarlama-ajansi/istanbul/` |
| Sosyal Medya Ajansı | `/sosyal-medya-ajansi/` | `/sosyal-medya-ajansi/ankara/` |
| Sosyal Medya Yönetimi Ajansı | `/sosyal-medya-yonetimi-ajansi/` | `/sosyal-medya-yonetimi-ajansi/izmir/` |
| Dijital Pazarlama Uzmanı | `/dijital-pazarlama-uzmani/` | `/dijital-pazarlama-uzmani/bursa/` |

### Meta title / description kuralları (kodda: `apps/seo/services.py`)

- **Title ≤ 60 karakter.** Önce "kanca"lı şablon denenir (ör. *"… | Müşteri Getiren Sistem"*, *"… | Takipçi Değil Müşteri"*). İl adı uzunsa (Afyonkarahisar, Kahramanmaraş) otomatik olarak daha kısa şablona düşer.
- **Description ≤ 158 karakter**, her ilde 3 şablondan biri hash ile seçilir. Böylece komşu iller aynı metni paylaşmaz. **324 sayfada tekrar eden title veya description sıfır** (test: `apps/seo/tests.py`).
- Türkçe ekler doğru çekilir: İstanbul'**da**, İzmir'**de**, Muş'**ta**, Gaziantep'**te**, Ankara'**nın**, Bingöl'**ün**.
- Her description bir **fayda** + bir **ayırt edici unsur** (beğeni değil müşteri / ekip gelir / 50.000 ₺'den) + bir **eylem çağrısı** içerir.

Örnekler:

| Sayfa | Title | Description |
|---|---|---|
| İstanbul · DPA | İstanbul Dijital Pazarlama Ajansı \| Müşteri Getiren Sistem (58) | İstanbul'da işletmenize müşteri getiren dijital pazarlama. Reklam + SEO + AI destekli içerik yayılımı. Paketler aylık 50.000 ₺'den. |
| Afyonkarahisar · SMA | Afyonkarahisar Sosyal Medya Ajansı \| Takipçi Değil Müşteri (58) | Afyonkarahisar sosyal medya ajansı Sterr: Instagram, TikTok ve Meta reklamlarını satışa bağlayan strateji. Aylık rapor, net hedef, 81 ilde hizmet. |
| Muş · Uzman | Muş Dijital Pazarlama Uzmanı \| Tek Kişi Değil, Ekip (51) | Muş'taki işletmenize kıdemli dijital pazarlama uzmanları. Google, Meta, SEO ve içerik — aylık rapor, net hedef. Paketler 50.000 ₺'den. |

### Sayfaları özgün kılan unsurlar ("thin content" koruması)

1. **Giriş paragrafı:** küme başına 3 farklı metin, ile göre dönüşümlü.
2. **Pazar büyüklüğü metni:** metro (İstanbul/Ankara/İzmir) · büyük şehir (22 il) · gelişen pazar (56 il) için farklı argüman.
3. **Bölge metni:** 7 coğrafi bölgenin her biri için ayrı pazar tanımı.
4. **İle özel SSS**, `FAQPage` şeması ile.
5. **Kapanış paragrafı:** çoğul ve fiyat varyasyonlarını doğal cümle içinde kullanır.
6. **İç linkler:** aynı bölgedeki iller + aynı ildeki diğer 3 hizmet + ilgili rehberler + hub.
7. **Şemalar:** `Service` (areaServed = City), `BreadcrumbList`, `FAQPage`, `ProfessionalService`.

---

## 4. Bilerek hedeflenmeyen keyword'ler

Bunlar trafik getirir ama **müşteri getirmez**. Funnel'ımız kalite odaklı olduğu için landing sayfalarına alınmadı.

| Keyword | Hacim | Neden hariç | Olası kullanım |
|---|---:|---|---|
| dijital pazarlama uzmanı maaşları / maaş / maaş 2025 | 320 | İş arayan niyeti | — |
| dijital pazarlama uzmanı iş ilanları / iş ilanı | 140 / 30 | İş arayan | İleride "Kariyer" sayfası |
| dijital pazarlama uzman yardımcısı (+ iş ilanları, maaş) | — | İş arayan | Kariyer sayfası |
| dijital pazarlama ajansı / sosyal medya ajansı iş ilanları | — | İş arayan | Kariyer sayfası |
| dijital pazarlama uzmanı nasıl olunur / hangi bölüm / eğitimi / sertifikası | 140 / 30 / 30 | Öğrenci / kariyer | — |
| dijital pazarlama uzmanlığı taban puanları | — | Üniversite adayı | — |
| sosyal medya ajansı kurmak / nasıl kurulur / kurmak için gerekenler | — | Rakip olmak isteyen | — |
| dijital pazarlama ajansı kurmak / nace kodu | — | Rakip / muhasebe | — |
| sosyal medya ajans isimleri / isim önerileri | 70 | Rakip olmak isteyen | — |
| adsera / bs / romeo / joker … ajans | 140 / 40 | Rakip marka (navigasyon) | Reklamda negatif keyword |
| dijital pazarlama ajansı ekşi | — | Forum / itibar araştırması | AI yayılım çalışmasında izlenecek kanal |

> **Google Ads notu:** Yukarıdaki iş/kariyer/kurmak/maaş kelimeleri reklam kampanyalarına **negatif keyword** olarak eklenmeli. Aksi halde 125 ₺'lik tıklamalar iş arayanlara gider.

---

## 5. Öncelik sırası (reklam + SEO)

| Öncelik | Neden | Sayfalar |
|---|---|---|
| 1 | En yüksek hacim + ticari niyet | `/sosyal-medya-ajansi/`, `/dijital-pazarlama-ajansi/` |
| 2 | Yüksek CPC = yüksek ticari değer; SEO ile ücretsiz trafik | Ankara (₺189.56), İzmir (₺148.52), İstanbul (₺127) il sayfaları |
| 3 | Düşük SEO zorluğu (SD 7), hızlı kazanım | `/dijital-pazarlama-ajansi/izmir/` |
| 4 | Uzun kuyruk: 81 il | Kalan il sayfaları, iç linklerle desteklenir |
| 5 | Güven ve iç link | 6 rehber |

## 6. Yayından sonra yapılacaklar

- [ ] `SITE_URL` canlı domain olarak ayarlanınca `export_keywords` yeniden çalıştırılmalı.
- [ ] Search Console'a `/sitemap.xml` gönderilmeli (354 URL).
- [ ] Hacmi "—" olan keyword'ler Keyword Planner'da doğrulanmalı. Hacimsiz çıkan il sayfaları noindex yapılmamalı; uzun kuyrukta dönüşüm getirirler.
- [ ] 3. ayda Search Console'dan gösterim alan fakat tıklanmayan il sayfalarının title'ları test edilmeli.
- [ ] Önerilen ek kümeler (araştırmada yok, hacmi doğrulanmalı): *seo ajansı {il}*, *google reklam ajansı {il}*, *reklam ajansı {il}*, *e-ticaret ajansı {il}*. Kod yapısı hazır; `apps/seo/services.py` içindeki `CLUSTERS` listesine bir küme eklemek 81 sayfayı otomatik üretir.


---

## 7. Küme F — Diş turizmi acentesi (16 dil) · `/dental-tourism/`

Kaynak: dental_tourism projesindeki keyword araştırması, grup **5. Ajans, sigorta ve süreç aramaları (B2B ortaklık ve SSS)**.
Acente mantığı: hastayı ruhsatlı partner kliniğe yönlendiriyoruz (hub), kliniklere ve yabancı acentelere B2B iş birliği sunuyoruz (iş birliği sayfası), sigorta/garanti/süreç sorularını SSS formatında cevaplıyoruz (sigorta sayfası).

- **3 sayfa × 16 dil = 48 sayfa.** İngilizce `x-default` ve `/dental-tourism/` altında; diğer diller `/dental-tourism/<dil>/`.
- Her sayfada 16 dil + x-default `hreflang`, sitemap'te `xhtml:link` alternatifleri, FAQPage şeması.
- Fiyat rakamı yok (dental_tourism kuralıyla aynı): "yazılı sabit teklif" vurgusu.
- İçerik: `apps/dental/locales/<dil>.py`. Testler her dilin İngilizceyle aynı yapıda olduğunu ve title/description uzunluklarını kontrol ediyor.
- Navbar'daki bayraklı dil menüsü: Türkçe = ana site, diğer diller = bu kümenin o dildeki sayfası.

| Dil | Acente (hub) · İş birliği | Hedef keyword'ler | Sigorta & süreç | Hedef keyword'ler |
|---|---|---|---|---|
| en | `/dental-tourism/` · `/dental-tourism/partners/` | dental tourism agency (110, PD 16), dental tourism agency turkey, dental tourism facilitator turkey | `/dental-tourism/insurance/` | best dental tourism insurance, dental travel insurance turkey |
| de | `/dental-tourism/de/` · `/dental-tourism/de/partner/` | zahntourismus agentur, zahnreise türkei agentur | `/dental-tourism/de/versicherung/` | zahnbehandlung türkei versicherung, zahnbehandlung türkei ablauf |
| nl | `/dental-tourism/nl/` · `/dental-tourism/nl/partners/` | tandartsreis bureau turkije, tandheelkundig toerisme | `/dental-tourism/nl/verzekering/` | tandarts turkije verzekering |
| fr | `/dental-tourism/fr/` · `/dental-tourism/fr/partenaires/` | agence tourisme dentaire turquie | `/dental-tourism/fr/assurance/` | soins dentaires turquie assurance |
| it | `/dental-tourism/it/` · `/dental-tourism/it/partner/` | agenzia turismo dentale turchia | `/dental-tourism/it/assicurazione/` | assicurazione cure dentali turchia |
| es | `/dental-tourism/es/` · `/dental-tourism/es/socios/` | agencia turismo dental turquía | `/dental-tourism/es/seguro/` | seguro tratamiento dental turquía |
| pl | `/dental-tourism/pl/` · `/dental-tourism/pl/partnerzy/` | agencja turystyki dentystycznej | `/dental-tourism/pl/ubezpieczenie/` | ubezpieczenie leczenie zębów turcja |
| ru | `/dental-tourism/ru/` · `/dental-tourism/ru/partnery/` | агентство стоматологического туризма | `/dental-tourism/ru/strakhovka/` | страховка лечение зубов турция |
| uk | `/dental-tourism/uk/` · `/dental-tourism/uk/partnery/` | агентство стоматологічного туризму | `/dental-tourism/uk/strakhuvannya/` | страхування лікування зубів туреччина |
| ar | `/dental-tourism/ar/` · `/dental-tourism/ar/shuraka/` | وكالة السياحة العلاجية للأسنان في تركيا | `/dental-tourism/ar/taamin/` | تأمين السياحة العلاجية للأسنان |
| sv | `/dental-tourism/sv/` · `/dental-tourism/sv/partner/` | tandturism byrå | `/dental-tourism/sv/forsakring/` | försäkring tandvård turkiet |
| da | `/dental-tourism/da/` · `/dental-tourism/da/partnere/` | tandturisme bureau | `/dental-tourism/da/forsikring/` | forsikring tandbehandling tyrkiet |
| no | `/dental-tourism/no/` · `/dental-tourism/no/partnere/` | tannturisme byrå | `/dental-tourism/no/forsikring/` | forsikring tannbehandling tyrkia |
| ro | `/dental-tourism/ro/` · `/dental-tourism/ro/parteneri/` | agenție turism dentar | `/dental-tourism/ro/asigurare/` | asigurare tratament dentar turcia |
| az | `/dental-tourism/az/` · `/dental-tourism/az/terefdaslar/` | diş turizmi agentliyi | `/dental-tourism/az/sigorta/` | diş müalicəsi sığorta türkiyə |
| tr | `/dental-tourism/tr/` · `/dental-tourism/tr/is-birligi/` | diş turizmi acentesi, sağlık turizmi acentesi iş birliği | `/dental-tourism/tr/sigorta/` | diş turizmi sigortası |

> Not: Aynı keyword'leri dentaltourism.tr de hedefliyor. İki site birbirinin rakibi olmasın diye
> dentaltourism.tr "kliniğin kendisi", sterragency.com "acente + B2B ortaklık" açısından yazıldı; iki site birbirine link verebilir.
