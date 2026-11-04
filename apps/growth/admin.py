from django.contrib import admin
from django.utils.html import format_html

from .constants import PROFILE_URL
from .models import AgencySubscription, Customer, FollowerOrder, StripeEvent, SubscriptionStat


class StatInline(admin.TabularInline):
    model = SubscriptionStat
    extra = 0
    fields = ("date", "followers", "likes", "comments")
    ordering = ("-date",)


@admin.register(AgencySubscription)
class AgencySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "account", "platform", "status", "renews", "location", "email", "amount", "created_at")
    list_filter = ("status", "platform", "cancel_at_period_end", "lang", "created_at")
    search_fields = ("handle", "email", "location", "stripe_subscription_id", "stripe_customer_id", "stripe_checkout_session_id")
    readonly_fields = ("user", "amount", "started_at", "current_period_end", "cancel_at_period_end", "canceled_at",
                       "stripe_checkout_session_id", "stripe_subscription_id", "stripe_customer_id", "notified", "mail_error",
                       "ip", "source_page", "utm_source", "utm_medium", "utm_campaign", "gclid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("platform", "handle", "location", "amount", "status", "note")}),
        ("Müşteri", {"fields": ("user", "email", "lang")}),
        ("Abonelik", {"fields": ("started_at", "current_period_end", "cancel_at_period_end", "canceled_at",
                                 "stripe_checkout_session_id", "stripe_subscription_id", "stripe_customer_id")}),
        ("Veriler", {"fields": ("start_followers", "current_followers", "stats_at")}),
        ("E-posta", {"fields": ("notified", "mail_error")}),
        ("Kaynak", {"classes": ("collapse",), "fields": ("ip", "source_page", "utm_source", "utm_medium", "utm_campaign",
                                                       "gclid", "created_at", "updated_at")}),
    )
    inlines = [StatInline]

    @admin.display(description="Hesap", ordering="handle")
    def account(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">@{}</a>', PROFILE_URL[obj.platform].format(obj.handle), obj.handle)

    @admin.display(description="Yenileme / bitiş", ordering="current_period_end")
    def renews(self, obj):
        if not obj.current_period_end or obj.status == "canceled":
            return "-"
        return f"{'Biter' if obj.cancel_at_period_end else 'Yenilenir'} {obj.current_period_end:%d.%m.%Y}"


@admin.register(FollowerOrder)
class FollowerOrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "handle", "platform", "followers", "amount", "status", "email", "created_at")
    list_filter = ("status", "platform")
    search_fields = ("handle", "email")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "email_verified", "lang", "created_at")
    list_filter = ("email_verified", "lang")
    search_fields = ("user__email",)
    raw_id_fields = ("user",)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("type", "event_id", "created_at")
    list_filter = ("type",)
    search_fields = ("event_id",)
