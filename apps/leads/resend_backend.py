"""Django email backend that sends through the Resend HTTP API.

Set in settings:
    EMAIL_BACKEND = "apps.leads.resend_backend.ResendEmailBackend"
    RESEND_API_KEY = "re_..."
    DEFAULT_FROM_EMAIL = "Sterr Agency <noreply@sterragency.com>"
"""
from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, "RESEND_API_KEY", "")

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        if not self.api_key:
            logger.warning("RESEND_API_KEY not set; skipping %d email(s)", len(email_messages))
            if not self.fail_silently:
                raise RuntimeError("RESEND_API_KEY is not configured.")
            return 0

        sent = 0
        for message in email_messages:
            payload = {
                "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                "to": list(message.to),
                "subject": message.subject,
                "text": message.body,
            }
            if message.cc:
                payload["cc"] = list(message.cc)
            if message.bcc:
                payload["bcc"] = list(message.bcc)
            if message.reply_to:
                payload["reply_to"] = list(message.reply_to)
            # Pick up an HTML alternative if present (EmailMultiAlternatives).
            for content, mimetype in getattr(message, "alternatives", []) or []:
                if mimetype == "text/html":
                    payload["html"] = content
                    break

            try:
                resp = requests.post(
                    RESEND_ENDPOINT,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=20,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(f"Resend error {resp.status_code}: {resp.text[:300]}")
                sent += 1
            except Exception:
                logger.exception("Resend send failed")
                if not self.fail_silently:
                    raise
        return sent
