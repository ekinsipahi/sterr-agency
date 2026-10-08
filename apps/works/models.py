from django.db import models
from django.urls import reverse


class CaseStudy(models.Model):
    title = models.CharField("Başlık", max_length=140, help_text="Örn. 'Fizik öğretmenine 3 ayda 42 yeni öğrenci'")
    slug = models.SlugField(unique=True)
    client = models.CharField("Müşteri / marka", max_length=100)
    sector = models.CharField("Sektör", max_length=80)
    city = models.CharField("Şehir", max_length=40, blank=True)
    summary = models.TextField("Özet", help_text="Listede görünen 1–2 cümle.")
    challenge = models.TextField("Sorun", blank=True)
    approach = models.TextField("Ne yaptık", blank=True)
    result = models.TextField("Sonuç", blank=True)
    cover = models.ImageField("Kapak görseli", upload_to="works/covers/", blank=True)
    video = models.FileField("Video (mp4)", upload_to="works/videos/", blank=True,
                             help_text="Ciro / panel ekran kaydı gibi.")
    video_url = models.URLField("Video linki (YouTube/Vimeo embed)", blank=True)
    is_featured = models.BooleanField("Ana sayfada göster", default=False)
    is_published = models.BooleanField("Yayında", default=True)
    order = models.PositiveSmallIntegerField("Sıra", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Çalışma"
        verbose_name_plural = "Çalışmalar"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("works:detail", args=[self.slug])


class CaseMetric(models.Model):
    case = models.ForeignKey(CaseStudy, related_name="metrics", on_delete=models.CASCADE)
    value = models.CharField("Değer", max_length=30, help_text="Örn. +312%, ₺2.4M, 42")
    label = models.CharField("Etiket", max_length=80, help_text="Örn. Organik trafik artışı")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Metrik"
        verbose_name_plural = "Metrikler"


class CaseMedia(models.Model):
    KINDS = [
        ("search_console", "Search Console grafiği"),
        ("revenue", "Ciro / satış paneli"),
        ("ads", "Reklam paneli"),
        ("analytics", "Analytics"),
        ("creative", "Kreatif / içerik"),
        ("other", "Diğer"),
    ]
    case = models.ForeignKey(CaseStudy, related_name="media", on_delete=models.CASCADE)
    kind = models.CharField("Tür", max_length=20, choices=KINDS, default="search_console")
    image = models.ImageField("Görsel", upload_to="works/media/")
    caption = models.CharField("Açıklama", max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Görsel"
        verbose_name_plural = "Görseller (Search Console, ciro vb.)"
