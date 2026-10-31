"""Package feature lists: no SEO wording anywhere on the site (user decision)."""
from django.db import migrations

REPLACE = {
    "Google İşletme profili ve temel SEO": "Google İşletme profili",
    "SEO": None,
    "Kapsamlı SEO": None,
}


def forwards(apps, schema_editor):
    for package in apps.get_model("core", "Package").objects.all():
        lines = []
        for line in package.features.splitlines():
            new = REPLACE.get(line.strip(), line)
            if new is not None:
                lines.append(new)
        package.features = "\n".join(lines)
        package.tagline = package.tagline.replace("Reklam + SEO + içerik", "Reklam + içerik")
        package.save(update_fields=["features", "tagline"])


class Migration(migrations.Migration):
    dependencies = [("core", "0005_ivme_instagram_growth")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
