import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "tier_badge", "sector", "budget", "city", "status", "contact_links")
    list_display_links = ("created_at", "name")
    list_editable = ("status",)
    list_filter = ("status", "budget", "sector", "goal", "timeline", "has_content", "created_at")
    search_fields = ("name", "email", "phone", "company", "website", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("score", "created_at", "source_page", "utm_source", "utm_medium", "utm_campaign",
                       "utm_term", "gclid", "ga_client_id", "ga_session_id", "ip", "user_agent", "notified")
    actions = ["export_csv", "mark_contacted"]
    fieldsets = (
        ("Kişi", {"fields": ("name", "company", "phone", "email", "website", "city")}),
        ("Başvuru", {"fields": ("sector", "goal", "budget", "has_content", "timeline", "message")}),
        ("Takip", {
            "description": "Durum değişikliği GA4'e lead event'i olarak gider (GA4_API_SECRET tanımlıysa).",
            "fields": ("status", "deal_value", "score", "notes"),
        }),
        ("Kaynak", {"classes": ("collapse",), "fields": ("source_page", "utm_source", "utm_medium",
                                                         "utm_campaign", "utm_term", "gclid", "ga_client_id",
                                                         "ga_session_id", "ip", "user_agent", "notified",
                                                         "created_at")}),
    )

    @admin.display(description="Skor", ordering="score")
    def tier_badge(self, obj):
        colors = {"A": "#1f9d55", "B": "#c98a00", "C": "#8a8a8a"}
        return format_html('<b style="color:{}">{} · {}</b>', colors[obj.tier], obj.tier, obj.score)

    @admin.display(description="İletişim")
    def contact_links(self, obj):
        return format_html('<a href="{}" target="_blank">WhatsApp</a> · <a href="tel:{}">Ara</a> · '
                           '<a href="mailto:{}">E-posta</a>', obj.whatsapp_url, obj.phone, obj.email)

    @admin.action(description="Seçilenleri CSV olarak indir")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="leads.csv"'
        resp.write("\ufeff")  # Excel-friendly UTF-8
        writer = csv.writer(resp)
        cols = ["created_at", "name", "company", "phone", "email", "website", "city", "sector", "goal",
                "budget", "has_content", "timeline", "score", "status", "message", "source_page",
                "utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid", "deal_value"]
        writer.writerow(cols)
        for lead in queryset:
            writer.writerow([getattr(lead, c) for c in cols])
        return resp

    @admin.action(description="İletişime geçildi olarak işaretle")
    def mark_contacted(self, request, queryset):
        for lead in queryset.exclude(status="contacted"):  # save() so GA4 gets working_lead
            lead.status = "contacted"
            lead.save(update_fields=["status"])
