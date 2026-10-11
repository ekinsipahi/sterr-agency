from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import translation
from django.views.decorators.http import require_POST

from apps.core.models import Testimonial
from apps.leads.views import _client_ip

from .forms import InquiryForm
from .languages import CONTENT, DEFAULT, LANG_BY_CODE, LANGS, PAGES, alternates, page_path, resolve
from .notifications import notify_inquiry

RATE_LIMIT, RATE_WINDOW = 5, 60 * 60
TEMPLATES = {"hub": "dental/hub.html", "partners": "dental/partners.html", "insurance": "dental/insurance.html"}
DEFAULT_KIND = {"hub": "patient", "partners": "clinic", "insurance": "patient"}

# Our own dental projects shown as proof on every language version.
WORK = [
    {"key": "dt", "name": "dentaltourism.tr", "url": "https://dentaltourism.tr/", "img": "img/works/dentaltourism.webp"},
    {"key": "clinic", "name": "drdevrim.com", "url": "https://drdevrim.com/", "img": "img/works/drdevrim.webp"},
]


def lang_links(page):
    """Language menu rows for `page`: (Lang, url). Shared with the Turkish main site."""
    return [(lang, page_path(lang.code, page)) for lang in LANGS]


def _context(request, code, page, form=None):
    data = CONTENT[code]
    ui = data["ui"]
    if form is None:
        form = InquiryForm(initial={"kind": DEFAULT_KIND[page]}).localize(ui)
    path = page_path(code, page)
    return {
        "L": LANG_BY_CODE[code],
        "page": page,
        "p": data[page],
        "ui": ui,
        "form": form,
        "lang_links": lang_links(page),
        "current_lang": LANG_BY_CODE[code],
        "alternates": alternates(page),
        "urls": {pg: page_path(code, pg) for pg in PAGES},
        "canonical_url": settings.SITE_URL + path,
        "og_locale": LANG_BY_CODE[code].og_locale,
        "whatsapp_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(ui['wa_text'])}",
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
        "work": WORK,
        "faqs": data[page]["faqs"],
    }


def dental_page(request, lang=None, slug=None):
    if lang == DEFAULT:
        found = resolve(DEFAULT, slug)
        if found:
            return redirect(page_path(*found), permanent=True)
    found = resolve(lang or DEFAULT, slug)
    if found is None:
        raise Http404
    code, page = found
    return render(request, TEMPLATES[page], _context(request, code, page))


@require_POST
def send(request):
    code = request.POST.get("lang")
    code = code if code in CONTENT else DEFAULT
    page = request.POST.get("page")
    page = page if page in PAGES else "hub"
    ui = CONTENT[code]["ui"]
    thanks = f"{reverse('dental:thanks')}?lang={code}"

    with translation.override(LANG_BY_CODE[code].django):
        form = InquiryForm(request.POST).localize(ui)
        if form.is_spam():
            return redirect(thanks)
        ip = _client_ip(request)
        key = f"dental-rate:{ip}"
        if cache.get(key, 0) >= RATE_LIMIT:
            form.add_error(None, ui["err_rate"])
        if not form.errors and form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.lang = code
            inquiry.ip = ip
            inquiry.source_page = request.POST.get("source_page", "")[:300]
            for field in ("utm_source", "utm_medium", "utm_campaign", "gclid"):
                setattr(inquiry, field, request.POST.get(field, "")[:150])
            inquiry.save()
            cache.set(key, cache.get(key, 0) + 1, RATE_WINDOW)
            inquiry.notified = notify_inquiry(inquiry)
            inquiry.save(update_fields=["notified"])
            request.session["lead_event"] = {
                "lead_id": f"dt-{inquiry.pk}",
                "form_id": f"dental_{inquiry.kind}",
                "lead_type": inquiry.kind,
                "language": code,
                "lead_country": inquiry.country[:40],
                "treatment": inquiry.treatment or "none",
            }
            return redirect(thanks)
        response = render(request, TEMPLATES[page], _context(request, code, page, form=form), status=400)
    return response


def thanks(request):
    code = request.GET.get("lang")
    code = code if code in CONTENT else DEFAULT
    ctx = _context(request, code, "hub")
    ctx["lead_event"] = request.session.pop("lead_event", None)
    return render(request, "dental/thanks.html", ctx)
