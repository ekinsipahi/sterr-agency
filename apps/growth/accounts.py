"""Customer accounts: email + password or Google, the subscriptions dashboard, email
confirmation and password reset. Pages follow the visitor's language (?lang=, then the session); emails are English."""
import logging
import secrets
from datetime import timedelta
from urllib.parse import urlencode

import requests

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.cache import cache
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import formats, translation
from django.utils.encoding import force_bytes, force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from apps.leads.views import _client_ip

from . import billing
from .content import CONTENT, PLATFORM_NAMES, PLATFORMS, UI, page_path, ui_for
from .forms import LoginForm, NewPasswordForm, ResetRequestForm, SignupForm
from .models import AgencySubscription, Customer
from .notifications import send_password_reset, send_verification
from .plan import count
from .views import VERIFY_MAX_AGE, VERIFY_SALT, google_enabled, place_order, shell, start_checkout, verify_link

logger = logging.getLogger(__name__)
TRIES, TRIES_WINDOW = 10, 60 * 60


def _lang(request):
    code = request.GET.get("lang") or request.POST.get("lang")
    if code not in UI:
        code = request.session.get("growth_lang")
    if code not in UI and request.user.is_authenticated and hasattr(request.user, "customer"):
        code = request.user.customer.lang
    code = code if code in UI else "en"
    request.session["growth_lang"] = code
    return code


def _limited(request, what):
    key = f"growth-{what}:{_client_ip(request)}"
    if cache.get(key, 0) >= TRIES:
        return True
    cache.set(key, cache.get(key, 0) + 1, TRIES_WINDOW)
    return False


def _ctx(request, code, mode, **extra):
    gu = ui_for(code, "instagram")
    ctx = shell(code)
    ctx.update({
        "mode": mode, "gu": gu, "robots": "noindex, nofollow", "followers_active": True,
        "lang_links": [], "alternates": [],
        "order_links": [{"name": PLATFORM_NAMES[p], "url": page_path(code, "main", p) + "#start"} for p in PLATFORMS if code in CONTENT[p]],
        "nav_cta_href": "#", "nav_cta_label": gu["nav_cta"],
        "google": google_enabled(), "google_failed": request.GET.get("google") == "failed",
    })
    if ctx["order_links"]:
        ctx["nav_cta_href"] = ctx["order_links"][0]["url"]
    ctx.update(extra)
    return ctx


def _next(request, code):
    nxt = request.POST.get("next") or request.GET.get("next") or ""
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return nxt
    return f"{reverse('growth:account')}?lang={code}"


