from django.db import models

from apps.core.languages import INTL_CODES, LANG_BY_CODE

LANG_CHOICES = [(code, LANG_BY_CODE[code].name) for code in INTL_CODES]


class Market(models.Model):
    """Pricing policy per language/country. The USD price is converted to the local
    currency with the latest exchange rate (see apps.intl.pricing)."""

    lang = models.CharField("Dil / pazar", max_length=5, choices=LANG_CHOICES, primary_key=True)
    country = models.CharField("Ülke(ler)", max_length=80)
    currency = models.CharField("Para birimi (ISO)", max_length=3, help_text="Örn. EUR, PLN, SEK")
    usd_price = models.PositiveIntegerField("Başlangıç fiyatı (USD / ay)", default=1000,
                                            help_text="Ekonomik olarak zor pazarlarda 900 gibi daha düşük bir değer.")

    class Meta:
        ordering = ["lang"]
        verbose_name = "Pazar fiyatı"
        verbose_name_plural = "Pazar fiyatları (ülkeye özel)"

    def __str__(self):
        return f"{self.get_lang_display()} · {self.usd_price} USD → {self.currency}"


class FxRate(models.Model):
    """1 USD = `rate` units of `currency`. Refreshed daily from a public API."""

    currency = models.CharField(max_length=3, primary_key=True)
    rate = models.DecimalField(max_digits=14, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Döviz kuru"
        verbose_name_plural = "Döviz kurları (USD bazlı)"

    def __str__(self):
        return f"1 USD = {self.rate} {self.currency}"


class IntlLead(models.Model):
    INTERESTS = [
        ("dijital-pazarlama-ajansi", "Dijital pazarlama ajansı"),
        ("sosyal-medya-ajansi", "Sosyal medya ajansı"),
        ("sosyal-medya-yonetimi-ajansi", "Sosyal medya yönetimi"),
        ("dijital-pazarlama-uzmani", "Dijital pazarlama uzmanı / ekip"),
        ("other", "Diğer / emin değil"),
    ]
    STATUSES = [
        ("new", "Yeni"), ("contacted", "İletişime geçildi"), ("meeting", "Görüşme planlandı"),
        ("proposal", "Teklif verildi"), ("won", "Kazanıldı"), ("lost", "Kaybedildi"), ("unqualified", "Uygun değil"),
    ]

    lang = models.CharField("Dil", max_length=5, choices=LANG_CHOICES)
    name = models.CharField("Ad Soyad", max_length=100)
    email = models.EmailField("E-posta")
    phone = models.CharField("Telefon / WhatsApp", max_length=40)
    company = models.CharField("İşletme", max_length=120, blank=True)
    website = models.CharField("Web sitesi / Instagram", max_length=200, blank=True)
    country = models.CharField("Ülke", max_length=60)
    interest = models.CharField("İlgilendiği hizmet", max_length=40, choices=INTERESTS, default="dijital-pazarlama-ajansi")
    message = models.TextField("Mesaj", blank=True)
    quoted_price = models.CharField("Gördüğü başlangıç fiyatı", max_length=40, blank=True)
    usd_price = models.PositiveIntegerField("Pazar fiyatı (USD)", null=True, blank=True)

    status = models.CharField("Durum", max_length=20, choices=STATUSES, default="new")
    notes = models.TextField("İç notlar", blank=True)
    source_page = models.CharField("Geldiği sayfa", max_length=300, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=150, blank=True)
    gclid = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    notified = models.BooleanField("Bildirim gönderildi", default=False)
    created_at = models.DateTimeField("Tarih", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Yurt dışı başvuru"
        verbose_name_plural = "Yurt dışı başvurular (15 dil)"

    def __str__(self):
        return f"{self.name} ({self.lang}, {self.country})"
