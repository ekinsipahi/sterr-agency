import logging
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.core import signing
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.languages import LANG_BY_CODE
from apps.leads.ga4 import hashed_user_data
from apps.leads.views import _client_ip

from . import billing
from .content import ACCOUNT_NAV, CONTENT, CREATOR_PAGES, CREATORS, GUIDES, UI, PAGES, PLATFORM_NAMES, PLATFORMS, alternates, creator_alternates, creator_path, lang_links, page_path, ui_for
from .forms import OrderForm
from .models import Customer, FollowerOrder, StripeEvent
from .notifications import acknowledge_request, confirm_payment, notify_team, send_verification
from .packages import DEFAULT_PACKAGE, PACKAGE_BY_KEY, count, for_page

logger = logging.getLogger(__name__)

RATE_LIMIT, RATE_WINDOW = 8, 60 * 60
VERIFY_SALT = "growth-verify"
VERIFY_MAX_AGE = 7 * 24 * 60 * 60


def shell(code):
    """The site chrome for a language: Turkish root site or the 15-language agency shell."""
    if code == "tr":
        ctx = {"base_template": "base.html"}
    else:
        from apps.intl.views import _base_context  # nav, footer, consent

        ctx = _base_context(code, "home")
        ctx["base_template"] = "intl/base.html"
    ctx.update(code=code, current_lang=LANG_BY_CODE[code])
    return ctx


def verify_link(user, order=None):
    token = signing.dumps({"u": user.pk, "e": user.email, "o": order.pk if order else None}, salt=VERIFY_SALT)
    return settings.SITE_URL + reverse("growth:verify", args=[token])


def _valid_page(code, page, platform):
    kind, _, geo = page.partition(":")
    return kind in PAGES or (kind == "geo" and geo in CONTENT[platform][code].get("geo", {}))


def _platform(value):
    return value if value in PLATFORMS else "instagram"


def _context(request, code, page, platform="instagram", form=None):
    data = CONTENT[platform][code]
    gu = ui_for(code, platform)
    kind, _, geo = page.partition(":")
    p = dict(data["main"])
    if kind == "geo":
        p.update(data["geo"][geo])
    elif kind != "main":
        p = data[kind]
    pack = kind[5:] if kind.startswith("pack_") else None
    selected = (form.data.get("package") if form is not None and form.is_bound else None) or pack or DEFAULT_PACKAGE
    other = [q for q in PLATFORMS if q != platform and code in CONTENT[q]]
    ctx = shell(code)
    ctx.update({
        "page": page, "kind": kind, "g": data, "gu": gu, "p": p,
        "platform": platform, "platform_name": PLATFORM_NAMES[platform], "followers_active": True,
        "faqs": p.get("faqs"),
        "packages": [{**pk, "delivery": gu["delivery"].replace("{min}", str(pk["days"][0])).replace("{max}", str(pk["days"][1]))}
                     for pk in for_page(code)],
        "selected_package": selected if selected in PACKAGE_BY_KEY else DEFAULT_PACKAGE,
        "page_package": next((pk for pk in for_page(code) if pk["key"] == pack), None),
        "form": form or OrderForm(ui=gu, user=request.user, initial={"location": p.get("place", "")}),
        "lang_links": lang_links(page, platform),
        "alternates": alternates(page, platform),
        "canonical_url": settings.SITE_URL + page_path(code, page, platform),
        "hub": [{"key": k, "url": page_path(code, k, platform), "p": data[k]} for k in PAGES if k != kind],
        "other_platform": [{"name": PLATFORM_NAMES[q], "url": page_path(code, "main", q), "p": CONTENT[q][code]["main"],
                            "label": ui_for(code, q)["other_platform"]} for q in other],
        "creators_link": {"url": creator_path(code, "main"), "p": CREATORS[code]["main"], "label": CREATORS[code]["nav"]} if code in CREATORS else None,
        "blocks": [(gu["engagement_title"], gu["engagement_text"]), (gu["instant_title"], gu["instant_text"]),
                   (gu["bots_title"], gu["bots_text"])],
        "signed_in": gu["signed_in_as"].replace("{email}", request.user.email) if request.user.is_authenticated else "",
        "account_nav": ACCOUNT_NAV.get(code, ACCOUNT_NAV["en"]),
        "geo_links": [(v["place"], page_path(code, f"geo:{k}", platform)) for k, v in data.get("geo", {}).items()],
        "is_guide": kind in GUIDES,
        "payments": billing.enabled(),
        "nav_cta_href": "#start",
        "nav_cta_label": gu["nav_cta"],
        "account_url": f"{reverse('growth:account')}?lang={code}",
        "google": google_enabled(),
        "canceled": request.GET.get("canceled") == "1",
    })
    return ctx


