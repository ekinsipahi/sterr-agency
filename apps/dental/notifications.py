"""'Yeni diş turizmi talebi' email to the team (same Resend backend as leads)."""
import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def notify_inquiry(inquiry) -> bool:
    recipients = settings.LEAD_NOTIFY_EMAILS
    if not recipients:
        logger.warning("LEAD_NOTIFY_EMAILS empty; dental inquiry #%s saved without notification", inquiry.pk)
        return False
    lines = [
        f"Tür: {inquiry.get_kind_display()}",
        f"Dil: {inquiry.get_lang_display()}",
        f"Ad: {inquiry.name}",
        f"E-posta: {inquiry.email}",
        f"Telefon / WhatsApp: {inquiry.phone}",
        f"Ülke: {inquiry.country}",
    ]
    if inquiry.company:
        lines.append(f"Klinik / acente: {inquiry.company}")
    if inquiry.treatment:
        lines.append(f"Tedavi: {inquiry.get_treatment_display()}")
    lines += ["", inquiry.message or "(mesaj yok)", "",
              f"Sayfa: {inquiry.source_page or '-'}",
              f"Admin: {settings.SITE_URL}/admin/dental/dentalinquiry/{inquiry.pk}/change/"]
    msg = EmailMessage(
        subject=f"[Diş turizmi · {inquiry.lang.upper()}] Yeni {inquiry.get_kind_display().lower()} talebi: "
                f"{inquiry.name} — {inquiry.country}",
        body="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[inquiry.email],
    )
    try:
        msg.send(fail_silently=False)
    except Exception:
        logger.exception("Dental inquiry notification failed for #%s", inquiry.pk)
        return False
    return True
