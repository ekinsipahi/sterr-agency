from django.contrib import admin
from django.utils.html import format_html

from .content import PROFILE_URL
from .models import GrowthSubscription, StripeEvent


@admin.register(GrowthSubscription)
class GrowthSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("handle", "platform", "location", "email", "status", "notified", "cancel_at_period_end", "current_period_end", "lang", "created_at")
    list_filter = ("platform", "status", "notified", "cancel_at_period_end", "lang", "created_at")
    search_fields = ("instagram", "email", "location", "stripe_customer_id", "stripe_subscription_id")
    readonly_fields = ("stripe_customer_id", "stripe_subscription_id", "stripe_checkout_session_id", "current_period_end",
                       "cancel_at_period_end", "welcomed", "notified", "mail_error", "ip", "source_page", "utm_source", "utm_medium",
                       "utm_campaign", "gclid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("platform", "instagram", "location", "email", "lang", "status", "note")}),
        ("E-posta", {"fields": ("notified", "mail_error")}),
        ("Stripe", {"fields": ("stripe_customer_id", "stripe_subscription_id", "stripe_checkout_session_id",
                               "current_period_end", "cancel_at_period_end", "welcomed")}),
        ("Kaynak", {"classes": ("collapse",), "fields": ("ip", "source_page", "utm_source", "utm_medium", "utm_campaign",
                                                       "gclid", "created_at", "updated_at")}),
    )

    @admin.display(description="Hesap", ordering="instagram")
    def handle(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">@{}</a>', PROFILE_URL[obj.platform].format(obj.instagram), obj.instagram)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("type", "event_id", "created_at")
    list_filter = ("type",)
    search_fields = ("event_id",)
