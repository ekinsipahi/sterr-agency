import logging

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.languages import LANG_BY_CODE
from apps.leads.ga4 import hashed_user_data
from apps.leads.views import _client_ip

from . import billing
from .content import CONTENT, PAGES, alternates, lang_links, page_path
from .forms import GrowthForm
from .models import GrowthSubscription, StripeEvent
from .notifications import confirm_cancellation, notify_team, send_manage_link, welcome_customer

logger = logging.getLogger(__name__)

TEMPLATES = {"main": "growth/main.html", "geo": "growth/main.html", "pricing": "growth/pricing.html",
             "guide_buy": "growth/guide.html", "guide_speed": "growth/guide.html"}
RATE_LIMIT, RATE_WINDOW = 8, 60 * 60
MANAGE_SALT = "growth-manage"
MANAGE_MAX_AGE = 60 * 60
# Links inside our emails (cancel / manage). Signed, tied to one Stripe customer and
# subscription, no expiry: they must keep working for the life of the subscription.
ACCOUNT_SALT = "growth-account"


def account_link(sub, action):
    """Direct link to the Stripe portal for this subscription; action 'cancel' opens the cancel screen."""
    token = signing.dumps({"c": sub.stripe_customer_id, "s": sub.stripe_subscription_id, "l": sub.lang, "a": action},
                          salt=ACCOUNT_SALT, compress=True)
    return settings.SITE_URL + reverse("growth:account", args=[token])


def _valid_page(code, page):
    kind, _, geo = page.partition(":")
    return kind in PAGES or (kind == "geo" and geo in CONTENT[code].get("geo", {}))


def _context(code, page, form=None):
    g = CONTENT[code]
    ui = g["ui"]
    kind, _, geo = page.partition(":")
    if code == "tr":
        ctx = {"base_template": "base.html"}
    else:
        from apps.intl.views import _base_context  # the 15-language agency shell: nav, footer, consent
        ctx = _base_context(code, "home")
        ctx["base_template"] = "intl/base.html"
    if kind in ("main", "geo"):
        p = dict(g["main"])
        if kind == "geo":
            p.update(g["geo"][geo])
    else:
        p = g[kind]
    ctx.update({
        "code": code, "page": page, "kind": kind, "g": g, "gu": ui, "p": p,
        "faqs": p.get("faqs"),
        "form": form or GrowthForm(ui=ui, initial={"location": p.get("place", "")}),
        "current_lang": LANG_BY_CODE[code],
        "lang_links": lang_links(page),
        "alternates": alternates(page),
        "canonical_url": settings.SITE_URL + page_path(code, page),
        "key": f"growth_{kind}",
        "gurls": {k: page_path(code, k) for k in PAGES},
        "geo_links": [(v["place"], page_path(code, f"geo:{k}")) for k, v in g.get("geo", {}).items()],
        "price_usd": settings.GROWTH_PRICE_USD,
        "nav_cta_href": "#start",
        "nav_cta_label": ui["cta"],
        "canceled": False,
    })
    return ctx


def page(request, lang, page):
    ctx = _context(lang, page)
    ctx["canceled"] = request.GET.get("canceled") == "1"
    return render(request, TEMPLATES[ctx["kind"]], ctx)


@require_POST
def checkout(request):
    code = request.POST.get("lang")
    if code not in CONTENT:
        raise Http404
    page_key = request.POST.get("page", "main")
    if not _valid_page(code, page_key):
        page_key = "main"
    ui = CONTENT[code]["ui"]
    form = GrowthForm(request.POST, ui=ui)
    if form.is_spam():
        return redirect(f"{reverse('growth:success')}?lang={code}&pending=1")
    ip = _client_ip(request)
    rate_key = f"growth-rate:{ip}"
    if cache.get(rate_key, 0) >= RATE_LIMIT:
        form.add_error(None, ui["err_rate"])
    if form.errors or not form.is_valid():
        ctx = _context(code, page_key, form=form)
        return render(request, TEMPLATES[ctx["kind"]], ctx, status=400)
    cache.set(rate_key, cache.get(rate_key, 0) + 1, RATE_WINDOW)

    d = form.cleaned_data
    sub = GrowthSubscription.objects.create(
        email=d["email"].lower(), instagram=d["instagram"], location=d["location"], lang=code, ip=ip,
        source_page=request.POST.get("source_page", "")[:300],
        **{f: request.POST.get(f, "")[:150] for f in ("utm_source", "utm_medium", "utm_campaign", "gclid")},
    )
    if billing.enabled():
        success_url = f"{settings.SITE_URL}{reverse('growth:success')}?lang={code}&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.SITE_URL}{page_path(code, page_key)}?canceled=1#start"
        try:
            session = billing.create_checkout(sub, success_url, cancel_url)
        except Exception:
            logger.exception("Stripe checkout failed for growth #%s", sub.pk)
            form.add_error(None, ui["err_payment"])
            ctx = _context(code, page_key, form=form)
            return render(request, TEMPLATES[ctx["kind"]], ctx, status=502)
        sub.stripe_checkout_session_id = session.id
        sub.save(update_fields=["stripe_checkout_session_id"])
        response = redirect(session.url)
        response.status_code = 303
        return response

    # No Stripe yet: keep the request and let the team send the payment link.
    notify_team(sub, "request")
    return redirect(f"{reverse('growth:success')}?lang={code}&pending=1")


