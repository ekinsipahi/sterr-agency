import logging
from datetime import datetime, timezone as dt_timezone
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
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.languages import LANG_BY_CODE
from apps.leads.ga4 import hashed_user_data
from apps.leads.views import _client_ip

from . import billing, evidence, linksterr
from .content import has_page, ACCOUNT_NAV, CONTENT, CREATOR_PAGES, CREATORS, GROUPS, GUIDES, PAGE_PLAN, UI, PAGES, PLATFORM_NAMES, PLATFORMS, alternates, creator_alternates, creator_path, lang_links, page_path, ui_for
from .constants import TERMS_VERSION
from .forms import OrderForm
from . import plan
from .models import AgencySubscription, Customer, Dispute, StripeEvent
from .notifications import (acknowledge_request, confirm_cancel, confirm_payment, notify_team, payment_notice,
                            remind_renewal, send_verification)

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


def verify_link(user, sub=None):
    token = signing.dumps({"u": user.pk, "e": user.email, "s": sub.pk if sub else None}, salt=VERIFY_SALT)
    return settings.SITE_URL + reverse("growth:verify", args=[token])


def _valid_page(code, page, platform):
    return has_page(code, page, platform)


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
    other = [q for q in PLATFORMS if q != platform and code in CONTENT[q]]
    selected = (form.data.get("plan") if form is not None and form.is_bound else None) or request.GET.get("plan") or PAGE_PLAN.get(kind)
    ctx = shell(code)
    ctx.update({
        "page": page, "kind": kind, "g": data, "gu": gu, "p": p,
        "platform": platform, "platform_name": PLATFORM_NAMES[platform], "followers_active": True,
        "faqs": p.get("faqs"),
        "plans": plan.for_page(code, gu),
        "selected_plan": selected if selected in plan.PLAN_BY_KEY else plan.DEFAULT_PLAN,
        "lowest_price": plan.money(plan.LOWEST),
        "form": form or OrderForm(ui=gu, user=request.user, initial={"location": p.get("place", "")}),
        "lang_links": lang_links(page, platform),
        "alternates": alternates(page, platform),
        "canonical_url": settings.SITE_URL + page_path(code, page, platform),
        "hub": [{"key": k, "url": page_path(code, k, platform), "p": data[k]} for k in ("main",) + GROUPS["followers"][:2] if k != kind],
        "hub_groups": [(gu["groups"][g], items) for g, keys in GROUPS.items() if "groups" in gu and (items := [
            {"url": page_path(code, k, platform), "p": data[k], "here": k == kind} for k in keys if has_page(code, k, platform)])],
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


def start_checkout(sub, cancel_path):
    """Create the Stripe Checkout session for a pending subscription and return its URL."""
    query = f"?lang={sub.lang}&platform={sub.platform}&sub={sub.pk}"
    success_url = f"{settings.SITE_URL}{reverse('growth:success')}{query}&session_id={{CHECKOUT_SESSION_ID}}"
    customer = (AgencySubscription.objects.filter(user_id=sub.user_id).exclude(stripe_customer_id="")
                .values_list("stripe_customer_id", flat=True).first()) if sub.user_id else ""
    session = billing.create_checkout(sub, success_url, settings.SITE_URL + cancel_path, customer=customer or "",
                                      note=ui_for(sub.lang, sub.platform)["policy"])
    sub.stripe_checkout_session_id = session.id
    sub.save(update_fields=["stripe_checkout_session_id", "updated_at"])
    return session.url


def see_other(url):
    response = redirect(url)
    response.status_code = 303
    return response


ORDER_FIELDS = ("plan", "handle", "location", "phone")
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
               "terms_at": timezone.now().isoformat(), "terms_version": TERMS_VERSION, "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
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
    """Create the subscription for a signed-in user and send it on: Stripe Checkout, the
    email confirmation step, or (payments off) a request. None when Stripe can't be reached."""
    code, platform = pending["lang"], pending["platform"]
    customer, _ = Customer.objects.get_or_create(user=user, defaults={"lang": code})
    package = plan.PLAN_BY_KEY[pending["plan"]]
    fields = {"email": user.email, "location": pending["location"], "phone": pending.get("phone", ""), "plan": package["key"], "amount": package["price"], "lang": code,
              "ip": pending.get("ip"), **{f: pending.get(f, "") for f in SOURCE_FIELDS},
              # The terms box is required on the order form: when, which version, from which browser.
              "terms_accepted_at": parse_datetime(pending.get("terms_at") or "") or timezone.now(),
              "terms_version": pending.get("terms_version", ""), "user_agent": pending.get("user_agent", "")}
    # Trying again for the same account (e.g. after a canceled checkout) reuses the unpaid one.
    sub = AgencySubscription.objects.filter(user=user, platform=platform, handle=pending["handle"], status="pending").first()
    if sub is None:
        sub = AgencySubscription.objects.create(user=user, platform=platform, handle=pending["handle"], **fields)
    else:
        for name, value in fields.items():
            setattr(sub, name, value)
        sub.save()
    if billing.enabled():
        if settings.GROWTH_VERIFY_EMAIL and not customer.email_verified:
            # A confirmed email before the first payment keeps card-testing scripts out.
            send_verification(user.email, verify_link(user, sub), sub)
            return redirect(f"{reverse('growth:account')}?lang={code}&verify=sent")
        try:
            return see_other(start_checkout(sub, f"{page_path(code, pending['page'], platform)}?canceled=1#start"))
        except Exception:
            logger.exception("Stripe checkout failed for subscription #%s", sub.pk)
            return None

    # Payments off: a request. Team email via Resend, English auto-reply to the customer.
    sub.status = "requested"
    team = notify_team(sub, "request")
    customer_mail = acknowledge_request(sub)
    sub.notified = bool(team)
    sub.mail_error = "\n".join(f"{who}: {r.error}" for who, r in (("Ekip", team), ("Müşteri", customer_mail)) if not r)
    sub.save(update_fields=["status", "notified", "mail_error", "updated_at"])
    request.session["growth_lead"] = {
        "lead_id": f"{platform[:2]}-{sub.pk}", "form_id": f"{platform}_followers", "language": code,
        "value": float(sub.amount), "currency": "USD", "package": sub.plan, "lead_location": sub.location[:40],
        "user_data": hashed_user_data(sub.email, ""),
    }
    return redirect(f"{reverse('growth:success')}?lang={code}&platform={platform}&sub={sub.pk}")


def google_enabled():
    return bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)


STRIPE_STATUS = {"active": "active", "trialing": "active", "past_due": "past_due", "unpaid": "past_due",
                 "canceled": "canceled", "incomplete_expired": "canceled"}


def sync(stripe_sub, sub_id=None, source="stripe"):
    """Bring our subscription in line with Stripe's. The first time it turns active the
    team note and the customer's welcome go out; a cancel at the period end (from our
    account page or Stripe's portal: `source`) and taking it back are
    told to the team, and a cancel is confirmed to the customer. A failed payment (the campaign
    pauses) and its recovery are told to both. Any change asks Linksterr to bring the campaign
    in line right away. Returns the subscription (or None)."""
    first_payment, change, payment = False, None, None
    with transaction.atomic():
        qs = AgencySubscription.objects.select_for_update()
        # sub_id comes only from a Checkout session we created; otherwise the Stripe id must
        # already be ours (events of the other sites on this Stripe account are skipped).
        sub = qs.filter(stripe_subscription_id=stripe_sub["id"]).first() or (qs.filter(pk=sub_id).first() if sub_id else None)
        if sub is None:
            return None
        status = STRIPE_STATUS.get(stripe_sub.get("status"))
        was_canceling, was_status, was_end = sub.cancel_at_period_end, sub.status, sub.current_period_end
        sub.stripe_subscription_id = stripe_sub["id"]
        sub.stripe_customer_id = stripe_sub.get("customer") or sub.stripe_customer_id
        sub.current_period_end = billing.period_end(stripe_sub) or sub.current_period_end
        sub.cancel_at_period_end = bool(stripe_sub.get("cancel_at_period_end"))
        if status:
            if status == "active" and sub.started_at is None:
                sub.started_at, first_payment = timezone.now(), True
            if status == "canceled" and sub.status != "canceled":
                sub.canceled_at = timezone.now()
            sub.status = status
        if sub.status != "canceled" and sub.cancel_at_period_end != was_canceling:
            change = "cancel_requested" if sub.cancel_at_period_end else "resumed"
            sub.cancel_requested_at = timezone.now() if sub.cancel_at_period_end else None
            sub.cancel_source = source if sub.cancel_at_period_end else ""
        if was_status == "active" and sub.status == "past_due":
            payment = "payment_failed"
        elif was_status == "past_due" and sub.status == "active":
            payment = "payment_recovered"
        sub.save()
        if first_payment or change or sub.status != was_status or sub.current_period_end != was_end:
            transaction.on_commit(linksterr.ping_soon)  # Linksterr opens, renews, pauses or ends the campaign now
    if first_payment:
        if sub.user_id:
            Customer.objects.filter(user_id=sub.user_id).update(email_verified=True)  # paid through the emailed link
        team, receipt = notify_team(sub, "paid"), confirm_payment(sub)
        sub.notified = bool(team)
        sub.mail_error = "\n".join(f"{who}: {r.error}" for who, r in (("Ekip", team), ("Müşteri", receipt)) if not r)
        sub.save(update_fields=["notified", "mail_error", "updated_at"])
    if change:
        notify_team(sub, change)
        if change == "cancel_requested":
            confirm_cancel(sub)
    if payment:
        notify_team(sub, payment)
        payment_notice(sub, payment)
    return sub


def send_reminder(sub):
    """The renewal reminder, once per billing period."""
    if sub.status != "active" or sub.cancel_at_period_end or not sub.current_period_end or sub.reminded_for == sub.current_period_end:
        return False
    if not remind_renewal(sub):
        return False
    AgencySubscription.objects.filter(pk=sub.pk).update(reminded_for=sub.current_period_end)
    return True


def success(request):
    platform = _platform(request.GET.get("platform"))
    code = request.GET.get("lang")
    code = code if code in CONTENT[platform] else "en"
    ctx = _context(request, code, "main", platform)
    ctx["robots"] = "noindex, nofollow"
    sub, purchase = None, None
    sub_id = request.GET.get("sub", "")
    session_id = request.GET.get("session_id", "")
    if sub_id.isdigit() and request.user.is_authenticated:
        sub = AgencySubscription.objects.filter(pk=int(sub_id), user=request.user).first()
    if sub is not None and session_id and billing.enabled() and session_id == sub.stripe_checkout_session_id:
        try:
            session = billing.retrieve_checkout(session_id)
            if session.status == "complete" and session.payment_status == "paid" and session.subscription:
                sub = sync(billing.retrieve_subscription(session.subscription), sub.pk) or sub
        except Exception:
            logger.exception("Could not confirm checkout session")
        seen = request.session.get("growth_purchases", [])
        if sub.status == "active" and session_id not in seen:
            purchase = {
                "transaction_id": session_id, "value": float(sub.amount), "currency": "USD", "language": code,
                "items": [{"item_id": f"{platform}_{sub.plan}", "item_name": f"{PLATFORM_NAMES[platform]} {sub.get_plan_display()}",
                           "price": float(sub.amount), "quantity": 1}],
                "user_data": hashed_user_data(sub.email, ""),
            }
            request.session["growth_purchases"] = (seen + [session_id])[-10:]
    paid = sub is not None and sub.status == "active"
    text = ""
    if sub is not None:
        text = (ctx["gu"]["success_text"] if paid else ctx["gu"]["pending_text"]).replace("{handle}", sub.handle).replace(
            "{package}", ctx["gu"][f"plan_{sub.plan}"])
    ctx.update(sub=sub, paid=paid, success_text=text, purchase_event=purchase,
               lead_event=request.session.pop("growth_lead", None), signup_event=request.session.pop("growth_signup", None))
    return render(request, "growth/success.html", ctx)


# --- Stripe webhooks --------------------------------------------------------------

def _on_checkout(obj):
    # Other sites share this Stripe account and their events arrive here too: only a
    # Checkout session we created is ours.
    sub = AgencySubscription.objects.filter(stripe_checkout_session_id=obj.get("id") or "-").first()
    if sub is None or obj.get("mode") != "subscription" or obj.get("payment_status") != "paid" or not obj.get("subscription"):
        return
    sync(billing.retrieve_subscription(obj["subscription"]), sub.pk)


def _on_invoice_paid(obj):
    """Every paid invoice moves the period on; a monthly renewal also tells the team."""
    stripe_id = billing.invoice_subscription(obj)
    if not stripe_id:
        return
    was_active = AgencySubscription.objects.filter(stripe_subscription_id=stripe_id, status="active").exists()
    sub = sync(billing.retrieve_subscription(stripe_id))
    if sub is not None and was_active and obj.get("billing_reason") == "subscription_cycle":
        notify_team(sub, "renewed", amount=obj.get("amount_paid"))


def _on_invoice_failed(obj):
    stripe_id = billing.invoice_subscription(obj)
    if stripe_id:
        sync(billing.retrieve_subscription(stripe_id))  # Stripe has it as past_due now


def _on_invoice_upcoming(obj):
    """Stripe's renewal notice (Settings → Billing → Subscriptions: upcoming renewal events, 3 days)."""
    stripe_id = billing.invoice_subscription(obj)
    sub = AgencySubscription.objects.filter(stripe_subscription_id=stripe_id).first() if stripe_id else None
    if sub is not None:
        send_reminder(sub)


def _on_subscription(obj):
    before = AgencySubscription.objects.filter(stripe_subscription_id=obj.get("id")).values_list("status", flat=True).first()
    sub = sync(obj)
    if sub is not None and before and before != "canceled" and sub.status == "canceled":
        notify_team(sub, "canceled")


DISPUTE_RESULTS = {"won": "KAZANILDI (para geri geldi)", "lost": "KAYBEDİLDİ", "warning_closed": "uyarı kapandı",
                   "charge_refunded": "ödeme iade edildi"}


def _dispute_sub(obj):
    """Our subscription behind a dispute, or None (a dispute of another site on this Stripe account)."""
    known = Dispute.objects.filter(dispute_id=obj.get("id")).select_related("subscription").first()
    if known is not None:
        return known.subscription
    stripe_sub, customer = billing.dispute_subscription(obj)
    qs = AgencySubscription.objects.exclude(started_at=None)
    return ((qs.filter(stripe_subscription_id=stripe_sub).first() if stripe_sub else None)
            or (qs.filter(stripe_customer_id=customer).order_by("-started_at").first() if customer else None))


def _on_dispute(obj):
    sub = _dispute_sub(obj)
    if sub is None:
        return
    due = (obj.get("evidence_details") or {}).get("due_by")
    dispute, opened = Dispute.objects.update_or_create(dispute_id=obj["id"], defaults={
        "subscription": sub, "amount": (obj.get("amount") or 0) / 100, "reason": obj.get("reason") or "",
        "status": obj.get("status") or "", "due_by": datetime.fromtimestamp(due, tz=dt_timezone.utc) if due else None})
    stripe_link = f"https://dashboard.stripe.com/disputes/{dispute.dispute_id}"
    admin_link = f"{settings.SITE_URL}{reverse('admin:growth_agencysubscription_evidence', args=[sub.pk])}"
    if opened:
        linksterr.sync([sub], force=True)  # the latest delivery numbers go into the evidence
        try:
            billing.stage_evidence(dispute.dispute_id, evidence.build(sub))
            dispute.evidence_staged = True
        except Exception as exc:
            logger.exception("Could not stage evidence for %s", dispute.dispute_id)
            dispute.error = str(exc)[:500]
        dispute.save(update_fields=["evidence_staged", "error", "updated_at"])
        staged = ("Kanıtlar Stripe'a TASLAK olarak yüklendi (gönderilmedi). Kontrol et, varsa ekran görüntüsü ekle ve "
                  "Submit'e bas." if dispute.evidence_staged else f"Kanıt Stripe'a yüklenemedi: {dispute.error}")
        due_text = f"{dispute.due_by:%d.%m.%Y %H:%M} UTC" if dispute.due_by else "-"
        notify_team(sub, "dispute", amount=obj.get("amount"), extra=(
            f"Sebep: {dispute.reason or '-'}\nSon kanıt tarihi: {due_text}\n{staged}\n"
            f"Stripe: {stripe_link}\nKanıt paketi (yazdır / PDF): {admin_link}\n"))
    elif obj.get("status") in DISPUTE_RESULTS:
        notify_team(sub, "dispute_closed", amount=obj.get("amount"),
                    extra=f"Sonuç: {DISPUTE_RESULTS[obj['status']]}\nStripe: {stripe_link}\n")


HANDLERS = {
    "charge.dispute.created": _on_dispute,
    "charge.dispute.closed": _on_dispute,
    "checkout.session.completed": _on_checkout,
    "checkout.session.async_payment_succeeded": _on_checkout,
    "invoice.paid": _on_invoice_paid,
    "invoice.payment_failed": _on_invoice_failed,
    "invoice.upcoming": _on_invoice_upcoming,
    "customer.subscription.updated": _on_subscription,
    "customer.subscription.deleted": _on_subscription,
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
