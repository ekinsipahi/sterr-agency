from django.db import models

from apps.seo.cities import CITIES_ALPHA

CITY_CHOICES = [(c.slug, c.name) for c in CITIES_ALPHA] + [("turkiye-geneli", "Türkiye geneli / Online")]


class Lead(models.Model):
    SECTORS = [
        ("ozel-ders", "Özel ders / eğitim"),
        ("e-ticaret", "E-ticaret"),
        ("saglik", "Klinik / sağlık"),
        ("profesyonel", "Profesyonel hizmet (hukuk, danışmanlık…)"),
        ("yerel", "Yerel işletme (restoran, güzellik, emlak…)"),
        ("diger", "Diğer"),
    ]
    BUDGETS = [
        ("lt50", "50.000 ₺ altı"),
        ("50-100", "50.000 – 100.000 ₺"),
        ("100-250", "100.000 – 250.000 ₺"),
        ("250+", "250.000 ₺ ve üzeri"),
    ]
    GOALS = [
        ("musteri", "Daha fazla müşteri / randevu"),
        ("satis", "Online satışları artırmak"),
        ("marka", "Marka bilinirliği ve konumlandırma"),
        ("kurulum", "Sıfırdan kurulum (site, e-ticaret, hesaplar)"),
    ]
    CONTENT = [
        ("var", "Evet, düzenli içeriğimiz var"),
        ("kismen", "Kısmen var"),
        ("yok", "Hayır, içerik üretimi gerekiyor"),
    ]
    TIMELINES = [
        ("hemen", "Hemen başlamak istiyorum"),
        ("1-ay", "1 ay içinde"),
        ("arastiriyorum", "Şimdilik araştırıyorum"),
    ]
    STATUSES = [
        ("new", "Yeni"),
        ("contacted", "İletişime geçildi"),
        ("meeting", "Görüşme planlandı"),
        ("proposal", "Teklif verildi"),
        ("won", "Kazanıldı"),
        ("lost", "Kaybedildi"),
        ("unqualified", "Uygun değil"),
    ]

    name = models.CharField("Ad Soyad", max_length=100)
    phone = models.CharField("Telefon", max_length=30)
    email = models.EmailField("E-posta")
    company = models.CharField("İşletme", max_length=120, blank=True)
    website = models.CharField("Web sitesi / Instagram", max_length=200, blank=True)
    sector = models.CharField("Sektör", max_length=20, choices=SECTORS)
    city = models.CharField("İl", max_length=30, choices=CITY_CHOICES, blank=True)
    budget = models.CharField("Aylık bütçe", max_length=10, choices=BUDGETS)
    goal = models.CharField("Hedef", max_length=20, choices=GOALS)
    has_content = models.CharField("İçerik durumu", max_length=10, choices=CONTENT, blank=True)
    timeline = models.CharField("Başlangıç", max_length=20, choices=TIMELINES, blank=True)
    message = models.TextField("Mesaj", blank=True)

    score = models.PositiveSmallIntegerField("Kalite skoru", default=0)
    status = models.CharField("Durum", max_length=20, choices=STATUSES, default="new")
    notes = models.TextField("İç notlar", blank=True)

    source_page = models.CharField("Geldiği sayfa", max_length=300, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=150, blank=True)
    utm_term = models.CharField(max_length=150, blank=True)
    gclid = models.CharField("Google Ads tıklama kimliği (gclid)", max_length=200, blank=True)
    ga_client_id = models.CharField("GA4 client_id", max_length=64, blank=True)
    ga_session_id = models.CharField("GA4 session_id", max_length=32, blank=True)
    deal_value = models.PositiveIntegerField("Anlaşma değeri (aylık ₺)", null=True, blank=True,
                                             help_text="Kazanıldı yapınca GA4'e dönüşüm değeri olarak gider.")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    notified = models.BooleanField("Bildirim gönderildi", default=False)
    created_at = models.DateTimeField("Tarih", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Lead'ler"

    def __str__(self):
        return f"{self.name} — {self.get_sector_display()}"

    @classmethod
    def from_db(cls, db, field_names, values):
        obj = super().from_db(db, field_names, values)
        obj._loaded_status = obj.status
        return obj

    def save(self, *args, **kwargs):
        previous = getattr(self, "_loaded_status", None)
        super().save(*args, **kwargs)
        if previous is not None and previous != self.status:
            from .ga4 import send_status_event  # avoid import cycle
            send_status_event(self)
        self._loaded_status = self.status

    # Rough monthly value per budget band — used as GA4 lead value (TRY).
    BUDGET_VALUE = {"lt50": 0, "50-100": 50000, "100-250": 90000, "250+": 150000}

    @property
    def estimated_value(self) -> int:
        return self.BUDGET_VALUE.get(self.budget, 0)

    def compute_score(self) -> int:
        """0–100 quality score: budget matters most, then intent signals."""
        score = {"lt50": 5, "50-100": 45, "100-250": 60, "250+": 70}.get(self.budget, 0)
        score += {"hemen": 15, "1-ay": 10, "arastiriyorum": 0}.get(self.timeline, 0)
        score += 8 if self.website else 0
        score += 7 if len(self.message) >= 40 else 0
        return min(score, 100)

    @property
    def tier(self) -> str:
        if self.score >= 70:
            return "A"
        if self.score >= 45:
            return "B"
        return "C"

    @property
    def whatsapp_url(self) -> str:
        digits = "".join(ch for ch in self.phone if ch.isdigit())
        if digits.startswith("0"):
            digits = "9" + digits
        elif not digits.startswith("90") and len(digits) == 10:
            digits = "90" + digits
        return f"https://wa.me/{digits}"