def account(request):
    code = _lang(request)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('growth:login')}?lang={code}")
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={"lang": code})
    ui = UI[code]
    subs = []
    with translation.override("nb" if code == "no" else code):
        def day(value):
            return formats.date_format(value, "DATE_FORMAT")

        for s in AgencySubscription.objects.filter(user=request.user).exclude(status="canceled", started_at__isnull=True).prefetch_related("stats"):
            stats = list(s.stats.all())
            since = (s.current_period_end - timedelta(days=30)).date() if s.current_period_end else None
            month = [r for r in stats if since is None or r.date > since]
            gained = s.gained
            renews = ""
            if s.current_period_end and s.status in ("active", "past_due"):
                renews = ui["acc_ends" if s.cancel_at_period_end else "acc_renews"].replace("{date}", day(s.current_period_end))
            subs.append({
                "s": s, "status": ui[f"st_{s.status}"], "amount": f"${s.amount:.2f}", "name": ui[f"plan_{s.plan}"],
                "started": ui["acc_ordered"].replace("{date}", day(s.started_at or s.created_at)),
                "renews": renews,
                "tiles": [(count(gained, code) if gained is not None else "–", ui["acc_gained"]),
                          (count(sum(r.likes for r in month), code), ui["acc_likes"]),
                          (count(sum(r.comments for r in month), code), ui["acc_comments"])] if stats else [],
                "now": ui["acc_now"].replace("{count}", count(s.current_followers, code)) if s.current_followers is not None else "",
                "updated": ui["acc_updated"].replace("{date}", formats.date_format(s.stats_at, "DATETIME_FORMAT")) if s.stats_at else "",
                "chart": _chart(stats),
                "can_pay": s.status == "pending" and billing.enabled(),
                "can_manage": bool(s.stripe_customer_id) and billing.enabled(),
            })
    summary = []
    live = [item["s"] for item in subs if item["s"].started_at]
    if live:
        latest = max((s for s in live if s.current_followers is not None), key=lambda s: s.stats_at, default=None)
        totals = AgencySubscription.objects.filter(pk__in=[s.pk for s in live]).aggregate(
            likes=Sum("stats__likes"), comments=Sum("stats__comments"))
        summary = [
            (count(sum(s.gained or 0 for s in live), code), ui["acc_sum_gained"]),
            (count((totals["likes"] or 0) + (totals["comments"] or 0), code), ui["acc_sum_engagement"]),
            (count(latest.current_followers, code) if latest else "–", ui["acc_sum_now"]),
        ]
    flags = {k: request.GET.get(k) for k in ("verify", "verified", "error", "reset")}
    return render(request, "growth/account.html", _ctx(request, code, "dashboard", subs=subs, summary=summary, customer=customer, flags=flags,
                                                       payments=billing.enabled(), signup_event=request.session.pop("growth_signup", None),
                                                       needs_verify=settings.GROWTH_VERIFY_EMAIL and not customer.email_verified))


def _chart(stats, width=320, height=72):
    """SVG polyline points for the account's follower count, day by day."""
    readings = [(r.date, r.followers) for r in stats if r.followers is not None]
    if len(readings) < 2:
        return ""
    low, high = min(f for _, f in readings), max(f for _, f in readings)
    first, last = readings[0][0].toordinal(), readings[-1][0].toordinal()
    xspan, yspan = max(last - first, 1), max(high - low, 1)
    return " ".join(f"{(d.toordinal() - first) / xspan * width:.1f},{height - (f - low) / yspan * (height - 4) - 2:.1f}"
                    for d, f in readings)


def login_view(request):
    code = _lang(request)
    gu = ui_for(code, "instagram")
    form = LoginForm(request.POST or None, ui=gu)
    if request.method == "POST" and form.is_valid():
        if _limited(request, "login"):
            form.add_error(None, gu["err_rate"])
        else:
            user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user is None:
                form.add_error(None, gu["login_error"])
            else:
                login(request, user)
                request.session["growth_login"] = True
                return redirect(_next(request, code))
    return render(request, "growth/account.html", _ctx(request, code, "login", form=form, next=request.GET.get("next", "")),
                  status=400 if form.errors else 200)


def signup_view(request):
    code = _lang(request)
    gu = ui_for(code, "instagram")
    form = SignupForm(request.POST or None, ui=gu)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        User = get_user_model()
        if _limited(request, "signup"):
            form.add_error(None, gu["err_rate"])
        elif User.objects.filter(username=email).exists():
            form.add_error("email", gu["signup_exists"])
        else:
            user = User.objects.create_user(username=email, email=email, password=form.cleaned_data["password"])
            Customer.objects.create(user=user, lang=code)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session["growth_signup"] = {"method": "email", "language": code}
            if settings.GROWTH_VERIFY_EMAIL:
                send_verification(email, verify_link(user))
                return redirect(f"{reverse('growth:account')}?lang={code}&verify=sent")
            return redirect(_next(request, code))
    return render(request, "growth/account.html", _ctx(request, code, "signup", form=form, next=request.GET.get("next", "")),
                  status=400 if form.errors else 200)


@require_POST
def logout_view(request):
    code = _lang(request)
    logout(request)
    return redirect(page_path(code, "main") if code in CONTENT["instagram"] else "/")