def page(request, lang, page, platform="instagram"):
    return render(request, "growth/page.html", _context(request, lang, page, platform))


def creators(request, lang, page):
    """The 'influencer agency for creators' hub and its guides."""
    data = CREATORS[lang]
    p = data[page]
    gu = ui_for(lang, "instagram")
    ctx = shell(lang)
    ctx.update({
        "page": page, "kind": page, "p": p, "g": data, "gu": gu, "faqs": p.get("faqs"), "is_guide": page != "main",
        "followers_active": True,
        "lang_links": [(lang_obj, creator_path(lang_obj.code, page)) for lang_obj in LANG_BY_CODE.values() if lang_obj.code in CREATORS],
        "alternates": creator_alternates(page),
        "canonical_url": settings.SITE_URL + creator_path(lang, page),
        "platform_links": [{"name": PLATFORM_NAMES[q], "label": ui_for(lang, q)["see_packages"], "url": page_path(lang, "main", q),
                            "agency_url": page_path(lang, "agency", q), "agency": CONTENT[q][lang]["agency"]}
                           for q in PLATFORMS if lang in CONTENT[q]],
        "hub": [{"url": creator_path(lang, k), "p": data[k]} for k in CREATOR_PAGES if k != page],
        "blocks": [(gu["bots_title"], UI[lang]["bots_text"].replace("{platform}", "Instagram / TikTok"))],
        "nav_cta_href": page_path(lang, "main", "instagram") + "#start" if lang in CONTENT["instagram"] else "#",
        "nav_cta_label": gu["nav_cta"],
    })
    return render(request, "growth/creators.html", ctx)


def start_checkout(order, cancel_path):
    """Create the Stripe Checkout session for a pending order and return its URL."""
    query = f"?lang={order.lang}&platform={order.platform}&order={order.pk}"
    success_url = f"{settings.SITE_URL}{reverse('growth:success')}{query}&session_id={{CHECKOUT_SESSION_ID}}"
    session = billing.create_checkout(order, success_url, settings.SITE_URL + cancel_path)
    order.stripe_checkout_session_id = session.id
    order.save(update_fields=["stripe_checkout_session_id", "updated_at"])
    return session.url


def see_other(url):
    response = redirect(url)
    response.status_code = 303
    return response


ORDER_FIELDS = ("package", "handle", "location")
SOURCE_FIELDS = ("source_page", "utm_source", "utm_medium", "utm_campaign", "gclid")


