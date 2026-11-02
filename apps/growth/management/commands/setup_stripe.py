"""Stripe setup for the one-time follower packages: creates the webhook endpoint, or
updates the events of the existing one. Prices are inline in Checkout (see
apps/growth/packages.py), so no products or prices are created. Safe to run again.

    STRIPE_SECRET_KEY=sk_... python manage.py setup_stripe
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import stripe

WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "charge.refunded",
]


class Command(BaseCommand):
    help = "Create or update the Stripe webhook for follower package orders."

    def add_arguments(self, parser):
        parser.add_argument("--site-url", default=settings.SITE_URL, help="Public origin for the webhook URL.")

    def handle(self, *args, **opts):
        if not settings.STRIPE_SECRET_KEY:
            raise CommandError("STRIPE_SECRET_KEY is not set.")
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
        url = f"{opts['site_url'].rstrip('/')}/growth/stripe/webhook/"
        existing = [w for w in client.v1.webhook_endpoints.list(params={"limit": 100}).data if w.url == url]
        if existing:
            endpoint = existing[0]
            client.v1.webhook_endpoints.update(endpoint.id, params={"enabled_events": WEBHOOK_EVENTS,
                                                                    "description": "Sterr follower packages"})
            self.stdout.write(f"Webhook exists: {endpoint.id} (events updated; its secret is in the Stripe dashboard)")
            return
        endpoint = client.v1.webhook_endpoints.create(params={"url": url, "enabled_events": WEBHOOK_EVENTS,
                                                              "description": "Sterr follower packages"})
        self.stdout.write(f"Created webhook {endpoint.id} → {url}")
        self.stdout.write("\nPut this in .env and in Render → Environment:\n")
        self.stdout.write(f"STRIPE_WEBHOOK_SECRET={endpoint.secret}")