def verify(request, token):
    code = _lang(request)
    try:
        data = signing.loads(token, salt=VERIFY_SALT, max_age=VERIFY_MAX_AGE)
    except signing.BadSignature:
        return redirect(f"{reverse('growth:account')}?lang={code}&verify=invalid")
    user = get_user_model().objects.filter(pk=data.get("u"), email=data.get("e")).first()
    if user is None:
        return redirect(f"{reverse('growth:account')}?lang={code}&verify=invalid")
    customer, _ = Customer.objects.get_or_create(user=user, defaults={"lang": code})
    customer.email_verified = True
    customer.save(update_fields=["email_verified"])
    # The link proves the inbox: sign the person in (often a different browser or the phone).
    if not request.user.is_authenticated or request.user.pk != user.pk:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    sub = AgencySubscription.objects.filter(pk=data.get("s"), user=user, status="pending").first() if data.get("s") else None
    if sub is not None and billing.enabled():
        try:
            response = redirect(start_checkout(sub, f"{reverse('growth:account')}?lang={sub.lang}"))
            response.status_code = 303
            return response
        except Exception:
            logger.exception("Stripe checkout failed for subscription #%s", sub.pk)
            return redirect(f"{reverse('growth:account')}?lang={code}&error=payment")
    return redirect(f"{reverse('growth:account')}?lang={code}&verified=1")


@require_POST
def resend_verification(request):
    code = _lang(request)
    if request.user.is_authenticated and not _limited(request, "verify"):
        sub = AgencySubscription.objects.filter(user=request.user, status="pending").first()
        send_verification(request.user.email, verify_link(request.user, sub), sub)
    return redirect(f"{reverse('growth:account')}?lang={code}&verify=sent")


@require_POST
def pay(request, sub_id):
    """'Start now' for a subscription saved earlier (e.g. after a canceled checkout)."""
    code = _lang(request)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('growth:login')}?lang={code}")
    sub = AgencySubscription.objects.filter(pk=sub_id, user=request.user, status="pending").first()
    if sub is None or not billing.enabled():
        return redirect(f"{reverse('growth:account')}?lang={code}")
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={"lang": code})
    if settings.GROWTH_VERIFY_EMAIL and not customer.email_verified:
        send_verification(request.user.email, verify_link(request.user, sub), sub)
        return redirect(f"{reverse('growth:account')}?lang={code}&verify=sent")
    try:
        response = redirect(start_checkout(sub, f"{reverse('growth:account')}?lang={code}"))
        response.status_code = 303
        return response
    except Exception:
        logger.exception("Stripe checkout failed for subscription #%s", sub.pk)
        return redirect(f"{reverse('growth:account')}?lang={code}&error=payment")


@require_POST
def billing_portal(request):
    """Stripe's customer portal: card, invoices, cancel."""
    code = _lang(request)
    if not request.user.is_authenticated:
        return redirect(f"{reverse('growth:login')}?lang={code}")
    customer = (AgencySubscription.objects.filter(user=request.user).exclude(stripe_customer_id="")
                .values_list("stripe_customer_id", flat=True).first())
    back = f"{settings.SITE_URL}{reverse('growth:account')}?lang={code}"
    if not customer or not billing.enabled():
        return redirect(back)
    try:
        response = redirect(billing.portal_url(customer, back, code))
        response.status_code = 303
        return response
    except Exception:
        logger.exception("Stripe portal failed for %s", request.user.pk)
        return redirect(f"{back}&error=payment")


def reset_request(request):
    code = _lang(request)
    gu = ui_for(code, "instagram")
    form = ResetRequestForm(request.POST or None, ui=gu)
    sent = False
    if request.method == "POST" and form.is_valid():
        if not _limited(request, "reset"):
            user = get_user_model().objects.filter(username=form.cleaned_data["email"], is_active=True).first()
            if user is not None:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                link = settings.SITE_URL + reverse("growth:reset_confirm", args=[uid, default_token_generator.make_token(user)])
                send_password_reset(user.email, f"{link}?lang={code}")
        sent = True  # same answer whether or not the email has an account
    return render(request, "growth/account.html", _ctx(request, code, "reset", form=form, sent=sent))


