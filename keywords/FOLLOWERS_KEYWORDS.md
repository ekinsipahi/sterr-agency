# Takipçi paketleri ve creator hub'ı: keyword planı

Kasım 2026'da gelen iki keyword analizinden ("buy instagram followers" ve "influencer agency") çıkan sayfa yapısı. Her grup bir sayfaya gidiyor; Instagram ve TikTok için aynı yapı ayrı ayrı var (`instagram` → `tiktok` varyasyonu), 16 dilde.

**Her sayfanın keyword listesi kod içinde durur** (`apps/growth/pages/<platform>/<dil>.py` → `keywords`) ve testler her keyword'ün o sayfanın metninde gerçekten geçtiğini kontrol eder. Tüm dillerin tam listesi: [`followers_keywords.csv`](followers_keywords.csv) (`python keywords/_followers_keywords.py` ile üretilir).

## Sayfa ↔ keyword grubu (İngilizce, Instagram; TikTok'ta "instagram" yerine "tiktok")

| Sayfa | URL (en) | Keyword grubu |
|---|---|---|
| Ana sayfa (hub) | `/en/instagram-followers/` | buy instagram followers, buy followers on instagram, buy instagram followers online, purchase instagram followers, best site / best place / platform to buy instagram followers, website |
| Real / active | `…/real-active-followers/` | buy real instagram followers, real active instagram followers, instagram followers that engage, real people, genuine, authentic, organic, targeted, high quality, look real, likes |
| Ucuz (fiyat tablosu üstte) | `…/pricing/` | cheap instagram followers, buy instagram followers cheap, cheapest, low price, low cost, debit card, apple pay, "10k for $5" |
| Paket sayfaları | `…/buy-1000-instagram-followers/` … `…/buy-10k-instagram-followers/` | buy 1000 / 2000 / 3000 / 5000 / 10k instagram followers, 1k…10k; her sayfada kendi fiyatı, teslim süresi ve SSS |
| Growth agency | `…/instagram-growth-agency/` | instagram growth agency, instagram agency, management agency, promotion agency, followers agency, reels, content agency |
| Non-drop | `…/non-drop-followers/` | non drop instagram followers, followers that don't drop, followers that stay, permanent, unfollow |
| Instant vs kademeli | `…/how-fast-can-you-grow/` | instant instagram followers, instant / fast delivery, gradual delivery, drip feed, daily |
| Satın alma rehberi | `…/should-you-buy-instagram-followers/` | can you buy instagram followers, get you banned, legal, worth it, pros and cons, iphone, android, how many followers, private account |
| Legit | `…/is-sterr-legit/` | legit, legitimate, reviews, trusted, safe, best site |
| Ülke (yalnız Instagram, İngilizce) | `…/usa/`, `/uk/`, `/australia/`, `/europe/`, `/uae/` | buy instagram followers in the usa / uk … |

## Creator hub'ı (platformdan bağımsız)

| Sayfa | URL (en) | Keyword grubu |
|---|---|---|
| Influencer agency for creators | `/en/influencer-agency/` | influencer agency, social media influencer agency, influencer agency for creators / small creators, social media agency for influencers, influencer agency instagram / tiktok, influencer talent / management agency, youtube, gaming, worldwide, best influencer agency |
| Rehber | `…/what-does-an-influencer-agency-do/` | what does an influencer marketing agency do |
| Rehber | `…/influencer-agency-red-flags/` | unpaid fees, red flags |
| Rehber | `…/how-to-get-signed/` | how to get signed by an influencer agency, brand-ready |
| Rehber | `…/do-small-creators-need-an-agency/` | do i need an agency as a small influencer |

Talent / management keyword'leri ayrı sayfa açılmadan ana creator sayfasında dürüstçe karşılanıyor: "marka anlaşması yapmıyoruz, o anlaşmaların dayandığı gerçek kitleyi büyütüyoruz". Marka anlaşması veya menajerlik hizmeti verilirse ayrı sayfa açılabilir.

## Bilerek kullanmadıklarımız

| Grup | Neden |
|---|---|
| Rakip markalar (buzzoid, stormlikes, famety…) | Marka hakkı riski; sitede hiç geçmiyor (testle engelli) |
| Hesap satışı, SMM panel, bayilik | Farklı ürün / farklı müşteri |
| free, gratis, bedava, free trial | Deneme paketi yok |
| PayPal, kripto, UPI, Paytm, GCash, naira… | Bu ödeme yöntemleri yok; yalnızca kart, Apple Pay, Google Pay (Stripe) |
| "instant delivery" opsiyonu | Satmıyoruz; bu aramayı "instant = bot" mesajıyla karşılıyoruz |
| "refill / garanti" | Refill politikası yok; garanti kelimesi hiçbir dilde kullanılmıyor (testle engelli) |
| likes, views, comments satın alma | Satmıyoruz; her sayfada nedenini anlatan blok var |
| Marka tarafı (influencer marketing platform, outreach, gifting, kampanya) | Bunları marka arar, creator değil |
| İş ilanı, maaş, Instagram ofisi, tanımlar, alakasız ajans türleri | Niyet uyuşmuyor |
| Hindistan, Pakistan, Nijerya vb. ülke sayfaları | Yerel ödeme yöntemi ve fiyat beklentisi uymuyor |

## Her sayfada geçen ortak mesajlar

- Takipçilerin hepsi gerçek kişi; teslim süreleri bu yüzden gerçek (7–14 günden 60–120 güne).
- Instant kalite değil, bot demek.
- Beğeni, izlenme, yorum satmıyoruz: doğal olmayan her sinyal algoritma tarafından cezalandırılır, algoritma hesabınıza çoktan bir değer biçmiştir.
- Sahte botlar gizli bir algoritma cezası getirir; toparlanmak aylar, bazen yıllar sürer.
- Şifre asla istenmez; tek seferlik ödeme, abonelik yok.
