from django.db import migrations

from apps.intl.pricing import DEFAULT_MARKETS


def seed(apps, schema_editor):
    Market = apps.get_model("intl", "Market")
    for lang, (country, currency, usd) in DEFAULT_MARKETS.items():
        Market.objects.get_or_create(lang=lang, defaults={"country": country, "currency": currency, "usd_price": usd})


class Migration(migrations.Migration):
    dependencies = [("intl", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