def reset_confirm(request, uidb64, token):
    code = _lang(request)
    gu = ui_for(code, "instagram")
    try:
        user = get_user_model().objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (ValueError, TypeError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "growth/account.html", _ctx(request, code, "reset", form=ResetRequestForm(ui=gu), invalid=True))
    form = NewPasswordForm(request.POST or None, ui=gu)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["password"])
        user.save()
        Customer.objects.filter(user=user).update(email_verified=True)  # the reset link came through their inbox
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(f"{reverse('growth:account')}?lang={code}&reset=1")
    return render(request, "growth/account.html", _ctx(request, code, "reset_confirm", form=form))


# --- Sign in with Google (OpenID Connect, authorization code flow) -----------------

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"


def _google_redirect_uri(request):
    return request.build_absolute_uri(reverse("growth:google_complete"))


def google_start(request):
    code = _lang(request)
    if not google_enabled():
        return redirect(f"{reverse('growth:login')}?lang={code}")
    if request.GET.get("order") != "1":  # a plain sign-in never places an order left from an abandoned attempt
        request.session.pop("google_order", None)
    state = secrets.token_urlsafe(24)
    request.session["google_oauth"] = {"state": state, "next": _next(request, code), "lang": code}
    params = {"client_id": settings.GOOGLE_OAUTH_CLIENT_ID, "redirect_uri": _google_redirect_uri(request),
              "response_type": "code", "scope": "openid email profile", "state": state, "prompt": "select_account"}
    return redirect(f"{GOOGLE_AUTH}?{urlencode(params)}")


def google_complete(request):
    flow = request.session.pop("google_oauth", None) or {}
    code = flow.get("lang") if flow.get("lang") in UI else _lang(request)
    failed = f"{reverse('growth:login')}?lang={code}&google=failed"
    if request.GET.get("error") and flow.get("next"):  # canceled on Google's screen: back to the form
        request.session.pop("google_order", None)
        return redirect(flow["next"])
    if not flow or request.GET.get("state") != flow.get("state") or not request.GET.get("code"):
        return redirect(failed)
    try:
        token = requests.post(GOOGLE_TOKEN, timeout=10, data={
            "code": request.GET["code"], "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET, "redirect_uri": _google_redirect_uri(request),
            "grant_type": "authorization_code"}).json()
        info = requests.get(GOOGLE_USERINFO, timeout=10,
                            headers={"Authorization": f"Bearer {token['access_token']}"}).json()
    except (requests.RequestException, KeyError, ValueError):
        logger.exception("Google sign-in failed")
        return redirect(failed)
    email = (info.get("email") or "").strip().lower()
    if not email or not info.get("email_verified") or len(email) > 150:
        return redirect(failed)
    User = get_user_model()
    user = User.objects.filter(username=email).first()
    if user is None:
        user = User.objects.create_user(username=email, email=email, password=None,
                                        first_name=(info.get("given_name") or "")[:150], last_name=(info.get("family_name") or "")[:150])
        request.session["growth_signup"] = {"method": "google", "language": code}
    if not user.is_active:
        return redirect(failed)
    customer, _ = Customer.objects.get_or_create(user=user, defaults={"lang": code})
    if not customer.email_verified:  # Google has verified the address
        customer.email_verified = True
        customer.save(update_fields=["email_verified"])
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    pending = request.session.pop("google_order", None)
    if pending:  # filled in on the order form before "Continue with Google": place it now
        response = place_order(request, user, pending)
        return response or redirect(f"{reverse('growth:account')}?lang={code}&error=payment")
    return redirect(flow.get("next") or f"{reverse('growth:account')}?lang={code}")
