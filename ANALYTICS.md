# GA4 Ölçüm Kurulumu — Sterr Agency

Sitenin her kritik anı GA4'e event olarak düşer: sayfa bağlamı, arama/WhatsApp tıklamaları, başvuru funnel'ının her adımı, lead ve **lead sonrası yaşam döngüsü** (görüşme → kazanıldı). Hepsi Consent Mode v2 ile KVKK/GDPR uyumlu çalışır.

## 1. `.env` ayarları

```env
GA4_ID=G-XXXXXXXXXX          # GA4 → Yönetici → Veri akışları → Ölçüm kimliği
GA4_API_SECRET=xxxxxxxx      # Aynı veri akışı → Measurement Protocol API gizli anahtarları → Oluştur
GTM_ID=                      # İsteğe bağlı. Doluysa GA4 GTM içinden yönetilir, gtag.js yüklenmez
META_PIXEL_ID=               # İsteğe bağlı
GOOGLE_SITE_VERIFICATION=    # Search Console HTML etiketi doğrulaması
```

> **GTM veya doğrudan GA4, ikisinden biri.** `GTM_ID` doluysa site olayları yalnızca `dataLayer`'a gönderir. GA4 etiketini GTM içinde kurun. `GA4_ID` + `GA4_API_SECRET` yine de sunucu tarafı lead olayları için gereklidir.

## 2. Olay sözlüğü

### İstemci (tarayıcı) olayları

| Event | Ne zaman | Parametreler | Anahtar etkinlik? |
|---|---|---|:-:|
| `page_view` (otomatik) | Her sayfa | `content_group`, `page_type`, `service`, `city`, `region`, `market_tier`, `sector`, `guide` | — |
| `phone_click` | `tel:` linki tıklandı (arama) | `link_location`, `link_url` | ✅ |
| `whatsapp_click` | wa.me linki (üst menü, alt bilgi, yüzen buton, CTA) | `link_location`, `link_url` | ✅ |
| `email_click` | `mailto:` linki | `link_location` | — |
| `cta_click` | Başvuru sayfasına giden buton | `cta_text`, `link_location` | — |
| `package_select` | Paket kartındaki "… için başvur" | `package`, `link_location` | — |
| `lead_form_start` | Formdaki ilk etkileşim | `form_id`, `package` | — |
| `lead_form_step` | 2–5. adım ilk kez görüldü | `step_number`, `step_name`, `lead_sector`, `lead_goal`, `lead_budget` | — |
| `lead_form_submit` | Gönder butonu | `lead_budget`, `lead_sector` | — |
| `lead_form_error` | Sunucu formu reddetti | `error_fields` | — |
| **`generate_lead`** | Teşekkür sayfası (tek sefer) | `value`, `currency=TRY`, `lead_id`, `lead_tier`, `lead_sector`, `lead_budget`, `lead_city`, `package` | ✅ |

`link_location` değerleri: `nav`, `hero`, `pricing`, `cta_band`, `footer`, `floating_button`, `form`, `body`.

`generate_lead` değeri bütçe bandına göre tahmini aylık gelirdir: 50–100K → 50.000, 100–250K → 90.000, 250K+ → 150.000, 50K altı → 0.

### Sunucu olayları (Measurement Protocol, admin'den)

Admin'de bir lead'in **Durum** alanı değiştiğinde (listeden ya da detaydan) otomatik gönderilir. Kullanıcının `_ga` çerezi başvuru anında kaydedildiği için olay **aynı kullanıcıya ve aynı kaynağa** (Google Ads, organik, il sayfası…) bağlanır.

| Admin durumu | GA4 event (Google'ın önerdiği lead event'leri) | Değer |
|---|---|---|
| İletişime geçildi | `working_lead` | tahmini |
| Görüşme planlandı | `qualify_lead` | tahmini |
| Teklif verildi | `lead_proposal_sent` | tahmini |
| **Kazanıldı** | **`close_convert_lead`** | **"Anlaşma değeri" alanı** |
| Kaybedildi | `close_unconvert_lead` | tahmini |
| Uygun değil | `disqualify_lead` (+ `disqualified_lead_reason`) | tahmini |

## 3. GA4 panelinde yapılacaklar (bir kerelik)

