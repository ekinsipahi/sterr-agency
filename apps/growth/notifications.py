"""Emails for the growth subscription: Turkish notes to the team, the customer's
language for the customer. Failures are logged, never raised."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


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


def welcome_customer(sub, ui, manage_url):
    subject = ui["mail_welcome_subject"].replace("{handle}", sub.instagram)
    body = (ui["mail_welcome_body"].replace("{handle}", sub.instagram).replace("{location}", sub.location)
            .replace("{manage}", manage_url))
    return _send(subject, body, [sub.email])


def confirm_cancellation(sub, ui, manage_url):
    """Customer email when they cancel: the plan stays active until the paid month ends."""
    from django.utils import formats, translation

    from apps.core.languages import LANG_BY_CODE

    date = ""
    if sub.current_period_end:
        lang = LANG_BY_CODE.get(sub.lang)
        with translation.override(lang.django if lang else "en"):
            date = formats.date_format(sub.current_period_end, "DATE_FORMAT")
    fill = lambda text: text.replace("{handle}", sub.instagram).replace("{date}", date).replace("{manage}", manage_url)
    return _send(fill(ui["mail_cancel_subject"]), fill(ui["mail_cancel_body"]), [sub.email])


def send_manage_link(email, ui, link):
    return _send(ui["mail_manage_subject"], ui["mail_manage_body"].replace("{link}", link), [email])
