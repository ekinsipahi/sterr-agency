from django.conf import settings
from django.db import models

from .constants import PLATFORM_NAMES
from .plan import CHOICES as PLAN_CHOICES, comments_for, likes_for


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
    """Legacy: the one-time follower packages sold before the monthly agency package.
    Kept for the orders already placed; new sales are AgencySubscription."""

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
    package = models.CharField("Paket", max_length=8)
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
        verbose_name = "Eski takipçi siparişi"
        verbose_name_plural = "Eski takipçi siparişleri"

    def __str__(self):
        return f"#{self.pk} @{self.handle} {self.followers} · {self.get_status_display()}"

    @property
    def platform_name(self):
        return PLATFORM_NAMES[self.platform]


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


class AgencySubscription(models.Model):
    """A monthly influencer package for one Instagram or TikTok account (see plan.py)."""

    STATUS = [
        ("pending", "Ödeme bekleniyor"),
        ("requested", "Başvuru (ödeme kapalıyken)"),
        ("active", "Aktif"),
        ("past_due", "Ödeme başarısız"),
        ("canceled", "İptal edildi"),
    ]
    PLATFORMS = [("instagram", "Instagram"), ("tiktok", "TikTok")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="growth_subscriptions")
    email = models.EmailField("E-posta")
    platform = models.CharField("Platform", max_length=12, choices=PLATFORMS, default="instagram")
    handle = models.CharField("Kullanıcı adı", max_length=30, help_text="@ olmadan")
    location = models.CharField("Hedef konum", max_length=120)
    plan = models.CharField("Paket", max_length=12, choices=PLAN_CHOICES, default="starter")
    amount = models.DecimalField("Aylık tutar (USD)", max_digits=8, decimal_places=2)
    lang = models.CharField("Dil", max_length=5, default="en")
    status = models.CharField("Durum", max_length=12, choices=STATUS, default="pending")
    started_at = models.DateTimeField("Başladı", null=True, blank=True)
    current_period_end = models.DateTimeField("Dönem bitişi", null=True, blank=True)
    cancel_at_period_end = models.BooleanField("Dönem sonunda bitecek", default=False)
    canceled_at = models.DateTimeField("İptal", null=True, blank=True)
    CANCEL_SOURCES = [("account", "Hesap paneli"), ("stripe", "Stripe portalı / panel")]
    cancel_requested_at = models.DateTimeField("İptal talebi", null=True, blank=True)
    cancel_source = models.CharField("İptal nereden", max_length=10, choices=CANCEL_SOURCES, blank=True)
    reminded_for = models.DateTimeField("Hatırlatma gönderilen dönem", null=True, blank=True,
                                        help_text="Yenileme hatırlatması bu dönem bitişi için gönderildi")
    # Evidence of what the customer agreed to: the required terms box on the order form.
    terms_accepted_at = models.DateTimeField("Şartlar kabul edildi", null=True, blank=True)
    terms_version = models.CharField("Şart sürümü", max_length=20, blank=True)
    user_agent = models.CharField("Tarayıcı", max_length=300, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=128, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=64, blank=True, db_index=True)
    stripe_customer_id = models.CharField(max_length=64, blank=True, db_index=True)
    # Filled in by the growth system through the stats API (see api.py).
    start_followers = models.PositiveIntegerField("Başlangıç takipçi", null=True, blank=True)
    current_followers = models.PositiveIntegerField("Güncel takipçi", null=True, blank=True)
    stats_at = models.DateTimeField("Son veri", null=True, blank=True)
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
        verbose_name = "Influencer paketi aboneliği"
        verbose_name_plural = "Influencer paketi abonelikleri"

    def __str__(self):
        return f"#{self.pk} @{self.handle} {self.platform_name} {self.get_plan_display()} · {self.get_status_display()}"

    @property
    def platform_name(self):
        return PLATFORM_NAMES[self.platform]

    def daily(self):
        """[{date, followers, likes, comments, visits, countries}] per day, oldest first. New
        followers are what the growth system counted for the day (without that, the change in the
        account's follower count); likes and comments are counted from them unless the growth
        system sent its own. visits: people who opened the profile from our network (or None)."""
        rows, previous = [], self.start_followers
        for stat in sorted(self.stats.all(), key=lambda s: s.date):
            gained = stat.new_followers
            if gained is None and stat.followers is not None and previous is not None:
                gained = max(stat.followers - previous, 0)
            base = gained or 0
            rows.append({"date": stat.date, "followers": gained,
                         "likes": stat.likes if stat.likes is not None else likes_for(base),
                         "comments": stat.comments if stat.comments is not None else comments_for(base),
                         "visits": stat.visits, "countries": stat.countries or {}})
            if stat.followers is not None:
                previous = stat.followers
        return rows

    @property
    def gained(self):
        """New followers since the package started (None before the first reading)."""
        counted = [d["followers"] for d in self.daily() if d["followers"] is not None]
        return sum(counted) if counted else None


