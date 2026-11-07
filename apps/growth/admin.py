from django.contrib import admin
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.html import format_html

from . import evidence, linksterr
from .constants import PROFILE_URL
from .models import AccountActivity, AgencySubscription, Customer, Dispute, FollowerOrder, StripeEvent, SubscriptionStat


def _panel_link(user_id, lang):
    """Opens the customer's dashboard read-only (staff only; nobody signs in as the customer)."""
    if not user_id:
        return "-"
    return format_html('<a href="{}?lang={}" target="_blank" rel="noopener">Paneli gör</a>',
                       reverse("growth:view_as", args=[user_id]), lang or "en")


class StatInline(admin.TabularInline):
    model = SubscriptionStat
    extra = 0
    fields = ("date", "followers", "new_followers", "likes", "comments", "impressions", "visits", "confirms")
    ordering = ("-date",)


class DisputeInline(admin.TabularInline):
    model = Dispute
    extra = 0
    can_delete = False
    fields = readonly_fields = ("dispute_id", "amount", "reason", "status", "due_by", "evidence_staged", "created_at")


@admin.register(AgencySubscription)
class AgencySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("pk", "account", "platform", "status", "renews", "projection_text", "location", "email", "amount",
                    "created_at", "panel")
    list_filter = ("status", "platform", "cancel_at_period_end", "lang", "created_at")
    search_fields = ("handle", "email", "location", "stripe_subscription_id", "stripe_customer_id", "stripe_checkout_session_id")
    readonly_fields = ("user", "amount", "started_at", "current_period_end", "cancel_at_period_end", "canceled_at",
                       "cancel_requested_at", "cancel_source", "reminded_for", "terms_accepted_at", "terms_version",
                       "user_agent", "evidence_link", "panel", "projection_text",
                       "stripe_checkout_session_id", "stripe_subscription_id", "stripe_customer_id", "notified", "mail_error",
                       "ip", "source_page", "utm_source", "utm_medium", "utm_campaign", "gclid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("platform", "handle", "location", "amount", "status", "note")}),
        ("Müşteri", {"fields": ("user", "email", "lang", "panel", "terms_accepted_at", "terms_version", "user_agent", "evidence_link")}),
        ("Abonelik", {"fields": ("started_at", "current_period_end", "cancel_at_period_end", "cancel_requested_at",
                                 "cancel_source", "canceled_at", "reminded_for",
                                 "stripe_checkout_session_id", "stripe_subscription_id", "stripe_customer_id")}),
        ("Veriler", {"fields": ("start_followers", "current_followers", "projection_text", "stats_at")}),
        ("E-posta", {"fields": ("notified", "mail_error")}),
        ("Kaynak", {"classes": ("collapse",), "fields": ("ip", "source_page", "utm_source", "utm_medium", "utm_campaign",
                                                       "gclid", "created_at", "updated_at")}),
    )
    inlines = [StatInline, DisputeInline]
    actions = ["sync_linksterr"]

    @admin.action(description="Linksterr'dan günlük verileri çek")
    def sync_linksterr(self, request, queryset):
        if not linksterr.enabled():
            self.message_user(request, "LINKSTERR_AGENCY_TOKEN ayarlı değil.", level="error")
            return
        updated = linksterr.sync(list(queryset.exclude(started_at=None)), force=True)
        self.message_user(request, f"{updated} abonelik güncellendi.")

    def get_urls(self):
        return [path("<int:pk>/evidence/", self.admin_site.admin_view(self.evidence_view),
                     name="growth_agencysubscription_evidence")] + super().get_urls()

    def evidence_view(self, request, pk):
        sub = get_object_or_404(AgencySubscription, pk=pk)
        linksterr.sync([sub], force=True)
        fields = [(name.replace("_", " ").capitalize(), text) for name, text in evidence.build(sub).items()]
        return render(request, "admin/growth/evidence.html", {**self.admin_site.each_context(request), "sub": sub,
                                                               "fields": fields, "title": f"Kanıt paketi: @{sub.handle}"})

    @admin.display(description="Dispute kanıtı")
    def evidence_link(self, obj):
        if not obj.pk:
            return "-"
        return format_html('<a href="{}" target="_blank">Kanıt paketini aç (yazdır / PDF)</a>',
                           reverse("admin:growth_agencysubscription_evidence", args=[obj.pk]))

    @admin.display(description="Hesap", ordering="handle")
    def account(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">@{}</a>', PROFILE_URL[obj.platform].format(obj.handle), obj.handle)

    @admin.display(description="Müşteri paneli")
    def panel(self, obj):
        return _panel_link(obj.user_id, obj.lang)

    @admin.display(description="30 gün tahmini")
    def projection_text(self, obj):
        """Linksterr'ın bugünkü hızla 30 günlük ortalama tahmini (müşteri panelinde de görünür)."""
        p = obj.projection
        if not p:
            return "-"
        return f"~{p['new_followers']:,} takipçi ({p['low']:,}–{p['high']:,}) · günde ~{p['per_day']:.0f}".replace(",", ".")

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
    list_display = ("user", "email_verified", "lang", "created_at", "panel")
    list_filter = ("email_verified", "lang")
    search_fields = ("user__email",)
    raw_id_fields = ("user",)
    readonly_fields = ("panel",)

    @admin.display(description="Müşteri paneli")
    def panel(self, obj):
        return _panel_link(obj.user_id, obj.lang)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("type", "event_id", "created_at")
    list_filter = ("type",)
    search_fields = ("event_id",)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("dispute_id", "subscription", "amount", "reason", "status", "due_by", "evidence_staged", "created_at")
    list_filter = ("status", "reason", "evidence_staged")
    search_fields = ("dispute_id", "subscription__handle", "subscription__email")
    readonly_fields = [f.name for f in Dispute._meta.fields]


@admin.register(AccountActivity)
class AccountActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "ip", "at")
    list_filter = ("kind",)
    search_fields = ("user__email", "ip")
    readonly_fields = ("user", "kind", "ip", "user_agent", "at")