1. **Anahtar etkinlikler** (Yönetici → Etkinlikler → yıldızla): `generate_lead`, `phone_click`, `whatsapp_click`, `qualify_lead`, `close_convert_lead`.
2. **Özel boyutlar** (Yönetici → Özel tanımlar → Etkinlik kapsamlı):
   `service`, `city`, `region`, `market_tier`, `page_type`, `link_location`, `lead_tier`, `lead_sector`, `lead_budget`, `lead_city`, `package`, `step_name`, `lead_status`.
   Özel metrik: `step_number`.
3. **Veri saklama**: Yönetici → Veri saklama → 14 ay.
4. **Dahili trafik**: kendi IP'nizi filtreleyin.
5. **Google Ads bağlantısı**: Yönetici → Ürün bağlantıları → Google Ads. Ardından Ads'te `generate_lead` ve `close_convert_lead` olaylarını dönüşüm olarak içe aktarın. Kazanılan müşteriler, onları getiren reklam kampanyasına değeriyle birlikte yazılır.
6. **Search Console bağlantısı**: Yönetici → Ürün bağlantıları → Search Console (il sayfalarının organik performansı GA4'te görünür).

## 4. Hazır raporlar (Keşfet)

**Funnel keşfi: "Başvuru hunisi"** (açık huni)
1. `page_view` (page_type = lead_form)
2. `lead_form_start`
3. `lead_form_step` (step_number = 3, bütçe)
4. `lead_form_step` (step_number = 5, iletişim)
5. `generate_lead`
6. `qualify_lead`
7. `close_convert_lead`

Kırılım: `lead_budget` ya da `session_source`. Fiyatçı filtresinin nerede devreye girdiğini ve hangi kaynağın gerçek müşteri getirdiğini gösterir.

**Serbest form: "pSEO il performansı"**
Satırlar `city`, sütunlar `service`, değerler `generate_lead` sayısı + `phone_click` + `whatsapp_click`. Filtre: `content_group = pseo_il`. Hangi ilde hangi hizmetin talep getirdiği görünür; reklam bütçesi buna göre kaydırılır.

**Serbest form: "İletişim kanalları"**
`event_name` ∈ {phone_click, whatsapp_click, email_click} × `link_location`. Arama butonunun sayfanın neresinde çalıştığını gösterir.

## 5. Arama (call) takibi hakkında

- **Web'den gelen aramalar:** `tel:` tıklamaları `phone_click` olarak ölçülür (mobilde tıklama = arama başlatma).
- **Google Ads arama uzantısından gelen aramalar** Ads tarafında otomatik ölçülür, ek kod gerekmez.
- **Numarayı elle çevirip arayanlar** (web sitesinde numarayı görüp tuşlayanlar) için Google Ads "web sitesi arama dönüşümü" ve dinamik numara (Google yönlendirme numarası) gerekir. Bu Ads hesabında kurulur; kurulduğunda `GTM_ID` üzerinden eklenebilir.

## 6. Onay (Consent Mode v2)

- Varsayılan: tüm depolama **reddedildi**. GA4 çerezsiz, modellenmiş sinyal gönderir.
- "Kabul et" tıklanınca `analytics_storage`, `ad_storage`, `ad_user_data`, `ad_personalization` **granted** olur ve Meta Pixel yüklenir.
- Tercih `localStorage.sterr_consent` içinde saklanır.
- Onay verilmemişse `_ga` çerezi olmaz. Sunucu olayları yine gider ama kullanıcıya değil, lead'e özel bir kimliğe bağlanır (kaynak eşleşmesi zayıflar).

## 7. Test

1. `.env`'e `GA4_ID` girin, siteyi açın, çerezi kabul edin.
2. [Google Tag Assistant](https://tagassistant.google.com) ile siteye bağlanın. Olaylar GA4 → Yönetici → **DebugView**'da canlı görünür.
3. Formu doldurun: `lead_form_start` → `lead_form_step` ×4 → `lead_form_submit` → `generate_lead` görünmeli.
4. Admin'de lead'in durumunu "Görüşme planlandı" yapın. Birkaç dakika içinde `qualify_lead` gelmeli. (Measurement Protocol olayları DebugView'da görünmez; Gerçek zamanlı raporda görünür.)