class SubscriptionStat(models.Model):
    """One day of numbers from the growth system: the new followers we brought that day and
    the account's follower count. Likes and comments are counted from the new followers
    (plan.likes_for / comments_for) unless the growth system sends them. Feeds the dashboard."""

    subscription = models.ForeignKey(AgencySubscription, on_delete=models.CASCADE, related_name="stats")
    date = models.DateField("Gün", db_index=True)
    followers = models.PositiveIntegerField("Hesap takipçi", null=True, blank=True)
    # Sent by the growth system; when missing, the change in the follower count is used.
    new_followers = models.PositiveIntegerField("Yeni takipçi", null=True, blank=True)
    likes = models.PositiveIntegerField("Beğeni", null=True, blank=True, help_text="Boşsa yeni takipçi × 2,5")
    comments = models.PositiveIntegerField("Yorum", null=True, blank=True, help_text="Boşsa yeni takipçi ÷ 10")
    # Delivery evidence from the growth system: how many real people were shown the profile,
    # went to it and said they followed, and from which countries ({"DE": {"impressions": ...}}).
    impressions = models.PositiveIntegerField("Gösterim", null=True, blank=True, help_text="Profilin gösterildiği kişi")
    visits = models.PositiveIntegerField("Profil ziyareti", null=True, blank=True)
    confirms = models.PositiveIntegerField("Takip onayı", null=True, blank=True, help_text="“Takip ettim” diyen kişi")
    countries = models.JSONField("Ülkeler", default=dict, blank=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "Günlük veri"
        verbose_name_plural = "Günlük veriler"
        constraints = [models.UniqueConstraint(fields=["subscription", "date"], name="growth_stat_subscription_date")]

    def __str__(self):
        return f"#{self.subscription_id} {self.date} {self.followers}"


class AccountActivity(models.Model):
    """Sign-ins and dashboard visits of customer accounts: evidence that a customer used
    the service (Stripe dispute access_activity_log). Dashboard visits at most once an hour."""

    KINDS = [("login", "Giriş"), ("dashboard", "Panel görüntüleme"), ("cancel_page", "İptal sayfası")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="growth_activity")
    kind = models.CharField("Ne", max_length=12, choices=KINDS)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField("Tarayıcı", max_length=300, blank=True)
    at = models.DateTimeField("Zaman", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-at"]
        verbose_name = "Hesap hareketi"
        verbose_name_plural = "Hesap hareketleri"

    def __str__(self):
        return f"{self.user} {self.kind} {self.at:%Y-%m-%d %H:%M}"


class Dispute(models.Model):
    """A Stripe dispute (chargeback) on one of our subscriptions. Evidence is staged on Stripe
    when it opens; the team reviews it and presses Submit in the Stripe Dashboard."""

    subscription = models.ForeignKey(AgencySubscription, on_delete=models.CASCADE, related_name="disputes")
    dispute_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField("Tutar (USD)", max_digits=8, decimal_places=2)
    reason = models.CharField("Sebep", max_length=40, blank=True)
    status = models.CharField("Durum", max_length=40, blank=True)
    due_by = models.DateTimeField("Son kanıt tarihi", null=True, blank=True)
    evidence_staged = models.BooleanField("Kanıt Stripe'a yüklendi", default=False)
    error = models.TextField("Hata", blank=True)
    created_at = models.DateTimeField("Açıldı", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "İtiraz (dispute)"
        verbose_name_plural = "İtirazlar (dispute)"

    def __str__(self):
        return f"{self.dispute_id} #{self.subscription_id} {self.status}"


class StripeEvent(models.Model):
    """Processed webhook event ids, so a retried delivery is handled once."""

    event_id = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.event_id}"
