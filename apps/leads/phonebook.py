"""Every phone number the site's forms collected, in one list for the admin: whose it is,
which form asked for it and why. Read-only; each row links to its own record.

Four forms ask for a phone number. Each has its own table; this module reads them all."""
from django.db.models import Q
from django.urls import reverse

# Which form, and what the visitor was told the number is for (shown as "Neden istendi").
SOURCES = {
    "growth": {
        "label": "Takipçi paketi sipariş formu",
        "why": "Influencer ile iletişimde kalmak, bağın kopmaması için (formda bu yazıyla istenir).",
    },
    "lead": {
        "label": "Başvuru formu (Türkçe site)",
        "why": "Ajans başvurusuna telefonla ya da WhatsApp'tan dönüş yapmak için.",
    },
    "intl": {
        "label": "Ajans formu (yabancı dil sayfaları)",
        "why": "Yurt dışından gelen ajans başvurusuna WhatsApp'tan dönüş yapmak için.",
    },
    "dental": {
        "label": "Diş turizmi formu",
        "why": "Hasta ya da iş birliği talebine dönüş yapmak için.",
    },
}
LIMIT = 2000   # newest rows read per form; the page is a working list, not an export


def whatsapp_url(phone):
    """wa.me link; a Turkish number written the local way (05xx... or 5xx...) gets its country code."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("00"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = "9" + digits
    elif len(digits) == 10 and digits.startswith("5"):
        digits = "90" + digits
    return f"https://wa.me/{digits}" if digits else ""


def _row(source, obj, who, detail, email, admin_name):
    return {
        "source": source, "source_label": SOURCES[source]["label"], "why": SOURCES[source]["why"],
        "date": obj.created_at, "who": who, "detail": detail, "email": email, "phone": obj.phone,
        "whatsapp": whatsapp_url(obj.phone), "status": obj.get_status_display(),
        "url": reverse(f"admin:{admin_name}_change", args=[obj.pk]),
    }


def _search(queryset, q, fields):
    if not q:
        return queryset
    cond = Q()
    for field in fields:
        cond |= Q(**{f"{field}__icontains": q})
    digits = "".join(ch for ch in q if ch.isdigit())
    if len(digits) >= 4:   # "0541 448" finds "+90 541 448 75 61" only when stored the same way; try the digits too
        cond |= Q(phone__icontains=digits)
    return queryset.filter(cond)


def rows(source="", q=""):
    """The phone numbers, newest first. source: one of SOURCES or "" for all; q: name, email,
    phone, company or username."""
    from apps.dental.models import DentalInquiry
    from apps.growth.models import AgencySubscription
    from apps.intl.models import IntlLead

    from .models import Lead

    q = (q or "").strip()
    out = []
    if source in ("", "growth"):
        subs = _search(AgencySubscription.objects.exclude(phone=""), q, ("handle", "email", "phone", "location"))
        for sub in subs.order_by("-created_at")[:LIMIT]:
            out.append(_row("growth", sub, f"@{sub.handle}", f"{sub.get_platform_display()} · {sub.get_plan_display()}",
                            sub.email, "growth_agencysubscription"))
    if source in ("", "lead"):
        leads = _search(Lead.objects.exclude(phone=""), q, ("name", "email", "phone", "company"))
        for lead in leads.order_by("-created_at")[:LIMIT]:
            out.append(_row("lead", lead, lead.name, lead.company, lead.email, "leads_lead"))
    if source in ("", "intl"):
        leads = _search(IntlLead.objects.exclude(phone=""), q, ("name", "email", "phone", "company", "country"))
        for lead in leads.order_by("-created_at")[:LIMIT]:
            out.append(_row("intl", lead, lead.name, " · ".join(v for v in (lead.company, lead.country) if v),
                            lead.email, "intl_intllead"))
    if source in ("", "dental"):
        inquiries = _search(DentalInquiry.objects.exclude(phone=""), q, ("name", "email", "phone", "company", "country"))
        for inquiry in inquiries.order_by("-created_at")[:LIMIT]:
            out.append(_row("dental", inquiry, inquiry.name,
                            " · ".join(v for v in (inquiry.get_kind_display(), inquiry.country) if v),
                            inquiry.email, "dental_dentalinquiry"))
    out.sort(key=lambda r: r["date"], reverse=True)
    return out