@require_POST
def order(request):
    platform = _platform(request.POST.get("platform"))
    code = request.POST.get("lang")
    if code not in CONTENT[platform]:
        raise Http404
    page_key = request.POST.get("page", "main")
    if not _valid_page(code, page_key, platform):
        page_key = "main"
    gu = ui_for(code, platform)
    # "Continue with Google": the order details are checked now, the account comes from Google.
    via_google = request.POST.get("via") == "google" and not request.user.is_authenticated and google_enabled()
    form = OrderForm(request.POST, ui=gu, user=request.user, account_fields=not via_google)
    if form.is_spam():
        return redirect(f"{reverse('growth:success')}?lang={code}&platform={platform}")
    ip = _client_ip(request)
    rate_key = f"growth-rate:{ip}"
    if cache.get(rate_key, 0) >= RATE_LIMIT:
        form.add_error(None, gu["err_rate"])

    user, signed_up = request.user, False
    if not form.errors and form.is_valid() and not user.is_authenticated and not via_google:
        email, password = form.cleaned_data["email"], form.cleaned_data["password"]
        User = get_user_model()
        if User.objects.filter(username=email).exists():
            user = authenticate(request, username=email, password=password)
            if user is None:
                form.add_error("password", gu["err_login"])
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            Customer.objects.create(user=user, lang=code)
            signed_up = True
    if form.errors or not form.is_valid():
        return render(request, "growth/page.html", _context(request, code, page_key, platform, form=form), status=400)
    cache.set(rate_key, cache.get(rate_key, 0) + 1, RATE_WINDOW)

    pending = {"platform": platform, "lang": code, "page": page_key, "ip": ip,
               **{f: form.cleaned_data[f] for f in ORDER_FIELDS},
               **{f: request.POST.get(f, "")[:300 if f == "source_page" else 150] for f in SOURCE_FIELDS}}
    if via_google:
        request.session["google_order"] = pending
        back = f"{page_path(code, page_key, platform)}#start"
        return redirect(f"{reverse('growth:google')}?lang={code}&order=1&next={quote(back)}")
    if not request.user.is_authenticated:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if signed_up:
        request.session["growth_signup"] = {"method": "email", "language": code}
    response = place_order(request, user, pending)
    if response is None:  # Stripe failed: show the form again with the error
        form.add_error(None, gu["err_payment"])
        return render(request, "growth/page.html", _context(request, code, page_key, platform, form=form), status=502)
    return response


def place_order(request, user, pending):
    """Create the order for a signed-in user and send it on: Stripe Checkout, the email
    confirmation step, or (payments off) a request. None when Stripe can't be reached."""
    code, platform = pending["lang"], pending["platform"]
    customer, _ = Customer.objects.get_or_create(user=user, defaults={"lang": code})
    package = PACKAGE_BY_KEY[pending["package"]]
    order = FollowerOrder.objects.create(
        user=user, email=user.email, platform=platform, handle=pending["handle"], location=pending["location"],
        package=package["key"], followers=package["followers"], amount=package["price"], lang=code, ip=pending.get("ip"),
        **{f: pending.get(f, "") for f in SOURCE_FIELDS},
    )
    if billing.enabled():
        if settings.GROWTH_VERIFY_EMAIL and not customer.email_verified:
            # A confirmed email before the first payment keeps card-testing scripts out.
            send_verification(user.email, verify_link(user, order), order)
            return redirect(f"{reverse('growth:account')}?lang={code}&verify=sent")
        try:
            return see_other(start_checkout(order, f"{page_path(code, pending['page'], platform)}?canceled=1#start"))
        except Exception:
            logger.exception("Stripe checkout failed for order #%s", order.pk)
            return None

    # Payments off: a request. Team email via Resend, English auto-reply to the customer.
    order.status = "requested"
    team = notify_team(order, "request")
    customer_mail = acknowledge_request(order)
    order.notified = bool(team)
    order.mail_error = "\n".join(f"{who}: {r.error}" for who, r in (("Ekip", team), ("Müşteri", customer_mail)) if not r)
    order.save(update_fields=["status", "notified", "mail_error", "updated_at"])
    request.session["growth_lead"] = {
        "lead_id": f"{platform[:2]}-{order.pk}", "form_id": f"{platform}_followers", "language": code,
        "value": float(order.amount), "currency": "USD", "package": order.package, "lead_location": order.location[:40],
        "user_data": hashed_user_data(order.email, ""),
    }
    return redirect(f"{reverse('growth:success')}?lang={code}&platform={platform}&order={order.pk}")


def google_enabled():
    return bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)


