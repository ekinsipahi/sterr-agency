from urllib.parse import quote

from django.conf import settings

from .company import COMPANY
from .models import SiteSettings

WHATSAPP_TEXT = "Merhaba Sterr Agency, işletmem için müşteri kazanımı hakkında görüşmek istiyorum."


def site(request):
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
    }
