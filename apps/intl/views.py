from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import translation
from django.views.decorators.http import require_POST

from apps.core.languages import LANG_BY_CODE
from apps.core.models import Testimonial
from apps.dental.languages import page_path as dental_path
from apps.leads.views import _client_ip

from .content import (CLUSTER_KEYS, CONTENT, GUIDE_KEYS, PAGE_KEYS, SECTOR_KEYS, alternates, fill, lang_links,
                      page_path, resolve)
from .forms import IntlLeadForm
from .notifications import notify_intl_lead
from .pricing import price_for

RATE_LIMIT, RATE_WINDOW = 5, 60 * 60

# Our live projects, captions come from ui[<key>].
WORK = [
    {"key": "work_linksterr", "name": "linksterr.com", "url": "https://linksterr.com/", "img": "img/works/linksterr.webp"},
    {"key": "work_dt", "name": "dentaltourism.tr", "url": "https://dentaltourism.tr/", "img": "img/works/dentaltourism.webp"},
    {"key": "work_clinic", "name": "drdevrim.com", "url": "https://drdevrim.com/", "img": "img/works/drdevrim.webp"},
]


def _base_context(code, key, form=None):
    price = price_for(code)
    data = fill(CONTENT[code], price=price["display"], currency=price["currency"])
    ui = data["ui"]
    path = page_path(code, key)
    if form is None:
        form = IntlLeadForm(initial={"interest": key.partition(":")[2] if key.startswith("cluster:") else "dijital-pazarlama-ajansi"})
        form.localize(ui)
    return {
        "L": LANG_BY_CODE[code],
        "key": key,
        "c": data,
        "ui": ui,
        "price": price,
        "form": form,
        "current_lang": LANG_BY_CODE[code],
        "lang_links": lang_links(key),
        "alternates": alternates(key),
        "canonical_url": settings.SITE_URL + path,
        "og_locale": LANG_BY_CODE[code].og_locale,
        "whatsapp_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(ui['wa_text'])}",
        "urls": {
            "home": page_path(code, "home"),
            "sectors": page_path(code, "sectors"),
            "guides": page_path(code, "guides"),
            "dental": dental_path(code, "hub"),
            "clusters": [(data["clusters"][k], page_path(code, f"cluster:{k}")) for k in CLUSTER_KEYS],
            "sector_list": [(data["sectors"][k], page_path(code, f"sector:{k}")) for k in SECTOR_KEYS],
            "guide_list": [(data["guides"][k], page_path(code, f"guide:{k}")) for k in GUIDE_KEYS],
        },
        "tiers": [(n, t, f, amount) for (n, t, f), amount in zip(ui["tiers"], price["tiers"])],
        "work": WORK,
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
    }


def _render(request, code, key, form=None, status=200):
    ctx = _base_context(code, key, form)
    data = ctx["c"]
    kind, _, slug = key.partition(":")
    if kind == "home":
        ctx.update(p=data["home"], faqs=data["home"]["faqs"], template="intl/home.html")
    elif kind == "cluster":
        ctx.update(p=data["clusters"][slug], faqs=data["clusters"][slug]["faqs"], template="intl/cluster.html",
                   others=[(cl, url) for cl, url in ctx["urls"]["clusters"] if cl is not data["clusters"][slug]])
    elif kind == "sectors":
        ctx.update(p=data["sectors_index"], faqs=None, template="intl/sectors.html")
    elif kind == "sector":
        ctx.update(p=data["sectors"][slug], faqs=data["sectors"][slug]["faqs"], template="intl/sector.html",
                   others=[(s, url) for s, url in ctx["urls"]["sector_list"] if s is not data["sectors"][slug]])
    elif kind == "guides":
        ctx.update(p=data["guides_index"], faqs=None, template="intl/guides.html")
    else:
        ctx.update(p=data["guides"][slug], faqs=data["guides"][slug]["faqs"], template="intl/guide.html",
                   others=[(g, url) for g, url in ctx["urls"]["guide_list"] if g is not data["guides"][slug]][:3])
    return render(request, ctx["template"], ctx, status=status)


def intl_page(request, lang, first=None, second=None):
    key = resolve(lang, first, second)
    if key is None:
        raise Http404
    return _render(request, lang, key)


@require_POST
def send(request):
    code = request.POST.get("lang")
    if code not in CONTENT:
        raise Http404
    key = request.POST.get("page_key")
    if key not in PAGE_KEYS:
        key = "home"
    ui = CONTENT[code]["ui"]
    thanks = f"{reverse('intl:thanks')}?lang={code}"
    with translation.override(LANG_BY_CODE[code].django):
        form = IntlLeadForm(request.POST).localize(ui)
        if form.is_spam():
            return redirect(thanks)
        ip = _client_ip(request)
        rate_key = f"intl-rate:{ip}"
        if cache.get(rate_key, 0) >= RATE_LIMIT:
            form.add_error(None, ui["err_rate"])
        if not form.errors and form.is_valid():
            price = price_for(code)
            lead = form.save(commit=False)
            lead.lang = code
            lead.ip = ip
            lead.quoted_price = price["display"]
            lead.usd_price = price["usd"]
            lead.source_page = request.POST.get("source_page", "")[:300]
            for field in ("utm_source", "utm_medium", "utm_campaign", "gclid"):
                setattr(lead, field, request.POST.get(field, "")[:150])
            lead.save()
            cache.set(rate_key, cache.get(rate_key, 0) + 1, RATE_WINDOW)
            lead.notified = notify_intl_lead(lead)
            lead.save(update_fields=["notified"])
            request.session["lead_event"] = {
                "lead_id": f"intl-{lead.pk}",
                "form_id": "intl_agency",
                "language": code,
                "lead_country": lead.country[:40],
                "service": lead.interest,
                "value": price["usd"],
                "currency": "USD",
            }
            return redirect(thanks)
        response = _render(request, code, key, form=form, status=400)
    return response


def thanks(request):
    code = request.GET.get("lang")
    if code not in CONTENT:
        raise Http404
    ctx = _base_context(code, "home")
    ctx.update(p=ctx["c"]["home"], lead_event=request.session.pop("lead_event", None))
    return render(request, "intl/thanks.html", ctx)