def mark_paid(order_id, payment_intent=""):
    """Pending/requested -> paid, once; sends the receipt and the team note on that transition."""
    with transaction.atomic():
        order = FollowerOrder.objects.select_for_update().filter(pk=order_id).first()
        if order is None or order.status not in ("pending", "requested"):
            return order
        order.status, order.paid_at = "paid", timezone.now()
        order.stripe_payment_intent_id = payment_intent or order.stripe_payment_intent_id
        order.save()
    if order.user_id:
        Customer.objects.filter(user_id=order.user_id).update(email_verified=True)  # paid through the emailed link
    team, receipt = notify_team(order, "paid"), confirm_payment(order)
    order.notified = bool(team)
    order.mail_error = "\n".join(f"{who}: {r.error}" for who, r in (("Ekip", team), ("Müşteri", receipt)) if not r)
    order.save(update_fields=["notified", "mail_error", "updated_at"])
    return order


def success(request):
    platform = _platform(request.GET.get("platform"))
    code = request.GET.get("lang")
    code = code if code in CONTENT[platform] else "en"
    ctx = _context(request, code, "main", platform)
    ctx["robots"] = "noindex, nofollow"
    order, purchase = None, None
    order_id = request.GET.get("order", "")
    session_id = request.GET.get("session_id", "")
    if order_id.isdigit() and request.user.is_authenticated:
        order = FollowerOrder.objects.filter(pk=int(order_id), user=request.user).first()
    if order is not None and session_id and billing.enabled() and session_id == order.stripe_checkout_session_id:
        try:
            session = billing.retrieve_checkout(session_id)
        except Exception:
            logger.exception("Could not retrieve checkout session")
            session = None
        if session is not None and session.status == "complete" and session.payment_status == "paid":
            order = mark_paid(order.pk, session.payment_intent or "")
            seen = request.session.get("growth_purchases", [])
            if session_id not in seen:
                purchase = {
                    "transaction_id": session.id, "value": float(order.amount), "currency": "USD", "language": code,
                    "items": [{"item_id": f"{platform}_{order.package}", "item_name": f"{order.followers} {PLATFORM_NAMES[platform]} followers",
                               "price": float(order.amount), "quantity": 1}],
                    "user_data": hashed_user_data(order.email, ""),
                }
                request.session["growth_purchases"] = (seen + [session_id])[-10:]
    paid = order is not None and order.status in ("paid", "completed")
    text = ""
    if order is not None:
        low, high = order.days
        text = (ctx["gu"]["success_text"] if paid else ctx["gu"]["pending_text"])
        text = text.replace("{followers}", count(order.followers, code))
        text = text.replace("{handle}", order.handle).replace("{min}", str(low)).replace("{max}", str(high))
    ctx.update(order=order, paid=paid, success_text=text, purchase_event=purchase,
               lead_event=request.session.pop("growth_lead", None), signup_event=request.session.pop("growth_signup", None))
    return render(request, "growth/success.html", ctx)


# --- Stripe webhooks --------------------------------------------------------------

def _order_id(obj):
    ref = obj.get("client_reference_id") or (obj.get("metadata") or {}).get("order_id")
    return int(ref) if ref and str(ref).isdigit() else None


def _on_checkout_paid(obj):
    if obj.get("mode") != "payment" or obj.get("payment_status") != "paid":
        return
    order_id = _order_id(obj)
    if order_id is None:
        logger.warning("Checkout %s without an order id", obj.get("id"))
        return
    mark_paid(order_id, obj.get("payment_intent") or "")


def _on_refund(obj):
    intent = obj.get("payment_intent")
    order = FollowerOrder.objects.filter(stripe_payment_intent_id=intent).first() if intent else None
    if order is None and (obj.get("metadata") or {}).get("order_id", "").isdigit():
        order = FollowerOrder.objects.filter(pk=int(obj["metadata"]["order_id"])).first()
    if order is None or order.status == "refunded":
        return
    order.status = "refunded"
    order.save(update_fields=["status", "updated_at"])
    notify_team(order, "refunded")


HANDLERS = {
    "checkout.session.completed": _on_checkout_paid,
    "checkout.session.async_payment_succeeded": _on_checkout_paid,
    "charge.refunded": _on_refund,
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
