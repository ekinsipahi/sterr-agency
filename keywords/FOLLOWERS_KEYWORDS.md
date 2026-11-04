# Influencer paketleri, takipçi/beğeni/izlenme/yorum sayfaları ve creator hub'ı: keyword planı

Kasım 2026'da gelen iki keyword analizinden ("buy instagram followers" ve "influencer agency") çıkan sayfa yapısı. Her grup bir sayfaya gidiyor; Instagram ve TikTok için aynı yapı ayrı ayrı var (`instagram` → `tiktok` varyasyonu), 16 dilde.

**Her sayfanın keyword listesi kod içinde durur** (`apps/growth/pages/<platform>/<dil>.py` → `keywords`) ve testler her keyword'ün o sayfanın metninde gerçekten geçtiğini kontrol eder. Tüm dillerin tam listesi: [`followers_keywords.csv`](followers_keywords.csv) (`python keywords/_followers_keywords.py` ile üretilir).

## Sayfa ↔ keyword grubu (İngilizce, Instagram; TikTok'ta "instagram" yerine "tiktok")

| Sayfa | URL (en) | Keyword grubu |
|---|---|---|
| Ana sayfa (hub) | `/en/instagram-followers/` | buy instagram followers, buy followers on instagram, buy instagram followers online, purchase instagram followers, best site / best place / platform to buy instagram followers, website, likes, comments, agency package, by country, italian, german |
| Real / active | `…/real-active-followers/` | buy real instagram followers, real active instagram followers, instagram followers that engage, real people, genuine, authentic, organic, targeted, high quality, look real, likes, buy instagram followers that are real, that interact, realistic |
| Ucuz (fiyat tablosu üstte) | `…/pricing/` | cheap instagram followers, buy instagram followers cheap, cheapest, low price, low cost, debit card, apple pay, "10k for $5", monthly, cancel |
| "X takipçi" sayfaları | `…/buy-1000-instagram-followers/` … `…/buy-10k-instagram-followers/` | buy 1000 / 2000 / 3000 / 5000 / 10k instagram followers, 1k…10k; artık sabit paket değil: hangi influencer paketiyle kaç ayda ulaşılacağı (1k Starter, 2k/3k Rising, 5k/10k Pro) |
| Growth agency | `…/instagram-growth-agency/` | instagram growth agency, instagram agency, management agency, promotion agency, followers agency, reels, content agency |
| Non-drop | `…/non-drop-followers/` | non drop instagram followers, followers that don't drop, followers that stay, permanent, unfollow |
| Instant vs kademeli | `…/how-fast-can-you-grow/` | instant instagram followers, instant / fast delivery, gradual delivery, drip feed, daily |
| Satın alma rehberi | `…/should-you-buy-instagram-followers/` | can you buy instagram followers, get you banned, legal, worth it, pros and cons, iphone, android, how many followers, private account, without getting banned, no ban |
| Legit | `…/is-sterr-legit/` | legit, legitimate, reviews, trusted, safe, best site |
| Ülke (yalnız Instagram, İngilizce) | `…/usa/`, `/uk/`, `/australia/`, `/europe/`, `/uae/` | buy instagram followers in the usa / uk … |

## Influencer paketleri, beğeni, izlenme, yorum (Kasım 2026, 3. analiz)

Hepsi aynı üç aylık paketi satar (Starter Creator / Rising Influencer / Pro Influencer). Beğeni, izlenme ve yorum tek başına satılmaz; her sayfa o metriğin pakette nasıl geldiğini anlatır. Adresler üst seviyede, TikTok'ta aynısı `tiktok` ile (Reels → video).

| Sayfa | URL (en) | Keyword grubu |
|---|---|---|
| Influencer paketleri (kombine) | `/en/instagram-packages/` | buy instagram followers, likes & views; buy instagram likes and followers / likes and views / views and likes / likes and views cheap; instagram likes and views; buy instagram comments and likes; buy instagram followers and views; buy instagram likes and shares; starter creator, rising influencer, pro influencer, 30 days |
| Beğeni (ana) | `/en/instagram-likes-packages/` | instagram likes, buy instagram likes (online, now), website, best website, price, premium, legit, reviews; real people, real accounts, genuine, organic, high quality, realistic, that look real, buy real instagram likes that engage, instagram likes real; cheap, cheapest, low price, $1, small amount, buy ig likes for cheap; video likes, likes on post, highlight; by country, american, india, in rupees, apple pay. 5/10/25/500 beğeni gibi adetler "küçük paket satmıyoruz" bölümünde geçer |
| Aylık beğeni | `/en/monthly-instagram-likes/` | buy automatic instagram likes monthly, buy instagram likes monthly, auto likes, trustpilot ("uydurma yorum yayınlamıyoruz"), every new post, subscription |
| Kademeli beğeni | `/en/instagram-likes-packages/gradual-delivery/` | instagram likes with gradual delivery, gradual delivery, slow delivery, slow, over time, no drop |
| Reels beğenisi | `/en/instagram-reels-likes/` | buy instagram likes for reels, likes on reels, get instagram likes on reels, reel likes from india |
| İzlenme (ana) | `/en/instagram-views-packages/` | buy views on ig, buy instagram views (online, cheap), buy views on instagram, instagram views to buy, website, post, cheapest, low price, 2026, instagram get more views, get instagram post views, profile views, india, pakistan, apple pay |
| Reels izlenme | `/en/instagram-reels-views/` | buy instagram views for reels, instagram views reels buy, buy instagram reel views cheap, buy views on instagram reels in india, buy instagram reel views in india, cheapest in india |
| Story izlenme | `/en/instagram-story-views/` | buy instagram views on story, views on story, story views, stories |
| Yorum (ana) | `/en/instagram-comments-packages/` | buy instagram comments, get instagram (post) comments, instagram comments to buy, buy comments in instagram, likes on comments, india, pakistan, nigeria, in rupees |
| Özel yorum | `/en/custom-instagram-comments/` | buy instagram comments custom, custom comments, ai comments (bot olarak anlatılır, satılmaz), generic, "nice pic" |
| Instant vs kademeli | `/en/instagram-instant-vs-gradual/` | buy instagram likes instant, fast, quick, instant views on instagram, buy instagram comments instant, buy instagram followers instant, instant delivery, gradual |
| Blog | `…/how-to-buy-instagram-likes/` | how do you buy instagram likes, likes package, choose |
| Blog | `…/how-much-does-instagram-pay-for-views/` | instagram views money, instagram views payment, brand deals, pay per view (TikTok'ta Creator Rewards) |
| Blog | `…/can-you-still-buy-instagram-likes/` | can you still buy instagram likes, can i buy instagram comments, 2026, still work |
| Blog | `…/instagram-comment-limit/` | is there a comment limit on instagram, 2,200 characters (TikTok: 150), action blocked, comment limit |
| Blog | `…/how-to-get-more-reels-views/` | instagram get more views, get instagram likes on post, reels views, 10 ways |

Bu analizden bilerek kullanılmayanlar:
- ücretsiz arayanlar ("free every 24 hours" vb.);
- rakip markalar;
- başka platformlar (YouTube, Twitch, Facebook, Twitter);
- pazar yerleri (etsy, g2g, ebay, shopee, upwork);
- "verified" veya "celebrity" yorum vaadi;
- kadın/erkek hedefleme (yapılamıyor);
- crypto, paytm, gcash (ödeme yalnız Stripe: kart, Apple Pay, Google Pay);
- "no sign up" (hesap açılıyor);
- threads (ileride ayrı sayfa olabilir);
- canlı yayın izleyicisi (paket yok).

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
