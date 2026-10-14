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
