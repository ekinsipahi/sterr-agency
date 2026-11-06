"""Stripe setup for the monthly influencer packages. Safe to run again.

- One product + one monthly USD price per platform and package (6 in all), found again
  by lookup key `sterr_<platform>_<package>_monthly_usd`. A changed amount in plan.py gets
  a new price; the lookup key moves to it (transfer_lookup_key).
- The customer portal configuration (card, invoices, cancel at period end), tagged
  metadata.app = sterr-growth so billing.portal_url finds it.
- The webhook endpoint: created, or its events updated. A new endpoint's signing
  secret is written to .env (STRIPE_WEBHOOK_SECRET), never printed.

    python manage.py setup_stripe
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import stripe

from apps.growth import plan
from apps.growth.billing import PORTAL_TAG, lookup_key, metadata
from apps.growth.constants import PLATFORM_NAMES, PLATFORMS

WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.upcoming",
    "customer.subscription.updated",
    "customer.subscription.deleted",
]


class Command(BaseCommand):
    help = "Create the influencer package products/prices, the customer portal and the webhook in Stripe."

    def add_arguments(self, parser):
        parser.add_argument("--site-url", default=settings.SITE_URL, help="Public origin for the webhook URL.")
        parser.add_argument("--env-file", default=str(Path(settings.BASE_DIR) / ".env"))

    def handle(self, *args, **opts):
        if not settings.STRIPE_SECRET_KEY:
            raise CommandError("STRIPE_SECRET_KEY is not set.")
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
        site = opts["site_url"].rstrip("/")

        for platform in PLATFORMS:
            for package in plan.PLANS:
                key = lookup_key(platform, package["key"])
                existing = client.v1.prices.list(params={"lookup_keys": [key], "active": True, "limit": 1}).data
                if existing and existing[0].unit_amount == plan.cents(package) and existing[0].recurring:
                    self.stdout.write(f"Price exists: {key} ({existing[0].id})")
                    continue
                low, high = package["followers"]
                product = client.v1.products.create(params={
                    "name": f"{plan.NAMES[package['key']]} · {PLATFORM_NAMES[platform]}",
                    "description": (f"Monthly influencer package, spread over 30 days: real people who follow, like, watch "
                                    f"and comment (typically {low:,}-{high:,} new followers a month). No bots, no password."),
                    "metadata": {"platform": platform, "plan": package["key"]},
                })
                price = client.v1.prices.create(params={
                    "product": product.id, "currency": "usd", "unit_amount": plan.cents(package),
                    "recurring": {"interval": "month"}, "lookup_key": key, "transfer_lookup_key": True,
                    "metadata": {"platform": platform, "plan": package["key"]},
                })
                self.stdout.write(f"Created {key}: ${package['price']} / month ({price.id})")

        portal = {
            "business_profile": {"headline": "Sterr Agency: manage your influencer package",
                                 "privacy_policy_url": f"{site}/gizlilik-politikasi/", "terms_of_service_url": f"{site}/kullanim-kosullari/"},
            "features": {
                "customer_update": {"enabled": True, "allowed_updates": ["email", "address"]},
                "invoice_history": {"enabled": True},
                "payment_method_update": {"enabled": True},
                "subscription_cancel": {"enabled": True, "mode": "at_period_end",
                                        "cancellation_reason": {"enabled": True, "options": [
                                            "too_expensive", "unused", "switched_service", "other"]}},
            },
            "metadata": {"app": PORTAL_TAG},
        }
        found = [c for c in client.v1.billing_portal.configurations.list(params={"active": True, "limit": 100}).data
                 if metadata(c).get("app") == PORTAL_TAG]
        if found:
            client.v1.billing_portal.configurations.update(found[0].id, params=portal)
            self.stdout.write(f"Portal configuration {found[0].id}: updated")
        else:
            conf = client.v1.billing_portal.configurations.create(params=portal)
            self.stdout.write(f"Created portal configuration {conf.id}")

        url = f"{site}/growth/stripe/webhook/"
        endpoints = [w for w in client.v1.webhook_endpoints.list(params={"limit": 100}).data if w.url == url]
        if endpoints:
            client.v1.webhook_endpoints.update(endpoints[0].id, params={"enabled_events": WEBHOOK_EVENTS,
                                                                        "description": "Sterr influencer packages"})
            self.stdout.write(f"Webhook {endpoints[0].id}: events updated ({', '.join(WEBHOOK_EVENTS)})")
            return
        endpoint = client.v1.webhook_endpoints.create(params={"url": url, "enabled_events": WEBHOOK_EVENTS,
                                                              "description": "Sterr influencer packages"})
        self._write_env(opts["env_file"], "STRIPE_WEBHOOK_SECRET", endpoint.secret)
        self.stdout.write(f"Created webhook {endpoint.id} → {url}; its secret is in {opts['env_file']} "
                          "(copy STRIPE_WEBHOOK_SECRET to Render → Environment)")

    def _write_env(self, path, name, value):
        env = Path(path)
        text = env.read_text(encoding="utf-8") if env.exists() else ""
        line = f"{name}={value}"
        text = re.sub(rf"^{name}=.*$", line, text, flags=re.M) if re.search(rf"^{name}=", text, re.M) else text.rstrip("\n") + f"\n{line}\n"
        env.write_text(text, encoding="utf-8")
