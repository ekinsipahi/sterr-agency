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

**Sadece "acente" arayanlar hedefleniyor** ("dental tourism agency" ve dillerdeki karşılıkları). Sigorta, fiyat,
tedavi ve genel "dental tourism" bilgi aramaları bilerek hedeflenmiyor; onlar dentaltourism.tr'nin işi.

- **2 sayfa × 16 dil = 32 sayfa.** İngilizce `x-default`, `/dental-tourism/` altında; diğer diller `/dental-tourism/<dil>/`.
  - **Acente sayfası (hub):** "dental tourism agency turkey" arayan hasta. Tek muhatap, yazılı plan, partner klinik.
  - **İş birliği sayfası:** "dental tourism agency" arayan klinik / acente. B2B ortaklık, 16 dilde hasta kazanımı.
- Her sayfada 16 dil + x-default `hreflang`, sitemap'te `xhtml:link` alternatifleri, FAQPage şeması.
- Fiyat rakamı yok. İçerik: `apps/dental/locales/<dil>.py`.
- Navbar'daki bayraklı dil menüsü: Türkçe = ana site, diğer diller = bu kümenin o dildeki acente sayfası.

| Dil | Acente sayfası | Hedef keyword'ler | İş birliği sayfası | Hedef keyword'ler |
|---|---|---|---|---|
| en | `/dental-tourism/` | dental tourism agency turkey, dental tourism facilitator turkey | `/dental-tourism/partners/` | dental tourism agency (110, PD 16), dental tourism agency partnership |
| de | `/dental-tourism/de/` | zahntourismus agentur türkei, zahnreise türkei agentur | `/dental-tourism/de/partner/` | zahntourismus agentur, zahntourismus agentur partner |
| nl | `/dental-tourism/nl/` | tandartsreis bureau turkije | `/dental-tourism/nl/partners/` | bureau tandheelkundig toerisme |
| fr | `/dental-tourism/fr/` | agence tourisme dentaire turquie | `/dental-tourism/fr/partenaires/` | agence de tourisme dentaire, partenariat |
| it | `/dental-tourism/it/` | agenzia turismo dentale turchia | `/dental-tourism/it/partner/` | agenzia di turismo dentale, partner |
| es | `/dental-tourism/es/` | agencia turismo dental turquía | `/dental-tourism/es/socios/` | agencia de turismo dental, socios |
| pl | `/dental-tourism/pl/` | agencja turystyki dentystycznej turcja | `/dental-tourism/pl/partnerzy/` | agencja turystyki dentystycznej, współpraca |
| ru | `/dental-tourism/ru/` | агентство стоматологического туризма в турции | `/dental-tourism/ru/partnery/` | агентство стоматологического туризма, партнёрство |
| uk | `/dental-tourism/uk/` | агентство стоматологічного туризму в туреччині | `/dental-tourism/uk/partnery/` | агентство стоматологічного туризму, партнерство |
| ar | `/dental-tourism/ar/` | وكالة السياحة العلاجية للأسنان في تركيا | `/dental-tourism/ar/shuraka/` | وكالة السياحة العلاجية للأسنان، شراكة |
| sv | `/dental-tourism/sv/` | tandturismbyrå turkiet | `/dental-tourism/sv/partner/` | tandturism byrå, partner |
| da | `/dental-tourism/da/` | tandturisme bureau tyrkiet | `/dental-tourism/da/partnere/` | tandturisme bureau, partner |
| no | `/dental-tourism/no/` | tannturisme byrå tyrkia | `/dental-tourism/no/partnere/` | tannturisme byrå, partner |
| ro | `/dental-tourism/ro/` | agenție turism dentar turcia | `/dental-tourism/ro/parteneri/` | agenție turism dentar, parteneriat |
| az | `/dental-tourism/az/` | türkiyədə diş turizmi agentliyi | `/dental-tourism/az/terefdaslar/` | diş turizmi agentliyi, tərəfdaşlıq |
| tr | `/dental-tourism/tr/` | diş turizmi acentesi | `/dental-tourism/tr/is-birligi/` | sağlık turizmi acentesi iş birliği, diş turizmi acentesi iş birliği |

> Not: dentaltourism.tr "kliniğin kendisi" olarak bilgi/tedavi aramalarını alır; sterragency.com yalnızca acente
> aramalarını hedefler. Böylece iki site aynı sorgu için birbiriyle yarışmaz.

