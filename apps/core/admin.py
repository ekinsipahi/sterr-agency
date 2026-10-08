from django.contrib import admin

from .models import Package, SiteSettings, Testimonial

admin.site.site_header = "Sterr Agency"
admin.site.site_title = "Sterr Agency Yönetim"
admin.site.index_title = "Yönetim paneli"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Marka", {"fields": ("logo", "favicon", "og_image")}),
        ("Google yorumları", {"fields": ("google_rating", "google_review_count", "google_business_url")}),
        ("Ana sayfa istatistikleri", {
            "description": "Yalnızca gerçek ve kanıtlanabilir rakamlar girin. Boş bırakılan satır gösterilmez.",
            "fields": (("stat_1_value", "stat_1_label"), ("stat_2_value", "stat_2_label"),
                       ("stat_3_value", "stat_3_label")),
        }),
        ("Sosyal medya", {"fields": ("instagram_url", "linkedin_url", "youtube_url", "tiktok_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_featured", "is_active", "order")
    list_editable = ("price", "is_featured", "is_active", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "role", "rating", "source", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("source", "is_published")
