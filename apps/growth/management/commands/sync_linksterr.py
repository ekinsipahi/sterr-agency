"""Fetch Linksterr's delivery numbers for every running package (and those canceled in the
last 60 days, so their final days are complete). The dashboard does this on its own when a
customer opens it; this keeps the admin and dispute evidence complete without visits
(e.g. a daily cron). Needs LINKSTERR_AGENCY_TOKEN.

    python manage.py sync_linksterr
"""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone

from apps.growth import linksterr
from apps.growth.models import AgencySubscription


class Command(BaseCommand):
    help = "Fetch Linksterr's daily delivery numbers into the subscriptions' stats."

    def handle(self, *args, **opts):
        if not linksterr.enabled():
            raise CommandError("LINKSTERR_AGENCY_TOKEN is not set.")
        recent = timezone.now() - timedelta(days=60)
        subs = list(AgencySubscription.objects.exclude(started_at=None).filter(
            Q(status__in=("active", "past_due")) | Q(status="canceled", canceled_at__gte=recent)))
        updated = linksterr.sync(subs, force=True)
        self.stdout.write(f"Subscriptions updated: {updated} of {len(subs)}")
