from django.core.management.base import BaseCommand

from apps.intl.models import FxRate
from apps.intl.pricing import refresh_rates


class Command(BaseCommand):
    help = "Fetch today's USD exchange rates for the international price display (run daily from cron)."

    def handle(self, *args, **options):
        ok = refresh_rates(force=True)
        for r in FxRate.objects.order_by("currency"):
            self.stdout.write(f"1 USD = {r.rate} {r.currency}  ({r.updated_at:%Y-%m-%d %H:%M})")
        if not ok:
            self.stderr.write("Fetch failed; stored/fallback rates are still used.")