---

## 8. Uluslararası ajans — 15 dil × 19 sayfa = 285 sayfa (il bazlı pSEO yok)

İl bazlı programatik sayfalar yabancı dillerde **bilerek yapılmadı** (spam riski). Her dil için: ülke ana sayfası, 4 hizmet kümesi,
sektörler listesi + 6 sektör, rehber listesi + 6 rehber. Her sayfa Türkçe karşılığına ve diğer 14 dile `hreflang` ile bağlı (x-default = İngilizce).
İçerik: `apps/intl/locales/<dil>.py`. Fiyat: admin → Pazar fiyatları (USD), güncel kurla yerel paraya çevrilir.

### Pazar ve fiyat politikası

| Dil | Pazar | Para birimi | Başlangıç (USD/ay) |
|---|---|---|---|
| en | International (US, UK, …) | USD | 1000 |
| de | Deutschland, Österreich, Schweiz | EUR | 1000 |
| nl | Nederland, België | EUR | 1000 |
| fr | France, Belgique | EUR | 1000 |
| it | Italia | EUR | 1000 |
| es | España | EUR | 1000 |
| pl | Polska | PLN | 900 |
| ru | Россия | RUB | 900 |
| uk | Україна | UAH | 900 |
| ar | Gulf / Arab countries | SAR | 1000 |
| sv | Sverige | SEK | 1000 |
| da | Danmark | DKK | 1000 |
| no | Norge | NOK | 1000 |
| ro | România | RON | 900 |
| az | Azərbaycan | AZN | 900 |

Paket kademeleri Türkiye'deki oranlarla aynı: başlangıç × 1 / × 1,8 / × 3 ("başlayan").

### Hizmet kümeleri (Türkçe ana keyword → her dildeki karşılık ve URL)

| Dil | Dijital pazarlama ajansı | Sosyal medya ajansı | Sosyal medya yönetimi | Dijital pazarlama uzmanı |
|---|---|---|---|---|
| en | Digital Marketing Agency `/en/digital-marketing-agency/` | Social Media Agency `/en/social-media-agency/` | Social Media Management `/en/social-media-management/` | Digital Marketing Specialist `/en/digital-marketing-specialist/` |
| de | Online-Marketing-Agentur `/de/online-marketing-agentur/` | Social-Media-Agentur `/de/social-media-agentur/` | Social-Media-Betreuung `/de/social-media-betreuung/` | Online-Marketing-Experte `/de/online-marketing-experte/` |
| nl | Online marketing bureau `/nl/online-marketing-bureau/` | Social media bureau `/nl/social-media-bureau/` | Social media beheer `/nl/social-media-beheer/` | Online marketeer `/nl/online-marketeer/` |
| fr | Agence marketing digital `/fr/agence-marketing-digital/` | Agence social media `/fr/agence-social-media/` | Gestion des réseaux sociaux `/fr/gestion-reseaux-sociaux/` | Consultant marketing digital `/fr/consultant-marketing-digital/` |
| it | Agenzia di marketing digitale `/it/agenzia-marketing-digitale/` | Agenzia social media `/it/agenzia-social-media/` | Gestione social media `/it/gestione-social-media/` | Consulente di marketing digitale `/it/consulente-marketing-digitale/` |
| es | Agencia de marketing digital `/es/agencia-de-marketing-digital/` | Agencia de redes sociales `/es/agencia-de-redes-sociales/` | Gestión de redes sociales `/es/gestion-de-redes-sociales/` | Especialista en marketing digital `/es/especialista-en-marketing-digital/` |
| pl | Agencja marketingu internetowego `/pl/agencja-marketingu-internetowego/` | Agencja social media `/pl/agencja-social-media/` | Prowadzenie social media `/pl/prowadzenie-social-media/` | Specjalista marketingu internetowego `/pl/specjalista-marketingu-internetowego/` |
| ru | Агентство интернет-маркетинга `/ru/agentstvo-internet-marketinga/` | SMM-агентство `/ru/smm-agentstvo/` | Ведение соцсетей `/ru/vedenie-socsetey/` | Интернет-маркетолог `/ru/internet-marketolog/` |
| uk | Агенція інтернет-маркетингу `/uk/agentsiia-internet-marketynhu/` | SMM-агенція `/uk/smm-agentsiia/` | Ведення соцмереж `/uk/vedennia-sotsmerezh/` | Інтернет-маркетолог `/uk/internet-marketoloh/` |
| ar | وكالة تسويق رقمي `/ar/wakalat-taswiq-raqmi/` | وكالة سوشيال ميديا `/ar/wakalat-social-media/` | إدارة حسابات التواصل الاجتماعي `/ar/idarat-hisabat-social-media/` | خبير تسويق رقمي `/ar/khabir-taswiq-raqmi/` |
| sv | Digital marknadsföringsbyrå `/sv/digital-marknadsforingsbyra/` | Byrå för sociala medier `/sv/sociala-medier-byra/` | Hantering av sociala medier `/sv/hantering-av-sociala-medier/` | Digital marknadsförare `/sv/digital-marknadsforare/` |
| da | Digitalt marketingbureau `/da/digitalt-marketingbureau/` | Social media bureau `/da/social-media-bureau/` | Håndtering af sociale medier `/da/haandtering-af-sociale-medier/` | Digital marketingekspert `/da/digital-marketingekspert/` |
| no | Digitalt markedsføringsbyrå `/no/digitalt-markedsforingsbyra/` | Byrå for sosiale medier `/no/sosiale-medier-byra/` | Administrasjon av sosiale medier `/no/administrasjon-av-sosiale-medier/` | Digital markedsfører `/no/digital-markedsforer/` |
| ro | Agenție de marketing digital `/ro/agentie-de-marketing-digital/` | Agenție social media `/ro/agentie-social-media/` | Administrare social media `/ro/administrare-social-media/` | Specialist marketing digital `/ro/specialist-marketing-digital/` |
| az | Rəqəmsal marketinq agentliyi `/az/reqemsal-marketinq-agentliyi/` | SMM agentliyi `/az/smm-agentliyi/` | Sosial media idarəetməsi `/az/sosial-media-idareetmesi/` | Rəqəmsal marketinq mütəxəssisi `/az/reqemsal-marketinq-mutexessisi/` |

