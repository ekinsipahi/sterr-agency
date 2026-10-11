from django.contrib import admin

from .models import DentalInquiry


@admin.register(DentalInquiry)
class DentalInquiryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "kind", "lang", "country", "treatment", "status", "notified")
    list_filter = ("status", "kind", "lang", "treatment")
    list_editable = ("status",)
    search_fields = ("name", "email", "phone", "country", "company", "message")
    readonly_fields = ("created_at", "source_page", "utm_source", "utm_medium", "utm_campaign", "gclid", "ip", "notified")
    fieldsets = (
        (None, {"fields": ("status", "kind", "lang", "name", "email", "phone", "country", "company", "treatment", "message")}),
        ("İç notlar", {"fields": ("notes",)}),
        ("Kaynak", {"classes": ("collapse",), "fields": readonly_fields}),
    )
