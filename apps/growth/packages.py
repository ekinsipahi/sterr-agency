"""One-time follower packages, the same on Instagram and TikTok. Delivery windows are
real: every follower is a real person, so bigger packages take longer."""
from decimal import Decimal

from django.utils import formats, translation

PACKAGES = (
    {"key": "1k", "followers": 1000, "price": Decimal("34.99"), "days": (7, 14)},
    {"key": "2k", "followers": 2000, "price": Decimal("59.99"), "days": (14, 24)},
    {"key": "3k", "followers": 3000, "price": Decimal("79.99"), "days": (24, 36), "popular": True},
    {"key": "5k", "followers": 5000, "price": Decimal("124.99"), "days": (30, 60)},
    {"key": "10k", "followers": 10000, "price": Decimal("229.99"), "days": (60, 120)},
)
PACKAGE_BY_KEY = {p["key"]: p for p in PACKAGES}
DEFAULT_PACKAGE = "3k"
CHOICES = [(p["key"], f"{p['followers']:,}") for p in PACKAGES]


def cents(package):
    return int(package["price"] * 100)


def count(n, code):
    """1000 -> '1,000' / '1.000' / '1 000' in the page language."""
    with translation.override("nb" if code == "no" else code):
        return formats.number_format(n, use_l10n=True, force_grouping=True)


def money(amount):
    return f"${amount:.2f}"


def for_page(code):
    """Packages with display strings for one language."""
    out = []
    for p in PACKAGES:
        out.append({**p, "count": count(p["followers"], code), "amount": money(p["price"]),
                    "per_1k": money(p["price"] * 1000 / p["followers"]), "value": f"{p['price']:.2f}"})
    return out