### Rehberler (Türkçe rehber → her dilde H1)

| Dil | dijital-pazarlama-ajansi-ne-is-yapar | dijital-pazarlama-ajansi-fiyatlari | sosyal-medya-ajansi-nedir | sosyal-medya-ajansi-fiyatlari | sosyal-medya-ajans-sozlesmesi | dijital-pazarlama-uzmani-nedir |
|---|---|---|---|---|---|---|
| en | What does a digital marketing agency do? | Digital marketing agency pricing: a realistic budget for 2026 | What is a social media agency, and what does it do? | Social media agency pricing and fees | Social media agency contract: 10 clauses it must include | What is a digital marketing specialist, and what do they do? |
| de | Was macht eine Online-Marketing-Agentur? | Online-Marketing-Agentur Kosten: ein realistisches Budget für 2026 | Was ist eine Social-Media-Agentur, und was macht sie? | Social-Media-Agentur Kosten und Preise | Social-Media-Agentur Vertrag: 10 Punkte, die er enthalten muss | Was ist ein Online-Marketing-Experte, und was macht er? |
| nl | Wat doet een online marketing bureau? | Kosten van een online marketing bureau: een realistisch budget voor 2026 | Wat is een social media bureau, en wat doet het? | Kosten en prijzen van een social media bureau | Contract met een social media bureau: 10 punten die erin moeten | Wat is een online marketeer, en wat doet die? |
| fr | Que fait une agence marketing digital ? | Tarif d'une agence marketing digital : un budget réaliste pour 2026 | Qu'est-ce qu'une agence social media, et que fait-elle ? | Tarifs et prix d'une agence social media | Contrat d'agence social media : 10 clauses indispensables | Qu'est-ce qu'un spécialiste marketing digital, et que fait-il ? |
| it | Cosa fa un'agenzia di marketing digitale? | Prezzi di un'agenzia di marketing digitale: un budget realistico per il 2026 | Cos'è un'agenzia social media, e cosa fa? | Prezzi e costi di un'agenzia social media | Contratto con un'agenzia social media: 10 clausole indispensabili | Cos'è un esperto di marketing digitale, e cosa fa? |
| es | ¿Qué hace una agencia de marketing digital? | Precios de una agencia de marketing digital: un presupuesto realista para 2026 | ¿Qué es una agencia de redes sociales y qué hace? | Precios y tarifas de una agencia de redes sociales | Contrato con una agencia de redes sociales: 10 cláusulas imprescindibles | ¿Qué es un especialista en marketing digital y qué hace? |
| pl | Czym zajmuje się agencja marketingu internetowego? | Ile kosztuje agencja marketingu internetowego: realny budżet na 2026 | Czym jest agencja social media i czym się zajmuje? | Cennik i koszty agencji social media | Umowa z agencją social media: 10 punktów, które musi zawierać | Kim jest specjalista ds. marketingu internetowego i czym się zajmuje? |
| ru | Чем занимается агентство интернет-маркетинга? | Стоимость агентства интернет-маркетинга: реалистичный бюджет на 2026 год | Что такое SMM-агентство и чем оно занимается? | Стоимость и цены SMM-агентства | Договор со SMM-агентством: 10 обязательных пунктов | Кто такой интернет-маркетолог и чем он занимается? |
| uk | Чим займається агенція інтернет-маркетингу? | Вартість агенції інтернет-маркетингу: реалістичний бюджет на 2026 рік | Що таке SMM-агенція і чим вона займається? | Вартість і ціни SMM-агенції | Договір зі SMM-агенцією: 10 обов'язкових пунктів | Хто такий інтернет-маркетолог і чим він займається? |
| ar | ماذا تفعل وكالة التسويق الرقمي؟ | أسعار وكالة التسويق الرقمي: ميزانية واقعية لعام 2026 | ما هي وكالة السوشيال ميديا، وماذا تفعل؟ | أسعار وتكاليف وكالة السوشيال ميديا | عقد وكالة السوشيال ميديا: 10 بنود لا غنى عنها | من هو خبير التسويق الرقمي، وماذا يفعل؟ |
| sv | Vad gör en digital marknadsföringsbyrå? | Pris för en digital marknadsföringsbyrå: en realistisk budget för 2026 | Vad är en byrå för sociala medier, och vad gör den? | Priser och kostnader för en byrå för sociala medier | Avtal med en byrå för sociala medier: 10 punkter som måste finnas | Vad är en digital marknadsförare, och vad gör hen? |
| da | Hvad laver et digitalt marketingbureau? | Pris på et digitalt marketingbureau: et realistisk budget for 2026 | Hvad er et social media bureau, og hvad laver det? | Priser og omkostninger for et social media bureau | Kontrakt med et social media bureau: 10 punkter, den skal have | Hvad er en digital marketingekspert, og hvad laver vedkommende? |
| no | Hva gjør et digitalt markedsføringsbyrå? | Pris på et digitalt markedsføringsbyrå: et realistisk budsjett for 2026 | Hva er et byrå for sosiale medier, og hva gjør det? | Priser og kostnader for et byrå for sosiale medier | Kontrakt med et byrå for sosiale medier: 10 punkter den må ha | Hva er en digital markedsfører, og hva gjør vedkommende? |
| ro | Ce face o agenție de marketing digital? | Prețurile unei agenții de marketing digital: un buget realist pentru 2026 | Ce este o agenție social media și ce face? | Prețurile și costurile unei agenții social media | Contractul cu o agenție social media: 10 clauze obligatorii | Ce este un specialist în marketing digital și ce face? |
| az | Rəqəmsal marketinq agentliyi nə edir? | Rəqəmsal marketinq agentliyi qiymətləri: 2026 üçün real büdcə | SMM agentliyi nədir və nə edir? | SMM agentliyinin qiymətləri və xərcləri | SMM agentliyi ilə müqavilə: mütləq olmalı 10 bənd | Rəqəmsal marketinq mütəxəssisi kimdir və nə edir? |

