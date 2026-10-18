"""Package feature lists: say "SEO", not how we do it (no programmatic SEO,
keyword or forum details)."""
from django.db import migrations

REPLACE = {
    "Türkçe anahtar kelime SEO'su ve içerik mimarisi": "SEO",
    "Programatik SEO sayfaları": None,
    "AI destekli forum ve soru-cevap içerik yayılımı": "AI destekli içerik yayılımı",
    "81 il ölçeğinde programatik SEO": "Kapsamlı SEO",
}


def forwards(apps, schema_editor):
    for package in apps.get_model("core", "Package").objects.all():
        lines = []
        for line in package.features.splitlines():
            new = REPLACE.get(line.strip(), line)
            if new is not None:
                lines.append(new)
        package.features = "\n".join(lines)
        package.save(update_fields=["features"])


class Migration(migrations.Migration):
    dependencies = [("core", "0003_sitesettings_google_review_url")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
