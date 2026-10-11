from django.contrib import admin

from .models import FxRate, IntlLead, Market
from .pricing import price_for


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("lang", "country", "usd_price", "currency", "local_price")
    list_editable = ("usd_price", "currency")

    @admin.display(description="Sitede görünen başlangıç fiyatı")
    def local_price(self, obj):
        return price_for(obj.lang)["display"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FxRate)
class FxRateAdmin(admin.ModelAdmin):
    list_display = ("currency", "rate", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(IntlLead)
class IntlLeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "lang", "country", "interest", "company", "status", "notified")
    list_filter = ("status", "lang", "interest")
    list_editable = ("status",)
    search_fields = ("name", "email", "phone", "company", "country", "message")
    readonly_fields = ("created_at", "quoted_price", "usd_price", "source_page", "utm_source", "utm_medium",
                       "utm_campaign", "gclid", "ip", "notified")
    fieldsets = (
        (None, {"fields": ("status", "lang", "interest", "name", "email", "phone", "company", "website", "country", "message")}),
        ("İç notlar", {"fields": ("notes",)}),
        ("Kaynak", {"classes": ("collapse",), "fields": readonly_fields}),
    )