### Sektörler (her dilde sayfadaki "müşterilerinizin aradıkları" keyword'leri)

- **en** · Private Tutors: private tutor near me, online tutor, maths tutor, GCSE tutor, SAT tutor · Math Tutors: maths tutor, online maths tutor, GCSE maths tutor, A-level maths tutor, SAT math prep · Physics Tutors: physics tutor, online physics tutor, A-level physics tutor, GCSE physics tutor, physics help online · E-commerce Brands: ecommerce marketing agency, google shopping ads, ecommerce SEO, start an online store, online sales · Clinics & Healthcare: dentist near me, dental clinic, aesthetic clinic, physiotherapist, dental implants · Professional Services: lawyer near me, accountant for small business, business consultant, interior designer, tax advisor
- **de** · Nachhilfelehrer: Nachhilfe in der Nähe, Online Nachhilfe, Nachhilfelehrer gesucht, Abitur Nachhilfe, Einzelnachhilfe Preise · Mathe-Nachhilfe: Mathe Nachhilfe, Mathe Nachhilfe online, Mathe Abitur Vorbereitung, Mathe Nachhilfe Gymnasium, Mathe Nachhilfe Preise · Physik-Nachhilfe: Physik Nachhilfe, Physik Nachhilfe online, Physik Abitur Vorbereitung, Physik Nachhilfe Oberstufe, Physik Hilfe online · E-Commerce-Marken: E-Commerce Agentur, Google Shopping Anzeigen, E-Commerce SEO, Online Shop erstellen lassen, Online verkaufen · Praxen & Kliniken: Zahnarzt in der Nähe, Zahnarztpraxis, ästhetische Klinik, Physiotherapie, Zahnimplantate · Dienstleister: Anwalt in der Nähe, Steuerberater für Selbstständige, Unternehmensberatung, Innenarchitekt, Fachanwalt Arbeitsrecht
- **nl** · Bijlesdocenten: bijles in de buurt, online bijles, bijlesdocent gezocht, examentraining, bijles prijzen · Bijles wiskunde: bijles wiskunde, online bijles wiskunde, examentraining wiskunde, wiskunde bijles havo vwo, bijles wiskunde prijs · Bijles natuurkunde: bijles natuurkunde, online bijles natuurkunde, examentraining natuurkunde, natuurkunde bijles vwo, natuurkunde hulp online · Webshops: e-commerce bureau, google shopping advertenties, webshop SEO, webshop laten maken, online verkopen · Klinieken & zorg: tandarts in de buurt, tandartspraktijk, esthetische kliniek, fysiotherapeut, tandimplantaten · Zakelijke dienstverleners: advocaat in de buurt, boekhouder voor zzp, bedrijfsadviseur, interieurontwerper, belastingadviseur
- **fr** · Professeurs particuliers: cours particuliers, cours en ligne, professeur particulier, soutien scolaire, préparation au bac · Cours de maths: cours de maths, cours de maths en ligne, prof de maths particulier, préparation bac maths, cours de maths prix · Cours de physique: cours de physique, cours de physique en ligne, prof de physique-chimie, préparation bac physique, aide physique en ligne · Marques e-commerce: agence e-commerce, publicité Google Shopping, SEO e-commerce, créer une boutique en ligne, vendre en ligne · Cliniques & santé: dentiste près de moi, cabinet dentaire, clinique esthétique, kinésithérapeute, implant dentaire · Professions libérales: avocat près de chez moi, expert-comptable, consultant en entreprise, architecte d'intérieur, conseiller fiscal
- **it** · Insegnanti privati: ripetizioni vicino a me, lezioni private online, insegnante privato, ripetizioni maturità, ripetizioni prezzi · Ripetizioni di matematica: ripetizioni di matematica, lezioni di matematica online, ripetizioni matematica maturità, insegnante di matematica privato, ripetizioni matematica prezzi · Ripetizioni di fisica: ripetizioni di fisica, lezioni di fisica online, ripetizioni fisica maturità, insegnante di fisica privato, aiuto fisica online · E-commerce: agenzia e-commerce, pubblicità Google Shopping, SEO e-commerce, aprire un negozio online, vendere online · Cliniche e sanità: dentista vicino a me, studio dentistico, clinica estetica, fisioterapista, impianti dentali · Studi professionali: avvocato vicino a me, commercialista, consulente aziendale, architetto d'interni, consulente fiscale
- **es** · Profesores particulares: clases particulares, clases online, profesor particular, clases de refuerzo, clases para selectividad · Clases de matemáticas: clases de matemáticas, clases de matemáticas online, profesor de matemáticas particular, matemáticas selectividad, clases de matemáticas precio · Clases de física: clases de física, clases de física online, profesor de física particular, física selectividad, ayuda con física online · Marcas de e-commerce: agencia ecommerce, anuncios Google Shopping, SEO para ecommerce, crear tienda online, vender por internet · Clínicas y salud: dentista cerca de mí, clínica dental, clínica estética, fisioterapeuta, implantes dentales · Servicios profesionales: abogado cerca de mí, asesoría para autónomos, consultor de empresas, interiorista, asesor fiscal
- **pl** · Korepetytorzy: korepetycje w pobliżu, korepetycje online, korepetytor, korepetycje do matury, korepetycje cena · Korepetycje z matematyki: korepetycje z matematyki, korepetycje z matematyki online, matematyka matura korepetycje, nauczyciel matematyki korepetycje, korepetycje z matematyki cena · Korepetycje z fizyki: korepetycje z fizyki, korepetycje z fizyki online, fizyka matura korepetycje, nauczyciel fizyki korepetycje, pomoc z fizyki online · Sklepy internetowe: agencja e-commerce, reklamy Google Shopping, SEO sklepu internetowego, założenie sklepu internetowego, sprzedaż online · Kliniki i gabinety: dentysta w pobliżu, gabinet stomatologiczny, klinika medycyny estetycznej, fizjoterapeuta, implanty zębów · Usługi profesjonalne: adwokat w pobliżu, biuro rachunkowe, doradca biznesowy, projektant wnętrz, doradca podatkowy
- **ru** · Репетиторы: репетитор рядом, репетитор онлайн, найти репетитора, подготовка к ЕГЭ, репетитор цена · Репетитор по математике: репетитор по математике, репетитор по математике онлайн, подготовка к ЕГЭ по математике, репетитор по алгебре, репетитор по математике цена · Репетитор по физике: репетитор по физике, репетитор по физике онлайн, подготовка к ЕГЭ по физике, физика для школьников, помощь по физике онлайн · Интернет-магазины: продвижение интернет-магазина, реклама Google Shopping, SEO интернет-магазина, создать интернет-магазин, продажи онлайн · Клиники и медицина: стоматология рядом, стоматологическая клиника, клиника эстетической медицины, физиотерапевт, имплантация зубов · Профессиональные услуги: юрист рядом, бухгалтерские услуги, бизнес-консультант, дизайнер интерьера, налоговый консультант
- **uk** · Репетитори: репетитор поруч, репетитор онлайн, знайти репетитора, підготовка до НМТ, репетитор ціна · Репетитор з математики: репетитор з математики, репетитор з математики онлайн, підготовка до НМТ з математики, репетитор з алгебри, репетитор з математики ціна · Репетитор з фізики: репетитор з фізики, репетитор з фізики онлайн, підготовка до НМТ з фізики, фізика для школярів, допомога з фізики онлайн · Інтернет-магазини: просування інтернет-магазину, реклама Google Shopping, SEO інтернет-магазину, створити інтернет-магазин, продажі онлайн · Клініки й медицина: стоматологія поруч, стоматологічна клініка, клініка естетичної медицини, фізіотерапевт, імплантація зубів · Професійні послуги: юрист поруч, бухгалтерські послуги, бізнес-консультант, дизайнер інтер'єру, податковий консультант
- **ar** · المدرسون الخصوصيون: مدرس خصوصي, دروس خصوصية أونلاين, مدرس خصوصي قريب مني, دروس تقوية, تحضير الثانوية العامة · مدرس رياضيات: مدرس رياضيات, مدرس رياضيات أونلاين, دروس رياضيات للثانوية العامة, مدرس رياضيات خصوصي, سعر درس الرياضيات · مدرس فيزياء: مدرس فيزياء, مدرس فيزياء أونلاين, دروس فيزياء للثانوية العامة, مدرس فيزياء خصوصي, مساعدة في الفيزياء أونلاين · المتاجر الإلكترونية: وكالة تسويق متاجر إلكترونية, إعلانات جوجل شوبينج, SEO للمتاجر الإلكترونية, إنشاء متجر إلكتروني, البيع أونلاين · العيادات والرعاية الصحية: طبيب أسنان قريب مني, عيادة أسنان, عيادة تجميل, علاج طبيعي, زراعة الأسنان · الخدمات المهنية: محامي قريب مني, مكتب محاسبة, مستشار أعمال, مصمم ديكور داخلي, مستشار ضريبي
- **sv** · Privatlärare: privatlärare, läxhjälp online, privatlektioner, läxhjälp i närheten, hjälp inför högskoleprovet · Mattelärare: mattehjälp, mattelärare online, matte privatlektioner, mattehjälp gymnasiet, mattelärare pris · Fysiklärare: fysikhjälp, fysiklärare online, fysik privatlektioner, fysik gymnasiet hjälp, läxhjälp fysik · E-handel: e-handelsbyrå, Google Shopping annonser, SEO för e-handel, starta webbutik, sälja online · Kliniker och vård: tandläkare nära mig, tandklinik, estetisk klinik, fysioterapeut, tandimplantat · Professionella tjänster: advokat nära mig, redovisningsbyrå, företagskonsult, inredningsarkitekt, skatterådgivare
- **da** · Privatlærere: privatlærer, lektiehjælp online, privatundervisning, lektiehjælp i nærheden, eksamenstræning · Matematiklærere: matematikhjælp, matematiklærer online, privatundervisning matematik, matematik eksamen hjælp, matematiklærer pris · Fysiklærere: fysikhjælp, fysiklærer online, privatundervisning fysik, fysik gymnasiet hjælp, lektiehjælp fysik · Webshops: e-commerce bureau, Google Shopping annoncer, SEO til webshop, lave en webshop, sælge online · Klinikker og sundhed: tandlæge i nærheden, tandklinik, æstetisk klinik, fysioterapeut, tandimplantater · Liberale erhverv: advokat i nærheden, revisor, virksomhedsrådgiver, indretningsarkitekt, skatterådgiver
- **no** · Privatlærere: privatlærer, leksehjelp på nett, privatundervisning, leksehjelp i nærheten, eksamensforberedelse · Mattelærere: mattehjelp, mattelærer på nett, privatundervisning matte, matte eksamen hjelp, mattelærer pris · Fysikklærere: fysikkhjelp, fysikklærer på nett, privatundervisning fysikk, fysikk vgs hjelp, leksehjelp fysikk · Nettbutikker: byrå for nettbutikk, Google Shopping annonser, SEO for nettbutikk, lage nettbutikk, selge på nett · Klinikker og helse: tannlege i nærheten, tannklinikk, estetisk klinikk, fysioterapeut, tannimplantater · Profesjonelle tjenester: advokat i nærheten, regnskapsfører, bedriftsrådgiver, interiørarkitekt, skatterådgiver
- **ro** · Meditatori: meditații, meditații online, profesor meditații, meditații bacalaureat, meditații preț · Meditații la matematică: meditații matematică, meditații matematică online, meditații matematică bacalaureat, profesor matematică meditații, meditații matematică preț · Meditații la fizică: meditații fizică, meditații fizică online, meditații fizică bacalaureat, profesor fizică meditații, ajutor fizică online · Magazine online: agenție e-commerce, reclame Google Shopping, SEO magazin online, creare magazin online, vânzări online · Clinici și sănătate: dentist lângă mine, clinică stomatologică, clinică estetică, kinetoterapeut, implant dentar · Servicii profesionale: avocat lângă mine, firmă de contabilitate, consultant afaceri, designer de interior, consultant fiscal
- **az** · Repetitorlar: repetitor, onlayn repetitor, yaxınlıqda repetitor, buraxılış imtahanına hazırlıq, repetitor qiyməti · Riyaziyyat repetitoru: riyaziyyat repetitoru, onlayn riyaziyyat dərsi, qəbul imtahanı riyaziyyat hazırlığı, riyaziyyat müəllimi fərdi dərs, riyaziyyat repetitoru qiyməti · Fizika repetitoru: fizika repetitoru, onlayn fizika dərsi, qəbul imtahanı fizika hazırlığı, fizika müəllimi fərdi dərs, fizikadan kömək onlayn · Onlayn mağazalar: onlayn mağaza marketinqi, Google Shopping reklamı, onlayn mağaza üçün SEO, onlayn mağaza açmaq, onlayn satış · Klinikalar və səhiyyə: yaxınlıqda diş həkimi, stomatoloji klinika, estetik klinika, fizioterapevt, diş implantı · Peşəkar xidmətlər: yaxınlıqda vəkil, mühasibat xidməti, biznes məsləhətçisi, interyer dizayneri, vergi məsləhətçisi
