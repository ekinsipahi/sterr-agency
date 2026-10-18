"""Drop the Search Console screenshot from linksterr.com (the site must not name
SEO tools) and strip SEO method details from the seeded case study texts. The
click / impression figures stay as plain metrics."""
from django.core.files.storage import default_storage
from django.db import migrations

LINKSTERR = "linksterr-saas-3000-kullanici"
METRICS = [("2,8 bin", "Google'dan tıklama"), ("86 bin", "Google gösterimi")]
TEXTS = {
    "dentaltourism-tr-16-dil": {
        "summary": "Yurt dışından hasta getirmek için kurduğumuz, 16 dilde yayında olan diş turizmi platformu.",
    },
    "devrimbirikensipahi-yerel-seo": {
        "title": "devrimbirikensipahi.com.tr: Şişli diş hekimi için klinik sitesi",
        "summary": "Şişli'deki diş hekimi için kurulan ikinci klinik sitesi; Türkçe, İngilizce, Felemenkçe ve Almanca.",
    },
}
OLD_MARKERS = ("programatik", "hreflang", "aramalarında", "yerel SEO sitesi")


def forwards(apps, schema_editor):
    CaseStudy = apps.get_model("works", "CaseStudy")
    CaseMedia = apps.get_model("works", "CaseMedia")
    CaseMetric = apps.get_model("works", "CaseMetric")
    for media in CaseMedia.objects.filter(kind="search_console"):
        if media.image and default_storage.exists(media.image.name):
            default_storage.delete(media.image.name)
        media.delete()
    case = CaseStudy.objects.filter(slug=LINKSTERR).first()
    if case:
        start = CaseMetric.objects.filter(case=case).count()
        for i, (value, label) in enumerate(METRICS):
            CaseMetric.objects.get_or_create(case=case, label=label, defaults={"value": value, "order": start + i})
    # Only overwrite texts still in their seeded form; admin edits are kept.
    for slug, fields in TEXTS.items():
        case = CaseStudy.objects.filter(slug=slug).first()
        if not case:
            continue
        for field, value in fields.items():
            if any(m in getattr(case, field) for m in OLD_MARKERS):
                setattr(case, field, value)
        case.save()


class Migration(migrations.Migration):
    dependencies = [("works", "0004_linksterr_search_console")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
