"""Case study texts: no SEO wording on the site (user decision)."""
from django.db import migrations

REPLACE = [
    ("randevu ve WhatsApp akışı, Google yorumları ve yerel SEO.", "randevu ve WhatsApp akışı ve Google yorumları."),
    (", Google yorumları ve yerel SEO", " ve Google yorumları"),
    ("yerel SEO", "Google görünürlüğü"),
]


def forwards(apps, schema_editor):
    for case in apps.get_model("works", "CaseStudy").objects.all():
        changed = False
        for field in ("title", "summary"):
            text = getattr(case, field)
            for old, new in REPLACE:
                if old in text:
                    text = text.replace(old, new)
            if text != getattr(case, field):
                setattr(case, field, text)
                changed = True
        if changed:
            case.save()


class Migration(migrations.Migration):
    dependencies = [("works", "0005_remove_search_console_media")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
