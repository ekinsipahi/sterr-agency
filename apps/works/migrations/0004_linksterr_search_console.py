"""Attach linksterr.com's Search Console results (16-month view) to its case study."""
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import migrations

SLUG = "linksterr-saas-3000-kullanici"
IMAGE = "linksterr-search-console.webp"
METRICS = [("2,8 bin", "Google'dan tıklama"), ("86 bin", "Google gösterimi")]


def attach(apps, schema_editor):
    CaseStudy = apps.get_model("works", "CaseStudy")
    CaseMedia = apps.get_model("works", "CaseMedia")
    CaseMetric = apps.get_model("works", "CaseMetric")
    case = CaseStudy.objects.filter(slug=SLUG).first()
    if case is None:
        return
    name = f"works/media/{IMAGE}"
    if not default_storage.exists(name):
        src = settings.BASE_DIR / "static" / "img" / "works" / IMAGE
        if not src.exists():
            return
        with src.open("rb") as fh:
            name = default_storage.save(name, File(fh))
    if not case.media.filter(kind="search_console").exists():
        CaseMedia.objects.create(case=case, kind="search_console", image=name,
                                 caption="linksterr.com · Google Search Console performans grafiği", order=0)
    start = case.metrics.count()
    for i, (value, label) in enumerate(METRICS):
        CaseMetric.objects.get_or_create(case=case, label=label, defaults={"value": value, "order": start + i})


def detach(apps, schema_editor):
    CaseStudy = apps.get_model("works", "CaseStudy")
    case = CaseStudy.objects.filter(slug=SLUG).first()
    if case:
        case.media.filter(kind="search_console").delete()
        case.metrics.filter(label__in=[label for _, label in METRICS]).delete()


class Migration(migrations.Migration):
    dependencies = [("works", "0003_seed_portfolio")]
    operations = [migrations.RunPython(attach, detach)]
