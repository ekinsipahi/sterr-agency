from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.core.models import Package
from apps.seo.cities import CITY_BY_SLUG

from .forms import LeadForm
from .ga4 import cookies_for
from .notifications import notify_new_lead

RATE_LIMIT = 5          # submissions
RATE_WINDOW = 60 * 60   # per hour per IP


def _client_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    return fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR")


def apply(request):
    """The qualifying application form (our funnel's front door)."""
    initial = {}
    city = request.GET.get("il")
    if city in CITY_BY_SLUG:
        initial["city"] = city
    form = LeadForm(initial=initial)
    return render(request, "leads/apply.html", {
        "form": form,
        "packages": Package.objects.filter(is_active=True),
        "selected_package": request.GET.get("paket", ""),
    })


@require_POST
def submit(request):
    form = LeadForm(request.POST)
    ip = _client_ip(request)

    if form.is_spam():
        return redirect("leads:thanks")

    key = f"lead-rate:{ip}"
    if cache.get(key, 0) >= RATE_LIMIT:
        form.add_error(None, "Çok fazla deneme yapıldı. Lütfen WhatsApp üzerinden bize ulaşın.")

    if not form.errors and form.is_valid():
        lead = form.save(commit=False)
        lead.ip = ip
        lead.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
        lead.source_page = request.POST.get("source_page", "")[:300]
        for field in ("utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid"):
            setattr(lead, field, request.POST.get(field, "")[:150])
        lead.ga_client_id, lead.ga_session_id = cookies_for(request)
        package = request.POST.get("package", "")
        if package:
            lead.message = f"[Paket: {package}] {lead.message}".strip()
        lead.score = lead.compute_score()
        lead.save()
        cache.set(key, cache.get(key, 0) + 1, RATE_WINDOW)

        lead.notified = notify_new_lead(lead)
        lead.save(update_fields=["notified"])

        # One-shot payload for the thank-you page's generate_lead event.
        request.session["lead_event"] = {
            "lead_id": str(lead.pk),
            "value": lead.estimated_value,
            "currency": "TRY",
            "lead_tier": lead.tier,
            "lead_sector": lead.sector,
            "lead_budget": lead.budget,
            "lead_city": lead.city or "none",
            "package": package or "none",
            "form_id": "basvuru",
        }
        return redirect(reverse("leads:thanks"))

    return render(request, "leads/apply.html", {
        "form": form,
        "packages": Package.objects.filter(is_active=True),
        "selected_package": request.POST.get("package", ""),
    }, status=400)


def thanks(request):
    lead_event = request.session.pop("lead_event", None)
    below_min = bool(lead_event) and lead_event["lead_budget"] == "lt50"
    return render(request, "leads/thanks.html", {"below_min": below_min, "lead_event": lead_event})
