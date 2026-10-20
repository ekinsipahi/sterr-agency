"""One-time Stripe setup for the organic Instagram growth subscription.

Creates (or reuses) the $99/month price, a customer portal configuration where
cancellation takes effect at the end of the paid month, and the webhook endpoint.
Prints the env values to put in .env and on Render. Safe to run again.

    STRIPE_SECRET_KEY=sk_... python manage.py setup_stripe
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import stripe

LOOKUP_KEY = "sterr_organic_growth_monthly_usd"
WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
]


class Command(BaseCommand):
    help = "Create the Stripe price, customer portal and webhook for the Instagram growth subscription."

    def add_arguments(self, parser):
        parser.add_argument("--site-url", default=settings.SITE_URL, help="Public origin for the webhook URL.")

    def handle(self, *args, **opts):
        if not settings.STRIPE_SECRET_KEY:
            raise CommandError("STRIPE_SECRET_KEY is not set.")
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
        amount = settings.GROWTH_PRICE_USD * 100

        prices = client.v1.prices.list(params={"lookup_keys": [LOOKUP_KEY], "active": True, "limit": 1}).data
        if prices and prices[0].unit_amount == amount:
            price = prices[0]
            self.stdout.write(f"Price exists: {price.id}")
        else:
            product = client.v1.products.create(params={
                "name": "Organic Instagram Growth",
                "description": "Real, organic Instagram followers, location-targeted. No bots, no password.",
            })
            price = client.v1.prices.create(params={
                "product": product.id, "currency": "usd", "unit_amount": amount,
                "recurring": {"interval": "month"}, "lookup_key": LOOKUP_KEY, "transfer_lookup_key": True,
            })
            self.stdout.write(f"Created price {price.id} (${settings.GROWTH_PRICE_USD}/month)")

        portal = client.v1.billing_portal.configurations.create(params={
            "business_profile": {"headline": "Sterr Agency · Organic Instagram Growth",
                                 "privacy_policy_url": f"{opts['site_url']}/gizlilik-politikasi/",
                                 "terms_of_service_url": f"{opts['site_url']}/kullanim-kosullari/"},
            "features": {
                "payment_method_update": {"enabled": True},
                "invoice_history": {"enabled": True},
                "customer_update": {"enabled": True, "allowed_updates": ["email"]},
                # Cancelling stops the next renewal; the month already paid is not refunded.
                "subscription_cancel": {"enabled": True, "mode": "at_period_end", "proration_behavior": "none"},
            },
        })
        self.stdout.write(f"Created portal configuration {portal.id}")

        url = f"{opts['site_url'].rstrip('/')}/growth/stripe/webhook/"
        existing = [w for w in client.v1.webhook_endpoints.list(params={"limit": 100}).data if w.url == url]
        if existing:
            endpoint = existing[0]
            client.v1.webhook_endpoints.update(endpoint.id, params={"enabled_events": WEBHOOK_EVENTS})
            secret = None
            self.stdout.write(f"Webhook exists: {endpoint.id} (events updated; its secret is in the Stripe dashboard)")
        else:
            endpoint = client.v1.webhook_endpoints.create(params={"url": url, "enabled_events": WEBHOOK_EVENTS,
                                                                  "description": "Sterr organic Instagram growth"})
            secret = endpoint.secret
            self.stdout.write(f"Created webhook {endpoint.id} → {url}")

        self.stdout.write("\nPut these in .env and in Render → Environment:\n")
        self.stdout.write(f"STRIPE_PRICE_ID={price.id}")
        self.stdout.write(f"STRIPE_PORTAL_CONFIG={portal.id}")
        if secret:
            self.stdout.write(f"STRIPE_WEBHOOK_SECRET={secret}")
