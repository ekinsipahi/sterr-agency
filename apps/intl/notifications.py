"""'Yeni yurt dışı başvuru' email to the team (same Resend backend as leads)."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def notify_intl_lead(lead) -> bool:
    recipients = settings.LEAD_NOTIFY_EMAILS
    if not recipients:
        logger.warning("LEAD_NOTIFY_EMAILS empty; intl lead #%s saved without notification", lead.pk)
        return False
    lines = [
        f"Dil: {lead.get_lang_display()}",
        f"Hizmet: {lead.get_interest_display()}",
        f"Ad: {lead.name}",
        f"E-posta: {lead.email}",
        f"Telefon / WhatsApp: {lead.phone}",
        f"Ülke: {lead.country}",
        f"İşletme: {lead.company or '-'}",
        f"Web / Instagram: {lead.website or '-'}",
        f"Gördüğü fiyat: {lead.quoted_price} (pazar: {lead.usd_price} USD)",
        "", lead.message or "(mesaj yok)", "",
        f"Sayfa: {lead.source_page or '-'}",
        f"Admin: {settings.SITE_URL}/admin/intl/intllead/{lead.pk}/change/",
    ]
    msg = EmailMessage(
        subject=f"[Yurt dışı · {lead.lang.upper()}] Yeni başvuru: {lead.name} — {lead.country}",
        body="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[lead.email],
    )
    try:
        msg.send(fail_silently=False)
    except Exception:
        logger.exception("Intl lead notification failed for #%s", lead.pk)
        return False
    return True
