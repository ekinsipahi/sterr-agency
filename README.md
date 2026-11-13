# Sterr Agency

Müşteri getiren dijital pazarlama ajansının web sitesi. Django 5.2, SQLite (ya da Postgres), sunucu tarafında render edilen şablonlar, harici framework yok.

**Sterr Technologies OÜ** · Sicil kodu 17591465 · Tornimäe tn 5, 10145 Tallinn, Estonya

## Kurulum

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env            # SECRET_KEY, RESEND_API_KEY, LEAD_NOTIFY_EMAILS, GA4_ID doldurun
.venv/bin/python manage.py migrate      # 3 paketi de (Kıvılcım, İvme, Hakimiyet) oluşturur
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Site: http://localhost:8000 · Admin: http://localhost:8000/admin/

## Admin'den yönetilenler

| Bölüm | Ne işe yarar |
|---|---|
| **Lead'ler** | Başvurular; A/B/C kalite skoru, durum takibi, WhatsApp/ara linkleri, CSV dışa aktarma. Durum değişikliği GA4'e gider |
| **Paketler** | Fiyat, özellik, öne çıkan paket. Tüm sayfalara ve rehberlere yansır |
| **Çalışmalar** | Vaka çalışmaları: kapak, ciro videosu (mp4 ya da YouTube), metrikler, Search Console / ciro / reklam paneli görselleri |
| **Müşteri yorumları** | Google yorumları ve referanslar (bölüm, yorum olunca görünür) |
| **Site ayarları** | **Logo** (yüklenene kadar yazı logosu), favicon, paylaşım görseli, Google puanı ve yorum sayısı, ana sayfa istatistikleri, sosyal medya linkleri |

> Rakamlar, yorumlar ve vakalar boşken ilgili bölümler sitede **hiç görünmez**. Sahte veri gösterilmez; yalnızca gerçek veri girin.

## Lead akışı

1. Ziyaretçi `/basvuru/` sayfasındaki 5 adımlı formu doldurur: sektör → hedef → bütçe → içerik/zamanlama → iletişim.
2. Lead veritabanına kaydedilir ve 0–100 arası skorlanır. 50K altı bütçe C sınıfına düşer, "fiyatçı filtresi" budur.
3. Resend üzerinden `LEAD_NOTIFY_EMAILS` adresine **"Yeni lead geldi"** e-postası gider (WhatsApp ve Admin butonlarıyla).
4. E-posta gönderilemezse bile lead kaybolmaz; admin'de `Bildirim gönderildi = hayır` olarak görünür.

**Resend (yeni hesap):** resend.com → Domains → alan adınızı ekleyip DNS kayıtlarını doğrulayın → API Keys → anahtar oluşturun → `.env`'e `RESEND_API_KEY` yazın. `DEFAULT_FROM_EMAIL` doğrulanmış domain'de olmalı. Anahtar yokken e-postalar terminale yazdırılır.

## SEO

- **324 programatik il sayfası:** 4 hizmet × 81 il, ör. `/sosyal-medya-ajansi/izmir/`
- 4 hizmet merkezi, 6 sektör sayfası, 6 rehber, `/hizmet-bolgeleri/`
- `sitemap.xml` (354 URL), `robots.txt`, canonical, OG, JSON-LD (`ProfessionalService`, `Service`, `FAQPage`, `BreadcrumbList`, `Article`)
- Keyword haritası ve il varyasyonları: [`keywords/KEYWORDS.md`](keywords/KEYWORDS.md)
- Yeni hizmet kümesi eklemek için `apps/seo/services.py` içindeki `CLUSTERS` listesine bir kayıt ekleyin; 81 sayfa otomatik üretilir.

```bash
SITE_URL=https://alanadiniz.com .venv/bin/python manage.py export_keywords   # keywords/*.csv
```

## Ölçüm

GA4, GTM, Meta Pixel, Consent Mode v2 ve lead yaşam döngüsü olayları: [`ANALYTICS.md`](ANALYTICS.md)

## Test

```bash
.venv/bin/python manage.py test apps
```

## Instagram ve TikTok influencer paketleri (aylık abonelik)

