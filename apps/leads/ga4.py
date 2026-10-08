"""Server-side GA4 events via the Measurement Protocol.

Admin status changes become GA4's recommended lead events, so the whole funnel
(generate_lead → qualify_lead → close_convert_lead) lives in one GA4 property:
https://developers.google.com/analytics/devguides/collection/ga4/reference/events
"""
import logging
import re
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MP_ENDPOINT = "https://www.google-analytics.com/mp/collect"

# Lead.status → (GA4 event, extra params builder)
STATUS_EVENTS = {
    "contacted": "working_lead",
    "meeting": "qualify_lead",
    "proposal": "lead_proposal_sent",
    "won": "close_convert_lead",
    "lost": "close_unconvert_lead",
    "unqualified": "disqualify_lead",
}


def parse_client_id(ga_cookie: str) -> str:
    """'_ga' cookie 'GA1.1.123456789.1700000000' → '123456789.1700000000'."""
    parts = (ga_cookie or "").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 4 else ""


def parse_session_id(session_cookie: str) -> str:
    """'_ga_<ID>' cookie, old 'GS1.1.1700000000.1...' or new 'GS2.1.s1700000000$o1...' format."""
    m = re.match(r"GS\d\.\d\.s?(\d+)", session_cookie or "")
    return m.group(1) if m else ""


def cookies_for(request) -> tuple[str, str]:
    client_id = parse_client_id(request.COOKIES.get("_ga", ""))
    session_id = ""
    if settings.GA4_ID:
        suffix = settings.GA4_ID.replace("G-", "")
        session_id = parse_session_id(request.COOKIES.get(f"_ga_{suffix}", ""))
    return client_id, session_id


def send_event(lead, name: str, params: dict | None = None) -> bool:
    if not (settings.GA4_ID and settings.GA4_API_SECRET):
        return False
    params = {**(params or {}), "lead_id": str(lead.pk), "lead_source": lead.utm_source or "direct",
              "engagement_time_msec": 1}
    if lead.ga_session_id:
        params["session_id"] = lead.ga_session_id
    payload = {
        # Without a _ga cookie (no consent / ad-blocker) fall back to a stable per-lead id.
        "client_id": lead.ga_client_id or f"{lead.pk}.{int(lead.created_at.timestamp())}",
        "timestamp_micros": int(time.time() * 1_000_000),
        "events": [{"name": name, "params": params}],
    }
    try:
        resp = requests.post(
            MP_ENDPOINT,
            params={"measurement_id": settings.GA4_ID, "api_secret": settings.GA4_API_SECRET},
            json=payload,
            timeout=5,
        )
        resp.raise_for_status()
    except Exception:
        logger.exception("GA4 MP event %s failed for lead #%s", name, lead.pk)
        return False
    return True


def send_status_event(lead) -> bool:
    name = STATUS_EVENTS.get(lead.status)
    if not name:
        return False
    params = {"currency": "TRY", "value": lead.estimated_value, "lead_status": lead.get_status_display()}
    if lead.status == "won":
        params["value"] = lead.deal_value or lead.estimated_value
    elif lead.status == "lost":
        params["unconvert_lead_reason"] = "lost"
    elif lead.status == "unqualified":
        params["disqualified_lead_reason"] = f"budget_{lead.budget}"
    return send_event(lead, name, params)
