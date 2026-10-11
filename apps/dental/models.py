from django.db import models

from .languages import LANGS


class DentalInquiry(models.Model):
    """A request from the international /dental-tourism/ pages (patient or B2B partner)."""

    TYPES = [("patient", "Hasta"), ("clinic", "Klinik"), ("agency", "Acente / aracı")]
    TREATMENTS = [
        ("implants", "İmplant"),
        ("all_on", "All-on-4 / All-on-6"),
        ("veneers", "Lamina / veneer"),
        ("crowns", "Kron & köprü"),
        ("smile", "Gülüş tasarımı"),
        ("whitening", "Beyazlatma"),
        ("other", "Henüz emin değil"),
    ]
    STATUSES = [
        ("new", "Yeni"),
        ("contacted", "İletişime geçildi"),
        ("plan_sent", "Plan / teklif gönderildi"),
        ("booked", "Randevu / anlaşma"),
        ("lost", "Kaybedildi"),
        ("spam", "Uygun değil"),
    ]

    kind = models.CharField("Tür", max_length=10, choices=TYPES, default="patient")
    lang = models.CharField("Dil", max_length=5, choices=[(lang.code, lang.name) for lang in LANGS])
    name = models.CharField("Ad Soyad", max_length=100)
    email = models.EmailField("E-posta")
    phone = models.CharField("Telefon / WhatsApp", max_length=40)
    country = models.CharField("Ülke", max_length=60)
    company = models.CharField("Klinik / acente adı", max_length=120, blank=True)
    treatment = models.CharField("Tedavi", max_length=12, choices=TREATMENTS, blank=True)
    message = models.TextField("Mesaj", blank=True)

    status = models.CharField("Durum", max_length=12, choices=STATUSES, default="new")
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
        verbose_name = "Diş turizmi talebi"
        verbose_name_plural = "Diş turizmi talepleri"

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()}, {self.lang})"
