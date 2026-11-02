from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .constants import PROFILE_URL
from .models import Customer, FollowerOrder, GrowthSubscription, StripeEvent
from .notifications import confirm_completed


@admin.register(FollowerOrder)
class FollowerOrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "account", "platform", "followers", "amount", "status", "location", "email", "eta", "created_at")
    list_filter = ("status", "platform", "package", "lang", "created_at")
    search_fields = ("handle", "email", "location", "stripe_checkout_session_id", "stripe_payment_intent_id")
    readonly_fields = ("user", "followers", "amount", "paid_at", "completed_at", "stripe_checkout_session_id",
                       "stripe_payment_intent_id", "notified", "mail_error", "ip", "source_page", "utm_source", "utm_medium",
                       "utm_campaign", "gclid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("platform", "handle", "location", "package", "followers", "amount", "status", "note")}),
        ("Müşteri", {"fields": ("user", "email", "lang")}),
        ("Ödeme", {"fields": ("paid_at", "completed_at", "stripe_checkout_session_id", "stripe_payment_intent_id")}),
        ("E-posta", {"fields": ("notified", "mail_error")}),
        ("Kaynak", {"classes": ("collapse",), "fields": ("ip", "source_page", "utm_source", "utm_medium", "utm_campaign",
                                                       "gclid", "created_at", "updated_at")}),
    )
    actions = ["mark_completed"]

    @admin.display(description="Hesap", ordering="handle")
    def account(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">@{}</a>', PROFILE_URL[obj.platform].format(obj.handle), obj.handle)

    @admin.display(description="Teslim aralığı")
    def eta(self, obj):
        if obj.status not in ("paid", "requested"):
            return "-"
        start, end = obj.delivery_window()
        return f"{start:%d.%m} – {end:%d.%m.%Y}"

    @admin.action(description="Tamamlandı olarak işaretle (müşteriye e-posta gider)")
    def mark_completed(self, request, queryset):
        done = 0
        for order in queryset.filter(status="paid"):
            order.status, order.completed_at = "completed", timezone.now()
            order.save(update_fields=["status", "completed_at", "updated_at"])
            confirm_completed(order)
            done += 1
        self.message_user(request, f"{done} sipariş tamamlandı.", messages.SUCCESS)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "email_verified", "lang", "created_at")
    list_filter = ("email_verified", "lang")
    search_fields = ("user__email",)
    raw_id_fields = ("user",)


@admin.register(GrowthSubscription)
class GrowthSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("instagram", "platform", "location", "email", "status", "notified", "lang", "created_at")
    list_filter = ("platform", "status", "lang", "created_at")
    search_fields = ("instagram", "email", "location")


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("type", "event_id", "created_at")
    list_filter = ("type",)
    search_fields = ("event_id",)
