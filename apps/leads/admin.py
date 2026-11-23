import csv

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html

from . import phonebook
from .models import Lead, PhoneBook


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "name", "phone", "tier_badge", "sector", "budget", "city", "status", "contact_links")
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


@admin.register(PhoneBook)
class PhoneBookAdmin(admin.ModelAdmin):
    """One read-only page: every phone number the forms collected, whose it is and why it was asked for."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        source = request.GET.get("source", "")
        if source not in phonebook.SOURCES:
            source = ""
        q = request.GET.get("q", "").strip()
        rows = phonebook.rows(source, q)
        counts = {key: 0 for key in phonebook.SOURCES}
        for row in rows:
            counts[row["source"]] += 1
        page = Paginator(rows, 100).get_page(request.GET.get("p"))
        return render(request, "admin/leads/phonebook.html", {
            **self.admin_site.each_context(request),
            "title": "Telefon rehberi",
            "opts": self.model._meta,
            "page": page,
            "total": len(rows),
            "q": q,
            "source": source,
            "sources": [(key, info["label"], info["why"], counts[key]) for key, info in phonebook.SOURCES.items()],
        })
