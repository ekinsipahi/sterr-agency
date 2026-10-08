from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """Singleton editable from the admin: logo, trust signals, social links."""

    logo = models.FileField("Logo (SVG/PNG, açık renk)", upload_to="brand/", blank=True,
                            help_text="Boş bırakılırsa yazı logosu kullanılır.")
    favicon = models.FileField("Favicon", upload_to="brand/", blank=True)
    og_image = models.ImageField("Paylaşım görseli (1200×630)", upload_to="brand/", blank=True)

    google_rating = models.DecimalField("Google puanı", max_digits=2, decimal_places=1, null=True, blank=True,
                                        help_text="Örn. 4.9 — boşsa rozet gösterilmez.")
    google_review_count = models.PositiveIntegerField("Google yorum sayısı", null=True, blank=True)
    google_business_url = models.URLField("Google İşletme profili linki", blank=True)

    stat_1_value = models.CharField("İstatistik 1 — değer", max_length=30, blank=True, help_text="Örn. ₺48M+")
    stat_1_label = models.CharField("İstatistik 1 — etiket", max_length=80, blank=True,
                                    help_text="Örn. Müşterilerimize kazandırılan ciro")
    stat_2_value = models.CharField("İstatistik 2 — değer", max_length=30, blank=True)
    stat_2_label = models.CharField("İstatistik 2 — etiket", max_length=80, blank=True)
    stat_3_value = models.CharField("İstatistik 3 — değer", max_length=30, blank=True)
    stat_3_label = models.CharField("İstatistik 3 — etiket", max_length=80, blank=True)

    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "Site ayarları"

    def __str__(self):
        return "Site ayarları"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    @classmethod
    def load(cls):
        obj = cache.get("site_settings")
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set("site_settings", obj, 300)
        return obj

    @property
    def stats(self):
        pairs = [(self.stat_1_value, self.stat_1_label), (self.stat_2_value, self.stat_2_label),
                 (self.stat_3_value, self.stat_3_label)]
        return [(v, lbl) for v, lbl in pairs if v and lbl]


class Package(models.Model):
    name = models.CharField("Paket adı", max_length=60)
    slug = models.SlugField(unique=True)
    tagline = models.CharField("Kısa açıklama", max_length=160)
    price = models.PositiveIntegerField("Aylık fiyat (₺)")
    price_prefix = models.CharField("Fiyat öneki", max_length=20, blank=True, help_text="Örn. 'başlayan'")
    ideal_for = models.CharField("Kimler için", max_length=200)
    features = models.TextField("Özellikler", help_text="Her satıra bir özellik.")
    is_featured = models.BooleanField("Öne çıkan", default=False)
    order = models.PositiveSmallIntegerField("Sıra", default=0)
    is_active = models.BooleanField("Yayında", default=True)

    class Meta:
        ordering = ["order", "price"]
        verbose_name = "Paket"
        verbose_name_plural = "Paketler"

    def __str__(self):
        return self.name

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class Testimonial(models.Model):
    SOURCE_GOOGLE, SOURCE_DIRECT = "google", "direct"
    SOURCES = [(SOURCE_GOOGLE, "Google yorumu"), (SOURCE_DIRECT, "Doğrudan referans")]

    author = models.CharField("Ad Soyad", max_length=80)
    role = models.CharField("Unvan / işletme", max_length=120, blank=True)
    quote = models.TextField("Yorum")
    rating = models.PositiveSmallIntegerField("Puan", default=5)
    source = models.CharField("Kaynak", max_length=10, choices=SOURCES, default=SOURCE_GOOGLE)
    source_url = models.URLField("Yorum linki", blank=True)
    avatar = models.ImageField(upload_to="testimonials/", blank=True)
    is_published = models.BooleanField("Yayında", default=True)
    order = models.PositiveSmallIntegerField("Sıra", default=0)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Müşteri yorumu"
        verbose_name_plural = "Müşteri yorumları"

    def __str__(self):
        return f"{self.author} ({self.get_source_display()})"
