"""Stripe Checkout for one-time follower packages. Payments run only with
GROWTH_PAYMENTS on and STRIPE_SECRET_KEY set; otherwise orders are taken as
requests and the team follows up by email."""
import json
import logging

import stripe
from django.conf import settings
from django.core.cache import cache

from .packages import PACKAGE_BY_KEY, cents

logger = logging.getLogger(__name__)

# Checkout UI languages Stripe supports; others fall back to the browser language.
STRIPE_LOCALES = {"en": "en", "tr": "tr", "de": "de", "nl": "nl", "fr": "fr", "it": "it", "es": "es", "pl": "pl",
                  "ru": "ru", "sv": "sv", "da": "da", "no": "nb", "ro": "ro"}


def enabled():
    return bool(settings.GROWTH_PAYMENTS and settings.STRIPE_SECRET_KEY)


def _client():
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


def lookup_key(platform, package_key):
    return f"sterr_{platform}_{package_key}_usd"


def price_id(platform, package_key):
    """The Stripe price created by `setup_stripe` for this package, if its amount still
    matches packages.py ("" otherwise). Cached for an hour."""
    key = lookup_key(platform, package_key)
    found = cache.get(f"stripe-price:{key}")
    if found is None:
        found = ""
        try:
            prices = _client().v1.prices.list(params={"lookup_keys": [key], "active": True, "limit": 1}).data
            if prices and prices[0].unit_amount == cents(PACKAGE_BY_KEY[package_key]):
                found = prices[0].id
        except stripe.StripeError:
            logger.exception("Stripe price lookup failed for %s", key)
        cache.set(f"stripe-price:{key}", found, 60 * 60)
    return found


def create_checkout(order, success_url, cancel_url):
    package = PACKAGE_BY_KEY[order.package]
    low, high = package["days"]
    name = f"{order.followers:,} real {order.platform_name} followers"
    description = f"For @{order.handle} ({order.location[:80]}). Delivered gradually in {low}-{high} days."
    metadata = {"order_id": str(order.pk), "platform": order.platform, "handle": order.handle, "package": order.package}
    price = price_id(order.platform, order.package)
    # The package's own Stripe price when it exists (reports per product), else an inline price.
    line = {"quantity": 1, "price": price} if price else {"quantity": 1, "price_data": {
        "currency": "usd", "unit_amount": cents(package), "product_data": {"name": name, "description": description}}}
    return _client().v1.checkout.sessions.create(params={
        "mode": "payment",
        "line_items": [line],
        "customer_email": order.email,
        "client_reference_id": str(order.pk),
        "success_url": success_url,
        "cancel_url": cancel_url,
        "locale": STRIPE_LOCALES.get(order.lang, "auto"),
        "metadata": metadata,
        "payment_intent_data": {"metadata": metadata, "description": f"{name} for @{order.handle} ({order.location[:80]})"},
    })


def retrieve_checkout(session_id):
    return _client().v1.checkout.sessions.retrieve(session_id)


def parse_event(payload: bytes, signature: str):
    """Verify the Stripe-Signature header and return the event as a plain dict."""
    stripe.WebhookSignature.verify_header(payload.decode("utf-8"), signature, settings.STRIPE_WEBHOOK_SECRET,
                                          tolerance=300)
    return json.loads(payload)