Büyüme yalnızca **paket** olarak satılır (ajans modeli). Tek başına beğeni, izlenme ya da yorum satılmaz. Üç aylık paket iki platformda da aynı (`apps/growth/plan.py`). Teslimat 30 güne yayılır, abonelik iptal edilene kadar her ay yenilenir ve ödenen ay iade edilmez:

| Paket | Aylık | Takipçi / ay (tipik) | Beğeni / ay | Yorum / ay | Ek |
|---|---|---|---|---|---|
| Starter Creator | $79.99 | 1.000–4.000 | 2.000–12.000 | 100–400 | |
| Rising Influencer (en popüler) | $149.99 | 2.000–8.000 | 4.000–24.000 | 200–800 | Hangi gönderilerin öne çıkacağını müşteri seçer |
| Pro Influencer | $279.99 | 4.000–16.000 | 8.000–48.000 | 400–1.600 | Gönderi seçimi + öncelikli yerleşim + doğrudan WhatsApp |

Rakamlar sözü verilen sayılar değil, tipik aralıklardır. Oranlar: yeni takipçi başına 2–3 beğeni, her 10 takipçide yaklaşık 1 yorum. Başlangıç paketi 1.000–4.000 takipçi/ay alındı; diğer paketler bunun 2 ve 4 katı.

