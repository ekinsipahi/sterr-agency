"""Emails for the growth subscription: Turkish notes to the team, English for the
customer whatever language the page was in. Failures are logged, never raised."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import formats, translation

logger = logging.getLogger(__name__)

WELCOME_SUBJECT = "Your plan is active: organic growth for @{handle} has started"
WELCOME_BODY = (
    "Thanks for subscribing. Organic growth for @{handle} ({location}) starts now. New followers arrive "
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
MANAGE_SUBJECT = "Your subscription link"
MANAGE_BODY = (
    "Here is your secure link to manage or cancel your Instagram growth subscription. It is valid for one hour:\n\n"
    "{link}\n\nIf you didn't request this, you can ignore this email."
)


def _fill(text, **values):
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text


def _send(subject, body, to, reply_to=None):
    if not to:
        return False
    try:
        EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=to,
                     reply_to=reply_to).send(fail_silently=False)
    except Exception:
        logger.exception("Growth email failed: %s", subject)
        return False
    return True


def notify_team(sub, event):
    """event: 'request' (no Stripe yet), 'started', 'payment_failed', 'cancel_scheduled', 'canceled'."""
    titles = {
        "request": "Yeni Instagram büyütme talebi (ödeme linki gönderilecek)",
        "started": "Yeni Instagram aboneliği başladı",
        "payment_failed": "Instagram aboneliği: ödeme başarısız",
        "cancel_scheduled": "Instagram aboneliği iptal edildi (dönem sonunda bitecek)",
        "canceled": "Instagram aboneliği sona erdi",
    }
    body = (
        f"{titles[event]}\n\n"
        f"Instagram: @{sub.instagram}  (https://www.instagram.com/{sub.instagram}/)\n"
        f"Hedef konum: {sub.location}\n"
        f"E-posta: {sub.email}\n"
        f"Dil: {sub.lang}\n"
        f"Durum: {sub.get_status_display()}\n"
        f"Kaynak: {sub.source_page or '-'} {sub.utm_source or ''}\n\n"
        f"Admin: {settings.SITE_URL}/admin/growth/growthsubscription/{sub.pk}/change/\n"
    )
    return _send(f"{titles[event]}: @{sub.instagram}", body, settings.LEAD_NOTIFY_EMAILS, reply_to=[sub.email])


def welcome_customer(sub, cancel_url):
    """'Your plan is active' email, with a direct cancel link for the life of the subscription."""
    values = {"handle": sub.instagram, "location": sub.location, "cancel": cancel_url}
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
