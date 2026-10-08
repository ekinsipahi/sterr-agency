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

## Yayına alma

```bash
DEBUG=False
ALLOWED_HOSTS=alanadiniz.com,www.alanadiniz.com
CSRF_TRUSTED_ORIGINS=https://alanadiniz.com
SITE_URL=https://alanadiniz.com
```

```bash
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py migrate
gunicorn config.wsgi --bind 0.0.0.0:8000
```

Statik dosyaları WhiteNoise sunar. Yüklenen medya (`media/`) varsayılan olarak Django üzerinden sunulur (`SERVE_MEDIA=True`). Trafik arttığında nginx ya da S3'e taşıyın. Medya klasörünün kalıcı diskte olduğundan emin olun.

## Yapı

```
apps/core    ana sayfa, kurumsal sayfalar, paketler, site ayarları, yasal sayfalar, sitemap/robots
apps/leads   başvuru formu, skor, Resend bildirimi, GA4 Measurement Protocol
apps/works   vaka çalışmaları (video, metrik, panel görselleri)
apps/seo     81 il verisi, Türkçe ek çekimi, pSEO kümeleri, sektörler, rehberler
templates/   tüm HTML (tasarım sistemi: static/css/site.css)
keywords/    keyword haritası + CSV'ler
```
