"""'Yeni lead geldi' email to the team, sent through the configured backend (Resend)."""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def notify_new_lead(lead) -> bool:
    recipients = settings.LEAD_NOTIFY_EMAILS
    if not recipients:
        logger.warning("LEAD_NOTIFY_EMAILS empty; lead #%s saved without notification", lead.pk)
        return False

    ctx = {"lead": lead, "admin_url": f"{settings.SITE_URL}/admin/leads/lead/{lead.pk}/change/"}
    subject = f"[{lead.tier}] Yeni lead: {lead.name} — {lead.get_sector_display()} · {lead.get_budget_display()}"
    msg = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string("leads/email/new_lead.txt", ctx),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[lead.email],
    )
    msg.attach_alternative(render_to_string("leads/email/new_lead.html", ctx), "text/html")
    try:
        msg.send(fail_silently=False)
    except Exception:
        # Never lose a lead because email failed — it is already in the DB.
        logger.exception("Lead notification failed for lead #%s", lead.pk)
        return False
    return True
