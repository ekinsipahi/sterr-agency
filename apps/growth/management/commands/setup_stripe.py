"""Stripe setup for the one-time follower packages. Safe to run again.

- One product + one-time USD price per platform and package (10 in all), found again
  by lookup key `sterr_<platform>_<package>_usd`. A changed amount in packages.py gets
  a new price; the lookup key moves to it (transfer_lookup_key).
- The webhook endpoint: created, or its events updated. A new endpoint's signing
  secret is written to .env (STRIPE_WEBHOOK_SECRET), never printed.

    python manage.py setup_stripe
"""
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import stripe

from apps.growth.billing import lookup_key
from apps.growth.constants import PLATFORM_NAMES, PLATFORMS
from apps.growth.packages import PACKAGES, cents

WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "charge.refunded",
]


class Command(BaseCommand):
    help = "Create the package products/prices and the webhook for follower orders in Stripe."

    def add_arguments(self, parser):
        parser.add_argument("--site-url", default=settings.SITE_URL, help="Public origin for the webhook URL.")
        parser.add_argument("--env-file", default=str(Path(settings.BASE_DIR) / ".env"))

    def handle(self, *args, **opts):
        if not settings.STRIPE_SECRET_KEY:
            raise CommandError("STRIPE_SECRET_KEY is not set.")
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)

        for platform in PLATFORMS:
            for package in PACKAGES:
                key = lookup_key(platform, package["key"])
                existing = client.v1.prices.list(params={"lookup_keys": [key], "active": True, "limit": 1}).data
                if existing and existing[0].unit_amount == cents(package):
                    self.stdout.write(f"Price exists: {key} ({existing[0].id})")
                    continue
                low, high = package["days"]
                product = client.v1.products.create(params={
                    "name": f"{package['followers']:,} real {PLATFORM_NAMES[platform]} followers",
                    "description": f"One-time package. Real people, delivered gradually in {low}-{high} days. No bots, no password.",
                    "metadata": {"platform": platform, "package": package["key"]},
                })
                price = client.v1.prices.create(params={
                    "product": product.id, "currency": "usd", "unit_amount": cents(package),
                    "lookup_key": key, "transfer_lookup_key": True,
                    "metadata": {"platform": platform, "package": package["key"]},
                })
                self.stdout.write(f"Created {key}: ${package['price']} ({price.id})")

        url = f"{opts['site_url'].rstrip('/')}/growth/stripe/webhook/"
        endpoints = [w for w in client.v1.webhook_endpoints.list(params={"limit": 100}).data if w.url == url]
        if endpoints:
            client.v1.webhook_endpoints.update(endpoints[0].id, params={"enabled_events": WEBHOOK_EVENTS,
                                                                        "description": "Sterr follower packages"})
            self.stdout.write(f"Webhook {endpoints[0].id}: events updated ({', '.join(WEBHOOK_EVENTS)})")
            return
        endpoint = client.v1.webhook_endpoints.create(params={"url": url, "enabled_events": WEBHOOK_EVENTS,
                                                              "description": "Sterr follower packages"})
        self._write_env(opts["env_file"], "STRIPE_WEBHOOK_SECRET", endpoint.secret)
        self.stdout.write(f"Created webhook {endpoint.id} → {url}; its secret is in {opts['env_file']} "
                          "(copy STRIPE_WEBHOOK_SECRET to Render → Environment)")

    def _write_env(self, path, name, value):
        env = Path(path)
        text = env.read_text(encoding="utf-8") if env.exists() else ""
        line = f"{name}={value}"
        text = re.sub(rf"^{name}=.*$", line, text, flags=re.M) if re.search(rf"^{name}=", text, re.M) else text.rstrip("\n") + f"\n{line}\n"
        env.write_text(text, encoding="utf-8")
