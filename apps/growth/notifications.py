"""Emails for the influencer packages and accounts: Turkish notes to the team, English for the
customer whatever language the page was in. Failures are logged, never raised."""
import logging
import math

from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import formats, timezone, translation

from . import plan
from .constants import PROFILE_URL

logger = logging.getLogger(__name__)

VERIFY_SUBJECT = "Confirm your email to start your package"
VERIFY_BODY = (
    "Hi,\n\nPlease confirm your email address. The link takes you straight to secure payment for the "
    "{package} package ({platform}) for @{handle}:\n\n{link}\n\n"
    "If you didn't create an account on sterragency.com, you can ignore this email."
)
SIGNUP_VERIFY_SUBJECT = "Confirm your email"
SIGNUP_VERIFY_BODY = (
    "Hi,\n\nPlease confirm your email address for your Sterr Agency account:\n\n{link}\n\n"
    "If you didn't create an account on sterragency.com, you can ignore this email."
)
REQUEST_SUBJECT = "We received your request: {package} for @{handle} on {platform}"
REQUEST_BODY = (
    "Thanks! We've received your request for the {package} package for @{handle} on {platform} ({location}).\n\n"
    "We'll email you within 24 hours to get you started. We will never ask for your password.\n\n"
    "Your account: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
PAID_SUBJECT = "Your {package} package is active: @{handle} on {platform}"
PAID_BODY = (
    "Thanks for starting the {package} package for @{handle} on {platform} ({location}). We've received your "
    "payment of ${amount}.\n\n"
    "From today, real people discover your profile every day. Those who like it follow you, like your posts "
    "and comment, all on their own. Your package is spread over every 30 days; a typical month brings {followers} new followers, 2-3 likes for every "
    "new follower and about one comment for every 10. Every follower is a real person, so every month is a "
    "little different, and nothing arrives instantly: instant followers are bots.\n\n"
    "You'll see your numbers in your account. We will never ask for your password; keep your account public "
    "while the package runs.\n\n"
    "Billed monthly: the next payment is on {renews}. We'll email you 3 days before every renewal. Cancel any "
    "time in your account; canceling stops the next payment and the month you've paid for runs to its end "
    "(it isn't refunded).\n\n"
    "Your account: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
REMINDER_SUBJECT = "Your {package} package renews in {days} ({renews})"
REMINDER_BODY = (
    "Hi,\n\nA reminder: your {package} package for @{handle} on {platform} renews automatically on {renews}, "
    "and ${amount} will be charged to the card on file. There's nothing you need to do.\n\n"
    "Your account: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}\n\n"
    "Sterr Agency\n\n"
    "--\n"
    "You can manage or cancel your subscription any time in your account."
)
CANCELED_SUBJECT = "Cancellation confirmed: {package} for @{handle}"
CANCELED_BODY = (
    "Hi,\n\nWe've canceled the renewal of your {package} package for @{handle} on {platform}. "
    "No further payments will be taken.\n\n"
    "Your package keeps running until {renews}. Changed your mind? You can keep it from your account "
    "before then: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
RESET_SUBJECT = "Reset your password"
RESET_BODY = (
    "Hi,\n\nUse this link to set a new password for your Sterr Agency account. It works for 3 days:\n\n{link}\n\n"
    "If you didn't ask for this, you can ignore this email; your password stays the same."
)


def _fill(text, **values):
    for key, value in values.items():
        text = text.replace("{" + key + "}", str(value))
    return text


class MailResult:
    """Truthy when sent; `error` says why not (shown in the admin)."""

    def __init__(self, ok, error=""):
        self.ok, self.error = ok, error

    def __bool__(self):
        return self.ok


def _send(subject, body, to, reply_to=None):
    if not to:
        logger.warning("Growth email skipped, no recipient: %s", subject)
        return MailResult(False, "Alıcı yok (LEAD_NOTIFY_EMAILS boş)")
    try:
        EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=to,
                     reply_to=reply_to).send(fail_silently=False)
    except Exception as exc:
        logger.exception("Growth email failed: %s", subject)
        return MailResult(False, str(exc)[:500])
    if "console" in settings.EMAIL_BACKEND:
        return MailResult(False, "RESEND_API_KEY yok: e-posta sadece loga yazıldı")
    return MailResult(True)


def _date(value):
    with translation.override("en"):
        return formats.date_format(value, "F j, Y")


def _values(sub):
    return {"platform": sub.platform_name, "handle": sub.handle, "location": sub.location, "amount": f"{sub.amount:.2f}",
            "package": sub.get_plan_display(),
            "followers": "{:,}-{:,}".format(*plan.PLAN_BY_KEY[sub.plan]["followers"]),
            "renews": _date(sub.current_period_end) if sub.current_period_end else "the same day next month",
            "account": f"{settings.SITE_URL}{reverse('growth:account')}?lang={sub.lang}",
            "whatsapp": settings.WHATSAPP_DISPLAY}


TEAM_TITLES = {
    "request": "Yeni {platform} influencer paketi başvurusu",
    "paid": "Yeni {platform} influencer paketi (ödendi)",
    "renewed": "{platform} influencer paketi yenilendi (ödendi)",
    "cancel_requested": "{platform} influencer paketi iptal talebi (dönem sonunda biter)",
    "resumed": "{platform} influencer paketi iptali geri alındı",
    "canceled": "{platform} influencer paketi iptal edildi",
    "dispute": "DİKKAT: {platform} influencer paketi ödemesine itiraz (dispute) açıldı",
    "dispute_closed": "{platform} influencer paketi itirazı sonuçlandı",
}
CANCEL_SOURCES = {"account": "müşteri hesap panelinden",
                  "stripe": "Stripe müşteri portalından veya Stripe panelinden"}


def notify_team(sub, event, amount=None, extra=""):
    """event: 'request' (payments off), 'paid' (first payment confirmed by Stripe),
    'renewed' (a monthly payment), 'cancel_requested' (no renewal, runs to the period end),
    'resumed' (that cancel taken back), 'canceled' (ended), 'dispute' / 'dispute_closed'
    (a chargeback; `extra` carries its details). Nothing is sent before a payment."""
    title = TEAM_TITLES[event].replace("{platform}", sub.platform_name)
    paid = f"${int(amount) / 100:.2f}" if amount is not None else f"${sub.amount:.2f}"
    period = f"{sub.current_period_end:%d.%m.%Y}" if sub.current_period_end else "-"
    canceled = ""
    if event == "cancel_requested" and sub.cancel_requested_at:
        canceled = f"İptal: {sub.cancel_requested_at:%d.%m.%Y %H:%M} UTC, {CANCEL_SOURCES.get(sub.cancel_source, '-')}\n"
    body = (
        f"{title}\n\n"
        f"Paket: {sub.get_plan_display()} · {paid} / ay\n"
        f"{sub.platform_name}: @{sub.handle}  ({PROFILE_URL[sub.platform].format(sub.handle)})\n"
        f"Hedef konum: {sub.location}\n"
        f"E-posta: {sub.email}\n"
        f"{'Bitiş' if sub.cancel_at_period_end or event == 'canceled' else 'Sonraki ödeme'}: {period}\n"
        f"{canceled}"
        f"{extra}"
        f"Dil: {sub.lang}\n"
        f"Kaynak: {sub.source_page or '-'} {sub.utm_source or ''}\n\n"
        f"Admin: {settings.SITE_URL}/admin/growth/agencysubscription/{sub.pk}/change/\n"
    )
    to = list(dict.fromkeys([*settings.LEAD_NOTIFY_EMAILS, *settings.GROWTH_NOTIFY_EMAILS]))
    return _send(f"{title}: @{sub.handle}", body, to, reply_to=[sub.email])


def acknowledge_request(sub):
    v = _values(sub)
    return _send(_fill(REQUEST_SUBJECT, **v), _fill(REQUEST_BODY, **v), [sub.email])


def confirm_payment(sub):
    v = _values(sub)
    return _send(_fill(PAID_SUBJECT, **v), _fill(PAID_BODY, **v), [sub.email])


def remind_renewal(sub):
    v = _values(sub)
    days = max(1, math.ceil((sub.current_period_end - timezone.now()).total_seconds() / 86400))
    v["days"] = "1 day" if days == 1 else f"{days} days"
    return _send(_fill(REMINDER_SUBJECT, **v), _fill(REMINDER_BODY, **v), [sub.email])


def confirm_cancel(sub):
    v = _values(sub)
    return _send(_fill(CANCELED_SUBJECT, **v), _fill(CANCELED_BODY, **v), [sub.email])


def send_verification(email, link, sub=None):
    if sub is None:
        return _send(SIGNUP_VERIFY_SUBJECT, _fill(SIGNUP_VERIFY_BODY, link=link), [email])
    return _send(VERIFY_SUBJECT, _fill(VERIFY_BODY, link=link, **_values(sub)), [email])


def send_password_reset(email, link):
    return _send(RESET_SUBJECT, _fill(RESET_BODY, link=link), [email])
