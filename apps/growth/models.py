from datetime import timedelta

from django.conf import settings
from django.db import models

from .constants import PLATFORM_NAMES
from .packages import CHOICES as PACKAGE_CHOICES, PACKAGE_BY_KEY


class Customer(models.Model):
    """What a site account needs beyond Django's User (username = email)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer")
    email_verified = models.BooleanField("E-posta onaylı", default=False)
    lang = models.CharField("Dil", max_length=5, default="en")
    created_at = models.DateTimeField("Oluşturuldu", auto_now_add=True)

    class Meta:
        verbose_name = "Müşteri hesabı"
        verbose_name_plural = "Müşteri hesapları"

    def __str__(self):
        return self.user.email


class FollowerOrder(models.Model):
    """A one-time follower package for one Instagram or TikTok account."""

    STATUS = [
        ("pending", "Ödeme bekleniyor"),
        ("requested", "Başvuru (ödeme kapalıyken)"),
        ("paid", "Ödendi · teslim ediliyor"),
        ("completed", "Tamamlandı"),
        ("refunded", "İade edildi"),
        ("canceled", "İptal"),
    ]
    PLATFORMS = [("instagram", "Instagram"), ("tiktok", "TikTok")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="follower_orders")
    email = models.EmailField("E-posta")
    platform = models.CharField("Platform", max_length=12, choices=PLATFORMS, default="instagram")
    handle = models.CharField("Kullanıcı adı", max_length=30, help_text="@ olmadan")
    location = models.CharField("Hedef konum", max_length=120)
    package = models.CharField("Paket", max_length=8, choices=PACKAGE_CHOICES)
    followers = models.PositiveIntegerField("Takipçi")
    amount = models.DecimalField("Tutar (USD)", max_digits=8, decimal_places=2)
    lang = models.CharField("Dil", max_length=5, default="en")
    status = models.CharField("Durum", max_length=12, choices=STATUS, default="pending")
    paid_at = models.DateTimeField("Ödendi", null=True, blank=True)
    # Filled in by the delivery system through the progress API (see api.py).
    delivered = models.PositiveIntegerField("Teslim edilen", default=0)
    start_followers = models.PositiveIntegerField("Başlangıç takipçi", null=True, blank=True)
    current_followers = models.PositiveIntegerField("Güncel takipçi", null=True, blank=True)
    progress_at = models.DateTimeField("Son veri", null=True, blank=True)
    completed_at = models.DateTimeField("Tamamlandı", null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=128, blank=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=64, blank=True, db_index=True)
    notified = models.BooleanField("Bildirim gönderildi", default=False)
    mail_error = models.TextField("E-posta hatası", blank=True)
    note = models.TextField("Not", blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    utm_source = models.CharField(max_length=150, blank=True)
    utm_medium = models.CharField(max_length=150, blank=True)
    utm_campaign = models.CharField(max_length=150, blank=True)
    gclid = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField("Oluşturuldu", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Takipçi siparişi"
        verbose_name_plural = "Takipçi siparişleri"

    def __str__(self):
        return f"#{self.pk} @{self.handle} {self.followers} · {self.get_status_display()}"

    @property
    def platform_name(self):
        return PLATFORM_NAMES[self.platform]

    @property
    def days(self):
        return PACKAGE_BY_KEY[self.package]["days"]

    @property
    def percent(self):
        return min(100, round(self.delivered * 100 / self.followers)) if self.followers else 0

    def delivery_window(self):
        """(earliest, latest) completion dates, counted from payment (or the request)."""
        start = self.paid_at or self.created_at
        return start + timedelta(days=self.days[0]), start + timedelta(days=self.days[1])


class OrderProgress(models.Model):
    """One reading from the delivery system: how many followers an order has delivered
    and the account's follower count at that moment. Feeds the account dashboard chart."""

    order = models.ForeignKey(FollowerOrder, on_delete=models.CASCADE, related_name="progress")
    at = models.DateTimeField("Zaman", db_index=True)
    delivered = models.PositiveIntegerField("Teslim edilen")
    followers = models.PositiveIntegerField("Hesap takipçi", null=True, blank=True)

    class Meta:
        ordering = ["at"]
        verbose_name = "Teslimat verisi"
        verbose_name_plural = "Teslimat verileri"
        constraints = [models.UniqueConstraint(fields=["order", "at"], name="growth_progress_order_at")]

    def __str__(self):
        return f"#{self.order_id} {self.at:%Y-%m-%d %H:%M} {self.delivered}"


class GrowthSubscription(models.Model):
    """Legacy: the earlier $79/mo plan, kept for the requests it collected. New sales are FollowerOrder."""

    STATUS = [
        ("pending", "Ödeme bekleniyor"),
        ("active", "Aktif"),
        ("past_due", "Ödeme başarısız"),
        ("canceled", "İptal edildi"),
    ]

    email = models.EmailField("E-posta")
    PLATFORMS = [("instagram", "Instagram"), ("tiktok", "TikTok")]

    platform = models.CharField("Platform", max_length=12, choices=PLATFORMS, default="instagram")
    instagram = models.CharField("Kullanıcı adı", max_length=30, help_text="@ olmadan")
    location = models.CharField("Hedef konum", max_length=120)
    lang = models.CharField("Dil", max_length=5, default="en")
    status = models.CharField("Durum", max_length=12, choices=STATUS, default="pending")
    cancel_at_period_end = models.BooleanField("Dönem sonunda iptal", default=False)
    current_period_end = models.DateTimeField("Dönem bitişi", null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=64, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=64, blank=True, db_index=True)
    stripe_checkout_session_id = models.CharField(max_length=128, blank=True)
    welcomed = models.BooleanField("Hoş geldin e-postası", default=False)
    notified = models.BooleanField("Bildirim gönderildi", default=False)
    mail_error = models.TextField("E-posta hatası", blank=True)
    note = models.TextField("Not", blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    utm_source = models.CharField(max_length=150, blank=True)
    utm_medium = models.CharField(max_length=150, blank=True)
    utm_campaign = models.CharField(max_length=150, blank=True)
    gclid = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField("Oluşturuldu", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Eski abonelik başvurusu"
        verbose_name_plural = "Eski abonelik başvuruları"

    def __str__(self):
        return f"@{self.instagram} · {self.get_status_display()}"


class StripeEvent(models.Model):
    """Processed webhook event ids, so a retried delivery is handled once."""

    event_id = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.event_id}"
