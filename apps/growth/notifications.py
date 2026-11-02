"""Emails for the growth subscription: Turkish notes to the team, English for the
customer whatever language the page was in. Failures are logged, never raised."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import formats, translation

from .content import PLATFORM_NAMES, PROFILE_URL

logger = logging.getLogger(__name__)

WELCOME_SUBJECT = "Your plan is active: organic {platform} growth for @{handle} has started"
WELCOME_BODY = (
    "Thanks for subscribing. Organic {platform} growth for @{handle} ({location}) starts now. New followers arrive "
    "gradually; on average our clients gain 900–3,000 real followers a month.\n\n"
    "We will never ask for your password.\n\n"
    "You can cancel any time. Cancellation stops the next renewal; the month already started is not refunded.\n\n"
    "To cancel, use this link at any time: {cancel}"
)
CANCEL_SUBJECT = "Cancellation confirmed: your plan stays active until {date}"
CANCEL_BODY = (
    "Your cancellation for @{handle} is confirmed.\n\n"
    "Your plan stays active until {date}: growth continues until then, and you won't be charged again. "
    "As the month had already started, it isn't refunded.\n\n"
    "Changed your mind? You can keep your plan here: {manage}"
)
REQUEST_SUBJECT = "We received your request: organic {platform} growth for @{handle}"
REQUEST_BODY = (
    "Thanks! We've received your request for organic {platform} growth for @{handle} ({location}).\n\n"
    "We'll email you within 24 hours to get started. We will never ask for your password.\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
MANAGE_SUBJECT = "Your subscription link"
MANAGE_BODY = (
    "Here is your secure link to manage or cancel your growth subscription. It is valid for one hour:\n\n"
    "{link}\n\nIf you didn't request this, you can ignore this email."
)


def _fill(text, **values):
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
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


def notify_team(sub, event):
    """event: 'request' (no Stripe yet), 'started', 'payment_failed', 'cancel_scheduled', 'canceled'."""
    titles = {
        "request": "Yeni {platform} büyütme başvurusu",
        "started": "Yeni {platform} aboneliği başladı",
        "payment_failed": "{platform} aboneliği: ödeme başarısız",
        "cancel_scheduled": "{platform} aboneliği iptal edildi (dönem sonunda bitecek)",
        "canceled": "{platform} aboneliği sona erdi",
    }
    platform = PLATFORM_NAMES[sub.platform]
    title = titles[event].replace("{platform}", platform)
    body = (
        f"{title}\n\n"
        f"{platform}: @{sub.instagram}  ({PROFILE_URL[sub.platform].format(sub.instagram)})\n"
        f"Hedef konum: {sub.location}\n"
        f"E-posta: {sub.email}\n"
        f"Dil: {sub.lang}\n"
        f"Durum: {sub.get_status_display()}\n"
        f"Kaynak: {sub.source_page or '-'} {sub.utm_source or ''}\n\n"
        f"Admin: {settings.SITE_URL}/admin/growth/growthsubscription/{sub.pk}/change/\n"
    )
    return _send(f"{title}: @{sub.instagram}", body, settings.LEAD_NOTIFY_EMAILS, reply_to=[sub.email])


def acknowledge_request(sub):
    """English auto-reply when the form only takes requests (payments off)."""
    values = {"handle": sub.instagram, "location": sub.location, "whatsapp": settings.WHATSAPP_DISPLAY,
              "platform": PLATFORM_NAMES[sub.platform]}
    return _send(_fill(REQUEST_SUBJECT, **values), _fill(REQUEST_BODY, **values), [sub.email])


def welcome_customer(sub, cancel_url):
    """'Your plan is active' email, with a direct cancel link for the life of the subscription."""
    values = {"handle": sub.instagram, "location": sub.location, "cancel": cancel_url, "platform": PLATFORM_NAMES[sub.platform]}
    return _send(_fill(WELCOME_SUBJECT, **values), _fill(WELCOME_BODY, **values), [sub.email])


def confirm_cancellation(sub, manage_url):
    """Customer email when they cancel: the plan stays active until the paid month ends."""
    date = ""
    if sub.current_period_end:
        with translation.override("en"):
            date = formats.date_format(sub.current_period_end, "F j, Y")
    values = {"handle": sub.instagram, "date": date, "manage": manage_url}
    return _send(_fill(CANCEL_SUBJECT, **values), _fill(CANCEL_BODY, **values), [sub.email])


def send_manage_link(email, link):
    return _send(MANAGE_SUBJECT, _fill(MANAGE_BODY, link=link), [email])