def success(request):
    code = request.GET.get("lang")
    code = code if code in CONTENT else "en"
    ctx = _context(code, "main")
    ctx["robots"] = "noindex, nofollow"
    handle, purchase = "", None
    session_id = request.GET.get("session_id", "")
    if session_id and billing.enabled():
        try:
            session = billing.retrieve_checkout(session_id)
        except Exception:
            logger.exception("Could not retrieve checkout session")
            session = None
        if session is not None and session.status == "complete":
            sub = GrowthSubscription.objects.filter(pk=session.client_reference_id).first()
            handle = sub.instagram if sub else ""
            seen = request.session.get("growth_purchases", [])
            if session_id not in seen:
                purchase = {
                    "transaction_id": session.id, "value": settings.GROWTH_PRICE_USD, "currency": "USD",
                    "items": [{"item_id": "organic_growth", "item_name": "Organic Instagram Growth",
                               "price": settings.GROWTH_PRICE_USD, "quantity": 1}],
                    "language": code,
                    "user_data": hashed_user_data(sub.email, "") if sub else {},
                }
                request.session["growth_purchases"] = (seen + [session_id])[-10:]
    ctx.update(handle=handle, pending=not handle, purchase_event=purchase,
               success_text=ctx["gu"]["success_text"].replace("{handle}", handle))
    return render(request, "growth/success.html", ctx)


def manage(request):
    code = request.GET.get("lang") or request.POST.get("lang")
    code = code if code in CONTENT else "en"
    ctx = _context(code, "main")
    ctx["robots"] = "noindex, nofollow"
    status = "expired" if request.GET.get("expired") else ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        ip_key = f"growth-manage:{_client_ip(request)}"
        if cache.get(ip_key, 0) < 5 and "@" in email:
            cache.set(ip_key, cache.get(ip_key, 0) + 1, RATE_WINDOW)
            sub = GrowthSubscription.objects.filter(email__iexact=email).exclude(stripe_customer_id="").first()
            if sub and billing.enabled():
                token = signing.dumps({"c": sub.stripe_customer_id, "l": code}, salt=MANAGE_SALT)
                send_manage_link(email, ctx["gu"], settings.SITE_URL + reverse("growth:portal", args=[token]))
        status = "sent"  # same answer whether or not the email exists
    ctx["manage_status"] = status
    return render(request, "growth/manage.html", ctx)


def portal(request, token):
    try:
        data = signing.loads(token, salt=MANAGE_SALT, max_age=MANAGE_MAX_AGE)
    except signing.BadSignature:
        return redirect(f"{reverse('growth:manage')}?expired=1")
    code = data.get("l") if data.get("l") in CONTENT else "en"
    if not billing.enabled():
        return redirect(f"{reverse('growth:manage')}?lang={code}&expired=1")
    return redirect(billing.portal_url(data["c"], settings.SITE_URL + page_path(code, "main")))


def account(request, token):
    try:
        data = signing.loads(token, salt=ACCOUNT_SALT)
    except signing.BadSignature:
        return redirect(f"{reverse('growth:manage')}?expired=1")
    code = data.get("l") if data.get("l") in CONTENT else "en"
    if not billing.enabled() or not data.get("c"):
        return redirect(f"{reverse('growth:manage')}?lang={code}&expired=1")
    cancel = data.get("s") if data.get("a") == "cancel" else None
    return redirect(billing.portal_url(data["c"], settings.SITE_URL + page_path(code, "main"), cancel_subscription=cancel))


