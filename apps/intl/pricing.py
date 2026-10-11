"""Country pricing: a USD price per market, shown in the local currency.

Rates come from open.er-api.com (free, daily, no key) and are stored in FxRate.
They refresh at most once a day, in a background thread so no visitor waits;
`python manage.py update_fx_rates` does the same from cron. If the API is down
the last stored rate is used, and before the first fetch the fallback below.
"""
import logging
import sys
import threading
from datetime import timedelta
from decimal import Decimal

import requests
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

FX_URL = "https://open.er-api.com/v6/latest/USD"
MAX_AGE = timedelta(hours=24)
TIER_MULTIPLIERS = (1, 1.8, 3)  # same ratios as the Turkish packages (50K / 90K / 150K+)

# lang: (country, currency, usd_price). 900 USD for economically harder markets.
DEFAULT_MARKETS = {
    "en": ("International (US, UK, …)", "USD", 1000),
    "de": ("Deutschland, Österreich, Schweiz", "EUR", 1000),
    "nl": ("Nederland, België", "EUR", 1000),
    "fr": ("France, Belgique", "EUR", 1000),
    "it": ("Italia", "EUR", 1000),
    "es": ("España", "EUR", 1000),
    "pl": ("Polska", "PLN", 900),
    "ru": ("Россия", "RUB", 900),
    "uk": ("Україна", "UAH", 900),
    "ar": ("Gulf / Arab countries", "SAR", 1000),
    "sv": ("Sverige", "SEK", 1000),
    "da": ("Danmark", "DKK", 1000),
    "no": ("Norge", "NOK", 1000),
    "ro": ("România", "RON", 900),
    "az": ("Azərbaycan", "AZN", 900),
}

# Approximate rates used only until the first successful fetch.
FALLBACK_RATES = {
    "USD": 1, "EUR": 0.86, "PLN": 3.65, "RUB": 80, "UAH": 41.5, "SAR": 3.75,
    "SEK": 9.5, "DKK": 6.4, "NOK": 10.1, "RON": 4.35, "AZN": 1.7,
}

# lang: (thousands separator, prefix, suffix)
NBSP = " "
FORMATS = {
    "en": (",", "$", ""), "de": (".", "", f"{NBSP}€"), "nl": (".", f"€{NBSP}", ""), "fr": (NBSP, "", f"{NBSP}€"),
    "it": (".", "", f"{NBSP}€"), "es": (".", "", f"{NBSP}€"), "pl": (NBSP, "", f"{NBSP}zł"),
    "ru": (NBSP, "", f"{NBSP}₽"), "uk": (NBSP, "", f"{NBSP}₴"), "ar": (",", "", f"{NBSP}ر.س"),
    "sv": (NBSP, "", f"{NBSP}kr"), "da": (".", "", f"{NBSP}kr."), "no": (NBSP, "", f"{NBSP}kr"),
    "ro": (".", "", f"{NBSP}lei"), "az": (NBSP, "", f"{NBSP}₼"),
}


def nice_round(value):
    """Round to two significant steps: 862 → 860, 3_694 → 3_700, 85_312 → 85_500."""
    value = float(value)
    if value < 100:
        return int(round(value))
    step = 10 ** (len(str(int(value))) - 2) / 2
    return int(round(value / step) * step)


def fmt(lang, amount):
    sep, prefix, suffix = FORMATS.get(lang, (",", "", ""))
    return f"{prefix}{amount:,}".replace(",", sep) + suffix


def _fetch_rates():
    from .models import FxRate

    try:
        data = requests.get(FX_URL, timeout=6).json()
        rates = data["rates"]
    except Exception:
        logger.warning("FX rate fetch failed; keeping stored rates", exc_info=True)
        return False
    wanted = {cur for _, cur, _ in DEFAULT_MARKETS.values()} | set(FALLBACK_RATES)
    for cur in wanted:
        if cur in rates:
            FxRate.objects.update_or_create(currency=cur, defaults={"rate": Decimal(str(rates[cur]))})
    cache.delete("fx_rates")
    return True


def refresh_rates(force=False):
    """Fetch new rates if the stored ones are older than a day. Returns True if fetched."""
    from .models import FxRate

    latest = FxRate.objects.order_by("-updated_at").values_list("updated_at", flat=True).first()
    if not force and latest and timezone.now() - latest < MAX_AGE:
        return False
    return _fetch_rates()


def _maybe_refresh_in_background():
    if "test" in sys.argv or not cache.add("fx_refresh_lock", 1, 60 * 30):
        return
    threading.Thread(target=refresh_rates, daemon=True).start()


def rates():
    cached = cache.get("fx_rates")
    if cached is not None:
        return cached
    from .models import FxRate

    stored = {r.currency: float(r.rate) for r in FxRate.objects.all()}
    result = {**FALLBACK_RATES, **stored}
    cache.set("fx_rates", result, 60 * 60)
    _maybe_refresh_in_background()
    return result


def market(lang):
    from .models import Market

    m = Market.objects.filter(pk=lang).first()
    if m:
        return m.country, m.currency, m.usd_price
    return DEFAULT_MARKETS[lang]


def price_for(lang):
    """Starting price and the three tiers for a language market, in local currency."""
    _, currency, usd = market(lang)
    rate = rates().get(currency, FALLBACK_RATES.get(currency, 1))
    amounts = [nice_round(usd * m * rate) for m in TIER_MULTIPLIERS]
    return {
        "currency": currency,
        "usd": usd,
        "amount": amounts[0],
        "display": fmt(lang, amounts[0]),
        "tiers": [fmt(lang, a) for a in amounts],
    }
