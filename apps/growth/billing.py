"""Stripe for the monthly influencer packages: Checkout in subscription mode and the customer
portal (card, invoices, cancel). Payments run only with GROWTH_PAYMENTS on and
STRIPE_SECRET_KEY set; otherwise subscriptions are taken as requests and the team
follows up by email."""
import json
import logging
from datetime import datetime, timezone as dt_timezone

import stripe
from django.conf import settings
from django.core.cache import cache

from . import plan

logger = logging.getLogger(__name__)

# Checkout UI languages Stripe supports; others fall back to the browser language.
STRIPE_LOCALES = {"en": "en", "tr": "tr", "de": "de", "nl": "nl", "fr": "fr", "it": "it", "es": "es", "pl": "pl",
                  "ru": "ru", "sv": "sv", "da": "da", "no": "nb", "ro": "ro"}
PORTAL_TAG = "sterr-growth"  # metadata.app of the portal configuration setup_stripe creates


def metadata(obj):
    """An API object's metadata as a plain dict (StripeObject isn't a dict in stripe-python 15)."""
    meta = getattr(obj, "metadata", None)
    return meta.to_dict() if hasattr(meta, "to_dict") else dict(meta or {})


def enabled():
    return bool(settings.GROWTH_PAYMENTS and settings.STRIPE_SECRET_KEY)


def _client():
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


def lookup_key(platform, plan_key):
    return f"sterr_{platform}_{plan_key}_monthly_usd"


def price_id(platform, plan_key):
    """The monthly Stripe price created by `setup_stripe`, if its amount still matches
    plan.py ("" otherwise). Cached for an hour."""
    key = lookup_key(platform, plan_key)
    found = cache.get(f"stripe-price:{key}")
    if found is None:
        found = ""
        try:
            prices = _client().v1.prices.list(params={"lookup_keys": [key], "active": True, "limit": 1}).data
            if prices and prices[0].unit_amount == plan.cents(plan.PLAN_BY_KEY[plan_key]):
                found = prices[0].id
        except stripe.StripeError:
            logger.exception("Stripe price lookup failed for %s", key)
        cache.set(f"stripe-price:{key}", found, 60 * 60)
    return found


def create_checkout(sub, success_url, cancel_url, customer=""):
    package = plan.PLAN_BY_KEY[sub.plan]
    name = f"{sub.get_plan_display()} · {sub.platform_name} · Sterr Agency"
    metadata = {"subscription_id": str(sub.pk), "platform": sub.platform, "handle": sub.handle, "plan": sub.plan}
    price = price_id(sub.platform, sub.plan)
    # The platform's own Stripe price when it exists (reports per product), else an inline one.
    line = {"quantity": 1, "price": price} if price else {"quantity": 1, "price_data": {
        "currency": "usd", "unit_amount": plan.cents(package), "recurring": {"interval": "month"},
        "product_data": {"name": name}}}
    params = {
        "mode": "subscription",
        "line_items": [line],
        "client_reference_id": str(sub.pk),
        "success_url": success_url,
        "cancel_url": cancel_url,
        "locale": STRIPE_LOCALES.get(sub.lang, "auto"),
        "metadata": metadata,
        "subscription_data": {"metadata": metadata,
                              "description": f"{name} for @{sub.handle} ({sub.location[:80]})"},
    }
    if customer:
        params["customer"] = customer  # one Stripe customer per account: one portal for all packages
    else:
        params["customer_email"] = sub.email
    return _client().v1.checkout.sessions.create(params=params)


def retrieve_checkout(session_id):
    return _client().v1.checkout.sessions.retrieve(session_id)


def retrieve_subscription(subscription_id):
    """The Stripe subscription as a plain dict (the shape webhooks deliver). to_dict() keeps
    *_decimal fields as Decimal; webhooks send them as strings, so they become strings here too."""
    return json.loads(json.dumps(_client().v1.subscriptions.retrieve(subscription_id).to_dict(), default=str))


def portal_configuration():
    """Id of the portal configuration setup_stripe made ("" = the account default)."""
    found = cache.get("stripe-portal-config")
    if found is None:
        found = ""
        try:
            for conf in _client().v1.billing_portal.configurations.list(params={"active": True, "limit": 100}).data:
                if metadata(conf).get("app") == PORTAL_TAG:
                    found = conf.id
                    break
        except stripe.StripeError:
            logger.exception("Stripe portal configuration lookup failed")
        cache.set("stripe-portal-config", found, 60 * 60)
    return found


def portal_url(customer, return_url, lang="en"):
    params = {"customer": customer, "return_url": return_url, "locale": STRIPE_LOCALES.get(lang, "auto")}
    conf = portal_configuration()
    if conf:
        params["configuration"] = conf
    return _client().v1.billing_portal.sessions.create(params=params).url


def period_end(sub):
    """current_period_end of a subscription dict, as an aware datetime. Newer API versions
    keep it on the subscription items, older ones on the subscription."""
    ts = sub.get("current_period_end")
    if ts is None:
        items = (sub.get("items") or {}).get("data") or []
        ts = items[0].get("current_period_end") if items else None
    return datetime.fromtimestamp(ts, tz=dt_timezone.utc) if ts else None


def invoice_subscription(invoice):
    """The subscription id of an invoice dict, in old and new API shapes."""
    sub = invoice.get("subscription")
    if not sub:
        sub = (((invoice.get("parent") or {}).get("subscription_details") or {}).get("subscription"))
    return sub if isinstance(sub, str) else (sub or {}).get("id", "")


def parse_event(payload: bytes, signature: str):
    """Verify the Stripe-Signature header and return the event as a plain dict."""
    stripe.WebhookSignature.verify_header(payload.decode("utf-8"), signature, settings.STRIPE_WEBHOOK_SECRET,
                                          tolerance=300)
    return json.loads(payload)
