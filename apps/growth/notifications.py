"""Emails for follower orders and accounts: Turkish notes to the team, English for the
customer whatever language the page was in. Failures are logged, never raised."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import formats, translation

from .constants import PROFILE_URL

logger = logging.getLogger(__name__)

VERIFY_SUBJECT = "Confirm your email to complete your order"
VERIFY_BODY = (
    "Hi,\n\nPlease confirm your email address. The link takes you straight to secure payment for your order "
    "of {followers} real {platform} followers for @{handle}:\n\n{link}\n\n"
    "If you didn't create an account on sterragency.com, you can ignore this email."
)
SIGNUP_VERIFY_SUBJECT = "Confirm your email"
SIGNUP_VERIFY_BODY = (
    "Hi,\n\nPlease confirm your email address for your Sterr Agency account:\n\n{link}\n\n"
    "If you didn't create an account on sterragency.com, you can ignore this email."
)
REQUEST_SUBJECT = "We received your order request: {followers} real {platform} followers for @{handle}"
REQUEST_BODY = (
    "Thanks! We've received your request for {followers} real {platform} followers for @{handle} ({location}).\n\n"
    "We'll email you within 24 hours to confirm and get started. We will never ask for your password.\n\n"
    "You can follow your order in your account: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
PAID_SUBJECT = "Payment received: {followers} real {platform} followers for @{handle}"
PAID_BODY = (
    "Thanks for your order. We've received your payment of ${amount} for {followers} real {platform} followers "
    "for @{handle} ({location}).\n\n"
    "Delivery has started. Every follower is a real person, so they arrive gradually: expect your order to be "
    "complete between {start} and {end}. Nothing arrives instantly, and that's how it should be: instant "
    "followers are bots.\n\n"
    "We will never ask for your password. Keep your account public while delivery is running.\n\n"
    "No refunds: delivery has started and continues until your order is complete.\n\n"
    "Your orders: {account}\n\n"
    "Questions? Message us on WhatsApp: {whatsapp}"
)
COMPLETED_SUBJECT = "Your order is complete: {followers} real {platform} followers for @{handle}"
COMPLETED_BODY = (
    "Your order of {followers} real {platform} followers for @{handle} is complete.\n\n"
    "Thanks for growing with us. Whenever you're ready for the next step: {account}"
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


def _values(order):
    start, end = order.delivery_window()
    return {"followers": f"{order.followers:,}", "platform": order.platform_name, "handle": order.handle,
            "location": order.location, "amount": f"{order.amount:.2f}", "start": _date(start), "end": _date(end),
            "account": f"{settings.SITE_URL}{reverse('growth:account')}?lang={order.lang}",
            "whatsapp": settings.WHATSAPP_DISPLAY}


def notify_team(order, event):
    """event: 'pending' (order placed, on its way to payment), 'request' (payments off), 'paid', 'refunded'."""
    titles = {"pending": "Yeni {platform} takipçi siparişi (ödeme bekleniyor)",
              "request": "Yeni {platform} takipçi başvurusu", "paid": "Yeni {platform} takipçi siparişi (ödendi)",
              "refunded": "{platform} takipçi siparişi iade edildi"}
    title = titles[event].replace("{platform}", order.platform_name)
    start, end = order.delivery_window()
    body = (
        f"{title}\n\n"
        f"Paket: {order.followers:,} takipçi · ${order.amount:.2f}\n"
        f"{order.platform_name}: @{order.handle}  ({PROFILE_URL[order.platform].format(order.handle)})\n"
        f"Hedef konum: {order.location}\n"
        f"E-posta: {order.email}\n"
        f"Teslim aralığı: {start:%d.%m.%Y} – {end:%d.%m.%Y}\n"
        f"Dil: {order.lang}\n"
        f"Kaynak: {order.source_page or '-'} {order.utm_source or ''}\n\n"
        f"Admin: {settings.SITE_URL}/admin/growth/followerorder/{order.pk}/change/\n"
    )
    to = list(dict.fromkeys([*settings.LEAD_NOTIFY_EMAILS, *settings.GROWTH_NOTIFY_EMAILS]))
    return _send(f"{title}: @{order.handle}", body, to, reply_to=[order.email])


def acknowledge_request(order):
    v = _values(order)
    return _send(_fill(REQUEST_SUBJECT, **v), _fill(REQUEST_BODY, **v), [order.email])


def confirm_payment(order):
    v = _values(order)
    return _send(_fill(PAID_SUBJECT, **v), _fill(PAID_BODY, **v), [order.email])


def confirm_completed(order):
    v = _values(order)
    return _send(_fill(COMPLETED_SUBJECT, **v), _fill(COMPLETED_BODY, **v), [order.email])


def send_verification(email, link, order=None):
    if order is None:
        return _send(SIGNUP_VERIFY_SUBJECT, _fill(SIGNUP_VERIFY_BODY, link=link), [email])
    return _send(VERIFY_SUBJECT, _fill(VERIFY_BODY, link=link, **_values(order)), [email])


def send_password_reset(email, link):
    return _send(RESET_SUBJECT, _fill(RESET_BODY, link=link), [email])
