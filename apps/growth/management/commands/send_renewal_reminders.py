"""Renewal reminders for packages that renew within --days
(default 3). Each billing period gets one reminder, whether it went from here or from
Stripe's invoice.upcoming webhook. Safe to run as often as you like (e.g. a daily cron).

    python manage.py send_renewal_reminders
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import F, Q
from django.utils import timezone

from apps.growth.models import AgencySubscription
from apps.growth.views import send_reminder


class Command(BaseCommand):
    help = "Email the renewal reminder to packages that renew within --days."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=3)

    def handle(self, *args, **opts):
        now = timezone.now()
        due = (AgencySubscription.objects.filter(status="active", cancel_at_period_end=False,
                                                 current_period_end__gt=now,
                                                 current_period_end__lte=now + timedelta(days=opts["days"]))
               .exclude(stripe_subscription_id="")
               .filter(Q(reminded_for__isnull=True) | ~Q(reminded_for=F("current_period_end"))))
        sent = sum(send_reminder(sub) for sub in due)
        self.stdout.write(f"Reminders sent: {sent}")
