"""İvme (and so Hakimiyet, which includes everything in İvme) gets organic,
location-focused Instagram growth. Kıvılcım does not."""
from django.db import migrations

FEATURE = "Konum odaklı organik Instagram büyümesi"
AFTER = "AI destekli içerik yayılımı"


def forwards(apps, schema_editor):
    package = apps.get_model("core", "Package").objects.filter(slug="ivme").first()
    if package is None:
        return
    lines = [line for line in package.features.splitlines() if line.strip()]
    if FEATURE in lines:
        return
    pos = lines.index(AFTER) + 1 if AFTER in lines else len(lines)
    lines.insert(pos, FEATURE)
    package.features = "\n".join(lines)
    package.save(update_fields=["features"])


def backwards(apps, schema_editor):
    package = apps.get_model("core", "Package").objects.filter(slug="ivme").first()
    if package:
        package.features = "\n".join(l for l in package.features.splitlines() if l.strip() != FEATURE)
        package.save(update_fields=["features"])


class Migration(migrations.Migration):
    dependencies = [("core", "0004_package_features_no_seo_method")]
    operations = [migrations.RunPython(forwards, backwards)]
