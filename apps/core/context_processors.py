from urllib.parse import quote

from django.conf import settings

from apps.core.languages import LANG_BY_CODE
from apps.intl.content import CLUSTER_KEYS, GUIDE_KEYS, SECTOR_KEYS, alternates, lang_links

from .company import COMPANY
from .models import SiteSettings

WHATSAPP_TEXT = "Merhaba Sterr Agency, işletmem için müşteri kazanımı hakkında görüşmek istiyorum."


def site(request):
    key = _page_key(request)
    return {
        "site": SiteSettings.load(),
        "company": COMPANY,
        "SITE_URL": settings.SITE_URL,
        "canonical_url": settings.SITE_URL + request.path,
        "whatsapp_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(WHATSAPP_TEXT)}",
        "whatsapp_display": settings.WHATSAPP_DISPLAY,
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "phone_tel": "+" + settings.WHATSAPP_NUMBER,
        "contact_email": settings.CONTACT_EMAIL,
        "GA4_ID": settings.GA4_ID,
        "GTM_ID": settings.GTM_ID,
        "META_PIXEL_ID": settings.META_PIXEL_ID,
        "GOOGLE_SITE_VERIFICATION": settings.GOOGLE_SITE_VERIFICATION,
        # Language menu + hreflang on the Turkish site. Pages with an equivalent in the
        # other 15 languages link to it; everything else falls back to the home pages.
        "current_lang": LANG_BY_CODE["tr"],
        "lang_links": lang_links(key or "home"),
        "alternates": alternates(key) if key else [],
    }


def _page_key(request):
    """Shared page key (see apps.intl.content) of a Turkish page, or None."""
    match = getattr(request, "resolver_match", None)
    if match is None:
        return None
    name, kw = match.view_name, match.kwargs
    if name == "core:home":
        return "home"
    if name == "seo:cluster" and kw.get("cluster") in CLUSTER_KEYS:
        return f"cluster:{kw['cluster']}"
    if name == "seo:sectors":
        return "sectors"
    if name == "seo:sector" and kw.get("slug") in SECTOR_KEYS:
        return f"sector:{kw['slug']}"
    if name == "seo:guides":
        return "guides"
    if name == "seo:guide" and kw.get("slug") in GUIDE_KEYS:
        return f"guide:{kw['slug']}"
    return None
