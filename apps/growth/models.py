from django.db import models


class GrowthSubscription(models.Model):
    """One $99/mo organic Instagram growth subscription. No user accounts: the
    customer is identified by email; Stripe holds the billing side."""

    STATUS = [
        ("pending", "Ödeme bekleniyor"),
        ("active", "Aktif"),
        ("past_due", "Ödeme başarısız"),
        ("canceled", "İptal edildi"),
    ]

    email = models.EmailField("E-posta")
    instagram = models.CharField("Instagram", max_length=30, help_text="@ olmadan")
    location = models.CharField("Hedef konum", max_length=120)
    lang = models.CharField("Dil", max_length=5, default="en")
    status = models.CharField("Durum", max_length=12, choices=STATUS, default="pending")
    cancel_at_period_end = models.BooleanField("Dönem sonunda iptal", default=False)
    current_period_end = models.DateTimeField("Dönem bitişi", null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=64, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=64, blank=True, db_index=True)
    stripe_checkout_session_id = models.CharField(max_length=128, blank=True)
    welcomed = models.BooleanField("Hoş geldin e-postası", default=False)
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
        verbose_name = "Instagram aboneliği"
        verbose_name_plural = "Instagram abonelikleri"

    def __str__(self):
        return f"@{self.instagram} · {self.get_status_display()}"


class StripeEvent(models.Model):
    """Processed webhook event ids, so a retried delivery is handled once."""

    event_id = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.event_id}"