# --- Stripe webhooks --------------------------------------------------------------

STATUS_MAP = {"active": "active", "trialing": "active", "past_due": "past_due", "unpaid": "past_due",
              "canceled": "canceled", "incomplete_expired": "canceled", "incomplete": "pending", "paused": "past_due"}


def _find(growth_id=None, subscription_id=None, customer_id=None):
    if growth_id and str(growth_id).isdigit():
        sub = GrowthSubscription.objects.filter(pk=int(growth_id)).first()
        if sub:
            return sub
    if subscription_id:
        sub = GrowthSubscription.objects.filter(stripe_subscription_id=subscription_id).first()
        if sub:
            return sub
    if customer_id:
        return GrowthSubscription.objects.filter(stripe_customer_id=customer_id).order_by("-created_at").first()
    return None


def _on_checkout_completed(obj):
    sub = _find(obj.get("client_reference_id") or (obj.get("metadata") or {}).get("growth_id"))
    if sub is None:
        logger.warning("Checkout %s without a matching growth subscription", obj.get("id"))
        return
    sub.stripe_customer_id = obj.get("customer") or sub.stripe_customer_id
    sub.stripe_subscription_id = obj.get("subscription") or sub.stripe_subscription_id
    if obj.get("payment_status") in ("paid", "no_payment_required"):
        sub.status = "active"
    sub.save()
    if not sub.welcomed:
        sub.welcomed = welcome_customer(sub, CONTENT.get(sub.lang, CONTENT["en"])["ui"], account_link(sub, "cancel"))
        sub.save(update_fields=["welcomed"])
        notify_team(sub, "started")


def _on_subscription_changed(obj):
    sub = _find((obj.get("metadata") or {}).get("growth_id"), obj.get("id"), obj.get("customer"))
    if sub is None:
        return
    was_canceling = sub.cancel_at_period_end
    sub.stripe_subscription_id = obj.get("id") or sub.stripe_subscription_id
    sub.stripe_customer_id = obj.get("customer") or sub.stripe_customer_id
    sub.status = STATUS_MAP.get(obj.get("status"), sub.status)
    sub.cancel_at_period_end = bool(obj.get("cancel_at_period_end") or obj.get("cancel_at"))
    sub.current_period_end = billing.period_end(obj) or sub.current_period_end
    sub.save()
    if sub.cancel_at_period_end and not was_canceling and sub.status != "canceled":
        notify_team(sub, "cancel_scheduled")
        confirm_cancellation(sub, CONTENT.get(sub.lang, CONTENT["en"])["ui"], account_link(sub, "portal"))


def _on_subscription_deleted(obj):
    sub = _find((obj.get("metadata") or {}).get("growth_id"), obj.get("id"), obj.get("customer"))
    if sub is None:
        return
    sub.status = "canceled"
    sub.save(update_fields=["status", "updated_at"])
    notify_team(sub, "canceled")


def _on_invoice(obj, paid):
    sub = _find(None, billing.invoice_subscription_id(obj), obj.get("customer"))
    if sub is None:
        return
    if paid:
        if sub.status in ("pending", "past_due"):
            sub.status = "active"
            sub.save(update_fields=["status", "updated_at"])
    else:
        sub.status = "past_due"
        sub.save(update_fields=["status", "updated_at"])
        notify_team(sub, "payment_failed")


HANDLERS = {
    "checkout.session.completed": _on_checkout_completed,
    "customer.subscription.created": _on_subscription_changed,
    "customer.subscription.updated": _on_subscription_changed,
    "customer.subscription.deleted": _on_subscription_deleted,
    "invoice.paid": lambda obj: _on_invoice(obj, paid=True),
    "invoice.payment_failed": lambda obj: _on_invoice(obj, paid=False),
}


@csrf_exempt
@require_POST
def webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse("webhook secret not configured", status=503)
    try:
        event = billing.parse_event(request.body, request.headers.get("Stripe-Signature", ""))
    except Exception:
        return HttpResponseBadRequest("invalid signature")
    handler = HANDLERS.get(event.get("type"))
    try:
        # Recording the event and handling it commit together: if handling fails,
        # Stripe's retry is processed again instead of being skipped as a duplicate.
        with transaction.atomic():
            StripeEvent.objects.create(event_id=event["id"], type=event["type"])
            if handler:
                handler(event["data"]["object"])
    except IntegrityError:
        return HttpResponse("duplicate")
    return HttpResponse("ok")