**Sayfalar (her platform × 16 dil, 31 sayfa + geo; hepsi takipçi ana sayfasındaki gruplu hub'dan bağlı):**
- Takipçi: ana sayfa, real/active, pricing, "1000/2000/3000/5000/10k takipçi" sayfaları (her biri hangi paketle kaç ayda ulaşılacağını anlatır ve o paketi seçili getirir), growth agency, non-drop, hız rehberi, satın alma rehberi, legit
- Kendi üst seviye adresleriyle: influencer paketleri (`/instagram-packages/`), beğeni (`/instagram-likes-packages/`, aylık `/monthly-instagram-likes/`, kademeli, Reels), izlenme (`/instagram-views-packages/`, Reels, story), yorum (`/instagram-comments-packages/`, özel yorum `/custom-instagram-comments/`), instant vs kademeli (`/instagram-instant-vs-gradual/`). TikTok'ta da aynıları var (`/tiktok-likes-packages/`, `/tiktok-video-views/` …).
- Blog: beğeni paketi nasıl seçilir, izlenme başına para, 2026'da hâlâ işe yarıyor mu, yorum limiti, daha fazla izlenmenin 10 yolu
- Navbar'daki **Takipçi** menüsü: her platform için Followers / Packages / Likes / Views / Comments, ardından creator sayfası ve Hesabım.

Bir sayfa bir dilde henüz yoksa o dil için yayına çıkmaz: route, hreflang, sitemap ve menü yalnızca var olan sayfaları gösterir.

**İçerik dosyaları:**
- `apps/growth/i18n/<dil>.py`: arayüz metinleri (paket kartları, form, hesap, ortak bloklar; `{platform}` yer tutucusu)
- `apps/growth/pages/instagram|tiktok|creators/<dil>.py`: slug'lar (`/` ile başlayan değer üst seviye adres demek), sayfa metinleri ve her sayfanın `keywords` listesi
- Bir dili kontrol etmek için `python manage.py check_growth_copy de` kullanılır. Kontrol edilenler: yapı, meta uzunlukları, yasak kelimeler, eski tek seferlik fiyatların kalmaması ve keyword'lerin sayfada geçmesi. Testler 16 dilin hepsini bu kontrolden geçirir.
- Keyword planı: [`keywords/FOLLOWERS_KEYWORDS.md`](keywords/FOLLOWERS_KEYWORDS.md)

**Hesaplar ve abonelikler:**
- Formda paket seçilir, ardından kullanıcı adı ve hedef konum girilir. Hesap için iki yol var: e-posta + şifre (hesap yoksa açılır, varsa şifreyle giriş yapılır) ya da "Google ile devam et".
- `/account/` paneli her abonelik için şunları gösterir: durum, yenilenme ya da bitiş tarihi, bugün ve bu ay gelen takipçi, beğeni ve yorum, günlük grafik ve gün gün tablo. **Faturayı yönet / iptal et** butonu Stripe müşteri portalını açar (kart, faturalar, dönem sonunda iptal).
- `GROWTH_VERIFY_EMAIL=True` (varsayılan): ilk ödemeden önce e-posta onayı istenir (kart deneyen botlara karşı). Onay linki doğrudan Stripe ödemesine götürür. Aynı hesap ve kullanıcı adı için ödenmemiş abonelik tekrar denenirse yeni kayıt açılmaz, aynı kayıt kullanılır.
- Admin → **Influencer paketi abonelikleri**: durum, paket, yenilenme, günlük veriler. Eski tek seferlik siparişler "Eski takipçi siparişleri"nde duruyor.
- **Google ile giriş:** `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`. Redirect URI: `https://sterragency.com/account/google/complete/`.
- Veriler Supabase Postgres'te (`DATABASE_URL` ya da `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`, session pooler). Testler her zaman SQLite'ta çalışır; `.env` içinde `DEBUG=False` iken `DEBUG=True python manage.py test apps` ile çalıştır.

**Linksterr bağlantısı (otomatik, elle veri girilmez):** paketlerin teslimatı Linksterr'daki promoted kampanyalarla yapılır. sterr-agency verileri Linksterr'ın ajans endpoint'inden kendisi çeker: `GET https://linksterr.com/user-api/v1/agency/accounts/?account=instagram:<kullanıcı>&since=…&until=…`, `Authorization: Bearer <LINKSTERR_AGENCY_TOKEN>`.
- Token iki serviste de aynı isim ve değerle durur (`LINKSTERR_AGENCY_TOKEN`; Render → sterr-agency ve Render → linksterr → Environment). Boşsa bağlantı kapalıdır. Bu token yalnızca bu endpoint'i açar; Linksterr hesabına erişim vermez.
- Eşleşme: aboneliğin platformu + kullanıcı adı = Linksterr kampanyasının `category` + `cta_url` içindeki kullanıcı adı. Aynı hesabın birden çok kampanyası toplanır; sadece paketin çalıştığı günler (başlangıç → bugün ya da iptal günü) alınır.
- Gelenler (UTC günleri): **yeni takipçi** = Linksterr'ın gösterim başına takip oranı modeliyle (gerçek takipçi sayımlarıyla kalibre) hesaplanan sayı, profil ziyaretinden fazla olamaz; **profil ziyareti** = Follow'a basıp profile gidenler; gösterim, "takip ettim" onayı ve ülkeler (müşteriye gösterilmez, dispute kanıtında kullanılır); tarihli takipçi sayımları.
- Ne zaman çekilir: müşteri panelini açınca (abonelik başına en fazla 10 dakikada bir), dispute açılınca, admin'de "Kanıt paketi" açılınca, admin eylemi "Linksterr'dan günlük verileri çek" ve `python manage.py sync_linksterr` (isteğe bağlı günlük cron). 2 günden eski günler bir kez yazıldıktan sonra değişmez.
- Panel: Bugün ve Bu ay (yeni takipçi, beğeni, yorum, profil ziyareti), ülkelere göre ziyaret, son 30 gün grafiği, gün gün tablo. Gösterim sayısı panelde yoktur.
- Ters yönde Linksterr, aynı token'la `GET /growth/api/subscriptions/?status=active,past_due,canceled` listesini okur (salt okunur; yalnız ödenmiş paketler; bu token `/growth/api/stats/` yazamaz) ve kampanyaları kendisi yönetir. Abonelik her değiştiğinde (ödeme, ödeme hatası, iptal, devam, yenileme) sterr-agency `POST https://linksterr.com/user-api/v1/agency/sync/` ile Linksterr'ı hemen tetikler; Linksterr'ın cron'u yedektir:
  - ilk ödeme: kampanya **otomatik açılır** (paket ağırlığı Starter 1 / Rising 2 / Pro 4, dünya geneli; hazırlanmış taslak varsa o yayına alınır);
  - yenileme: `paid_until` uzar; dönem sonunda iptal: kampanya o gün durur; ödeme alınamadı: duraklar, ödeme gelince devam eder; abonelik bitti: kapanır; yeniden abonelik: tekrar açılır.
- Müşteriye (İngilizce): ilk ödemede "Your campaign has started", ödeme alınamayınca "We couldn't take your payment, so your campaign is paused", ödeme gelince "Payment received: your campaign is running again". Ekibe (Türkçe) aynı olaylar.
- Admin → Müşteriler veya abonelikler → **Paneli gör**: müşterinin panelini onun gördüğü haliyle, salt okunur açar (yalnızca staff; müşteri olarak giriş yapılmaz, hiçbir düğme yoktur, ziyaret müşterinin hareketi sayılmaz).

**Büyüme sistemi için API** (elle veya başka bir kaynaktan veri göndermek için; `GROWTH_API_TOKEN`, `Authorization: Bearer <token>`):
- `GET /growth/api/subscriptions/?status=active`: büyütülecek hesaplar (id, platform, kullanıcı adı, konum, dönem bitişi, başlangıç ve güncel takipçi).
- `POST /growth/api/stats/`: `{"subscription_id": 12, "date": "2026-11-04", "new_followers": 140, "followers": 5120}` ya da `{"updates": [...]}`. Her şeyi **getirdiğimiz takipçiden** sayıyoruz:
  - `new_followers`: o gün bizim getirdiğimiz takipçi. Gönderilmezse hesabın toplam takipçi sayısındaki fark kullanılır.
  - Beğeni = yeni takipçi × 2,5, yorum = yeni takipçi ÷ 10 (`plan.py`). `likes` / `comments` gönderilirse gönderilen değer kullanılır.
  - `followers` o günkü toplam takipçidir ve isteğe bağlıdır. Aynı gün tekrar gönderilirse yalnızca gönderilen alanlar güncellenir. `date` gönderilmezse bugünün UTC tarihi kullanılır.
  - Teslimat kanıtı (dispute için, isteğe bağlı): `impressions` (profilin gösterildiği kişi), `visits` (profile giden), `confirms` ("takip ettim" diyen) ve `countries`: `{"DE": {"impressions": 900, "visits": 210, "confirms": 95}}`.
  
  Panel her abonelik için şunları gösterir: **Bugün** (yeni takipçi, beğeni, yorum), **Bu ay**, son 30 günün grafiği ve gün gün tablo.

**Bildirimler (ekibe, Türkçe):** ödeme olmadan e-posta gitmez. Ekibe giden e-postalar:
- ilk ödeme Stripe'ta onaylanınca "Yeni … influencer paketi (ödendi)";
- her aylık ödemede "… yenilendi (ödendi)";
- müşteri iptal edince (panel ya da Stripe portalı) "… iptal talebi (dönem sonunda biter)", geri alınca "… iptali geri alındı";
- abonelik bitince "… iptal edildi";
- ödemeye itiraz gelince "DİKKAT: … itiraz (dispute) açıldı", sonuçlanınca "… itirazı sonuçlandı".

**İptal ve hatırlatma:** panelde "Aboneliği iptal et" (onay sayfası, dönem sonunda biter) ve "Aboneliğime devam et". Her yenilemeden önce müşteriye hatırlatma gider: tarih, tutar, hesap linki, WhatsApp ve en altta küçük bir not ("panelden istediğin zaman iptal edebilirsin"). Stripe'ın `invoice.upcoming` olayıyla gider (Stripe → Settings → Billing → Subscriptions and emails → *Upcoming renewal events*: 3 gün); yedek olarak `python manage.py send_renewal_reminders` (günlük cron) aynı işi yapar, dönem başına bir kez.

**Dispute kanıtı:** sipariş formundaki zorunlu şart kutusu (zaman, IP, tarayıcı, `TERMS_VERSION`), müşterinin girişleri ve panel ziyaretleri (`AccountActivity`), linksterr'ın günlük teslimat verisi, iptal ve hatırlatma kayıtları. İtiraz açılınca (`charge.dispute.created`) bunlar Stripe'a **taslak** olarak yüklenir, ekibe e-posta gider; Stripe'ta kontrol edip *Submit* edilir. Admin → abonelik → "Kanıt paketini aç" sayfası yazdırılıp PDF olarak eklenebilir. Checkout'ta 3D Secure istenir ve yenileme/iptal şartı ödeme butonunun üstünde yazar. Aynı Stripe hesabındaki diğer sitelerin olayları atlanır: ödeme yalnızca bizim oluşturduğumuz Checkout oturumuyla, abonelik ve itiraz yalnızca bizim Stripe kimliklerimizle eşleşir.

**Devreden büyüme (Şartlar 2a.1, 13 Kasım 2026):** iptal veya Stripe ödeme yönteminin kaldırılması ödenmiş dönemlerin eksik teslimatını silmez. Admin → abonelik → *Devreden büyüme*: biten ödenmiş dönemlerin toplam hedefini, buna karşı doğrulanmış toplam teslimatı, doğrulama zamanını ve hesabın dayanağını girin. Kalan takipçi `max(hedef - teslimat, 0)` olarak hesaplanır. Bunlar ekipçe doğrulanan değerlerdir; günlük tahminlerden veya abonelik yaşından otomatik borç üretilmez. Devam eden ayı erken eksik saymayın ve yeni ayın normal büyümesini önceki ayın telafisi yerine kullanmayın. İptal sonrası telafiyi ekip yürütür; bu değişiklik Linksterr'da iptal edilmiş kampanyayı otomatik yeniden açmaz. Her tamamlamadan sonra doğrulanmış toplamı ve zamanı güncelleyin. Kanıt paketi bakiye ile dayanağını gösterir; doldurulmadıysa sıfır yerine “not yet reconciled” yazar. Stripe'a daha önce yüklenmiş taslaklar kendiliğinden güncellenmez; güncel kanıt paketini kontrol edip taslağı güncelleyin. Yeni şart sürümü formun gönderildiği anda kaydedilir, geçmiş kabul kayıtları değiştirilmez.

Alıcılar: `LEAD_NOTIFY_EMAILS` + `GROWTH_NOTIFY_EMAILS` (varsayılan ekinsipahi8@gmail.com). Müşteri e-postaları her zaman İngilizcedir.

**Ödeme modu:** `GROWTH_PAYMENTS=False` iken abonelik "başvuru" olarak kaydedilir (ekibe bildirim, müşteriye "talebinizi aldık"). `True` iken Stripe Checkout abonelik modunda çalışır.

**Stripe kurulumu (fiyat değişince tekrar çalıştır):**
1. `STRIPE_SECRET_KEY` ve `STRIPE_PUBLISHABLE_KEY` → `.env` ve Render → Environment.
2. `python manage.py setup_stripe` şunları yapar:
   - 6 aylık fiyatı oluşturur (`sterr_<platform>_<paket>_monthly_usd`);
   - müşteri portalı ayarını oluşturur (kart, faturalar, dönem sonunda iptal);
   - webhook olaylarını günceller: `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `invoice.paid`, `invoice.payment_failed`, `invoice.upcoming`, `customer.subscription.updated`, `customer.subscription.deleted`, `charge.dispute.created`, `charge.dispute.closed`.
   
   Yeni webhook oluşturursa secret'ı `.env` dosyasına yazar, ekrana yazdırmaz.

## Yayına alma (Render)

Render'ın diski her deploy'da sıfırlanır. Bu yüzden veritabanı ve yüklenen görseller dışarıda durmalı: **Supabase** (ücretsiz plan yeterli) Postgres ve Storage için kullanılır.

**1. Supabase**
- Yeni proje açın (bölge: Frankfurt / eu-central-1).
- *Project Settings → Database → Connection string → **Session pooler*** adresini kopyalayın, şifreyi yerleştirin → `DATABASE_URL`. Direct connection IPv6'dır, Render'dan bağlanamaz.
- *Storage → New bucket* → adı `media`, **Public** işaretli.
- *Storage → S3 Configuration*: Endpoint → `AWS_S3_ENDPOINT_URL`, Region → `AWS_S3_REGION_NAME`. *New access key* → `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.
- `AWS_STORAGE_BUCKET_NAME=media`, `AWS_S3_CUSTOM_DOMAIN=<ref>.supabase.co/storage/v1/object/public/media`

**2. Render**
- *New → Blueprint* → bu repo. `render.yaml` servisi kurar; `sync: false` değişkenleri bir kez sorulur (yukarıdaki Supabase değerleri, `RESEND_API_KEY`, `LEAD_NOTIFY_EMAILS`, `DJANGO_SUPERUSER_*`, `GA4_ID`…).
- Build: `pip install` + `collectstatic`. Start: `migrate` → `ensure_seed_media` → `ensure_superuser` → gunicorn. Paketler, pazar fiyatları ve portföy migration'larla gelir.
- Health check: `/healthz`. `*.onrender.com` adresi `noindex` döner; sadece `sterragency.com` indekslenir.

**3. Alan adı**
- Render → *Settings → Custom Domains* altında `sterragency.com` ve `www.sterragency.com` görünür. Verilen DNS kayıtlarını alan adı panelinde girin. `www` otomatik olarak çıplak alan adına 301 yönlenir.
- Resend → Domains → `sterragency.com` doğrulaması (SPF/DKIM kayıtları).

Supabase istemiyorsanız: Render Postgres + Render persistent disk (`MEDIA_ROOT=/var/data/media`) de çalışır, ikisi de ücretli.

Statik dosyaları WhiteNoise sunar. Döviz kurları günde bir kez kendiliğinden yenilenir (`update_fx_rates` komutu elle de çalışır).

## Yapı

```
apps/core    ana sayfa, kurumsal sayfalar, paketler, site ayarları, yasal sayfalar, sitemap/robots
apps/leads   başvuru formu, skor, Resend bildirimi, GA4 Measurement Protocol
apps/works   vaka çalışmaları (video, metrik, panel görselleri)
apps/seo     81 il verisi, Türkçe ek çekimi, pSEO kümeleri, sektörler, rehberler
templates/   tüm HTML (tasarım sistemi: static/css/site.css)
keywords/    keyword haritası + CSV'ler
```


## Diş turizmi (16 dil) ve yorumlar

- `/dental-tourism/` altında 2 sayfa × 16 dil (acente + iş birliği); yalnızca "dental tourism agency" tipi aramaları hedefler. İçerik `apps/dental/locales/<dil>.py`.
  Gelen talepler admin → **Diş turizmi talepleri**; bildirim aynı Resend ayarıyla gider.
- Navbar'daki bayraklı dil menüsü bayrakları `static/img/flags/` (PNG, @2x).
- **Google yorumları:** admin → Site ayarları → "Google'da yorum yazma linki" alanına Google İşletme Profili'ndeki
  "Yorum iste" linkini girin. Sitede yorum butonu çıkar ve müşterilere `sterragency.com/yorum/` kısayolunu gönderebilirsiniz.
- **Çalışmalar:** linksterr.com, dentaltourism.tr, drdevrim.com, devrimbirikensipahi.com.tr ekran görüntüleriyle
  migration ile eklendi (admin → Çalışmalar). Search Console, ciro ve hasta sayısı görsellerini her çalışmanın altına ekleyin.

## Uluslararası ajans (15 dil)

- `/<dil>/` altında her dil için ana sayfa, 4 hizmet kümesi, sektörler ve rehberler (285 sayfa). İçerik `apps/intl/locales/<dil>.py`.
- **Fiyatlar:** admin → *Pazar fiyatları* üzerinden her pazarın USD başlangıç fiyatı (varsayılan 1000, Polonya/Rusya/Ukrayna/Romanya/Azerbaycan 900).
  Yerel para birimine güncel kurla çevrilir; kurlar günde bir kez otomatik yenilenir. Sunucuda cron ile de çalıştırılabilir:
  `python manage.py update_fx_rates`
- Türkçe ana sayfa, hizmet kümeleri, sektörler ve rehberler, yabancı dildeki karşılıklarına `hreflang` ile bağlı.
