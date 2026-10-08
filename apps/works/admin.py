from django.contrib import admin

from .models import CaseMedia, CaseMetric, CaseStudy


class CaseMetricInline(admin.TabularInline):
    model = CaseMetric
    extra = 3


class CaseMediaInline(admin.TabularInline):
    model = CaseMedia
    extra = 2


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "sector", "city", "is_featured", "is_published", "order")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("is_published", "is_featured", "sector")
    search_fields = ("title", "client", "sector")
    prepopulated_fields = {"slug": ("client", "title")}
    inlines = [CaseMetricInline, CaseMediaInline]
