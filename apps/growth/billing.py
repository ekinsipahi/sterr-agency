"""Stripe calls for the growth subscription. Payments run only with GROWTH_PAYMENTS
on and STRIPE_SECRET_KEY + STRIPE_PRICE_ID set; otherwise the form just takes
requests and the team follows up by email."""
import json
import logging
from datetime import datetime, timezone

import stripe
from django.conf import settings

logger = logging.getLogger(__name__)

# Checkout UI languages Stripe supports; others fall back to the browser language.
STRIPE_LOCALES = {"en": "en", "tr": "tr", "de": "de", "nl": "nl", "fr": "fr", "it": "it", "es": "es", "pl": "pl",
                  "ru": "ru", "sv": "sv", "da": "da", "no": "nb", "ro": "ro"}


def enabled():
    return bool(settings.GROWTH_PAYMENTS and settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID)


def _client():
    return stripe.StripeClient(settings.STRIPE_SECRET_KEY)


def create_checkout(sub, success_url, cancel_url):
    session = _client().v1.checkout.sessions.create(params={
        "mode": "subscription",
        "line_items": [{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        "customer_email": sub.email,
        "client_reference_id": str(sub.pk),
        "success_url": success_url,
        "cancel_url": cancel_url,
        "locale": STRIPE_LOCALES.get(sub.lang, "auto"),
        "metadata": {"growth_id": str(sub.pk)},
        "subscription_data": {"metadata": {"growth_id": str(sub.pk), "instagram": sub.instagram,
                                           "location": sub.location[:200], "lang": sub.lang}},
    })
    return session


def retrieve_checkout(session_id):
    return _client().v1.checkout.sessions.retrieve(session_id)


def portal_url(customer_id, return_url, cancel_subscription=None):
    """Customer portal session. With `cancel_subscription` it opens straight on the
    cancellation screen; if Stripe refuses that (e.g. already set to cancel), the
    normal portal opens instead."""
    params = {"customer": customer_id, "return_url": return_url}
    if settings.STRIPE_PORTAL_CONFIG:
        params["configuration"] = settings.STRIPE_PORTAL_CONFIG
    if cancel_subscription:
        flow = {"type": "subscription_cancel", "subscription_cancel": {"subscription": cancel_subscription},
                "after_completion": {"type": "redirect", "redirect": {"return_url": return_url}}}
        try:
            return _client().v1.billing_portal.sessions.create(params={**params, "flow_data": flow}).url
        except stripe.InvalidRequestError:
            logger.info("Cancel flow refused for %s; opening the portal instead", cancel_subscription)
    return _client().v1.billing_portal.sessions.create(params=params).url


def parse_event(payload: bytes, signature: str):
    """Verify the Stripe-Signature header and return the event as a plain dict."""
    stripe.WebhookSignature.verify_header(payload.decode("utf-8"), signature, settings.STRIPE_WEBHOOK_SECRET,
                                          tolerance=300)
    return json.loads(payload)


def period_end(subscription: dict):
    """current_period_end lives on the subscription items in newer API versions."""
    ts = subscription.get("current_period_end")
    if not ts:
        items = (subscription.get("items") or {}).get("data") or []
        ts = items[0].get("current_period_end") if items else None
    return datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None


def invoice_subscription_id(invoice: dict):
    sub = invoice.get("subscription")
    if not sub:
        sub = (((invoice.get("parent") or {}).get("subscription_details") or {}).get("subscription"))
    return sub if isinstance(sub, str) else (sub or {}).get("id")
