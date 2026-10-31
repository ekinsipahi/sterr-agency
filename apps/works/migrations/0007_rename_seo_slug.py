"""URL without 'seo': devrimbirikensipahi-yerel-seo -> devrimbirikensipahi-klinik-sitesi (old URL 301s)."""
from django.db import migrations

OLD, NEW = "devrimbirikensipahi-yerel-seo", "devrimbirikensipahi-klinik-sitesi"


def forwards(apps, schema_editor):
    apps.get_model("works", "CaseStudy").objects.filter(slug=OLD).update(slug=NEW)


def backwards(apps, schema_editor):
    apps.get_model("works", "CaseStudy").objects.filter(slug=NEW).update(slug=OLD)


class Migration(migrations.Migration):
    dependencies = [("works", "0006_case_texts_no_seo")]
    operations = [migrations.RunPython(forwards, backwards)]
