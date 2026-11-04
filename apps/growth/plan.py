"""The influencer packages: monthly subscriptions, the same on Instagram and TikTok, each
spread over 30 days. Real people choose to follow, so the numbers are typical monthly
ranges, never a count we promise. The base: 1,000–4,000 followers a month, 2–3 likes per
new follower, about one comment per 10 new followers; bigger packages scale that up."""
from decimal import Decimal

from django.utils import formats, translation

LIKES_PER_FOLLOWER = (2, 3)
FOLLOWERS_PER_COMMENT = 10
# Everything is counted from the followers we bring: a day's likes and comments, unless
# the growth system sends them, are its new followers × the middle of 2–3, and ÷ 10.
LIKES_PER_FOLLOWER_AVG = 2.5


def likes_for(followers):
    return round(followers * LIKES_PER_FOLLOWER_AVG)


def comments_for(followers):
    return round(followers / FOLLOWERS_PER_COMMENT)


PLANS = (
    {"key": "starter", "price": Decimal("79.99"), "followers": (1000, 4000)},
    {"key": "rising", "price": Decimal("149.99"), "followers": (2000, 8000), "popular": True},
    {"key": "pro", "price": Decimal("279.99"), "followers": (4000, 16000)},
)
for _p in PLANS:
    low, high = _p["followers"]
    _p["likes"] = (low * LIKES_PER_FOLLOWER[0], high * LIKES_PER_FOLLOWER[1])
    _p["comments"] = (low // FOLLOWERS_PER_COMMENT, high // FOLLOWERS_PER_COMMENT)
del _p, low, high
PLAN_BY_KEY = {p["key"]: p for p in PLANS}
DEFAULT_PLAN = "rising"
NAMES = {"starter": "Starter Creator", "rising": "Rising Influencer", "pro": "Pro Influencer"}
CHOICES = [(p["key"], NAMES[p["key"]]) for p in PLANS]
LOWEST = PLANS[0]["price"]


def cents(p):
    return int(p["price"] * 100)


def count(n, code):
    """1000 -> '1,000' / '1.000' / '1 000' in the page language."""
    with translation.override("nb" if code == "no" else code):
        return formats.number_format(n, use_l10n=True, force_grouping=True)


def span(pair, code):
    return f"{count(pair[0], code)}–{count(pair[1], code)}"


def money(amount):
    return f"${amount:.2f}"


def for_page(code, ui):
    """The packages with their display strings for one language (ui: that language's UI)."""
    out = []
    for p in PLANS:
        ranges = {name: span(p[name], code) for name in ("followers", "likes", "comments")}

        def fill(text, ranges=ranges):
            for name, value in ranges.items():
                text = text.replace("{" + name + "}", value)
            return text

        out.append({**p, **ranges, "name": ui[f"plan_{p['key']}"], "for": ui[f"plan_{p['key']}_for"],
                    "amount": money(p["price"]), "value": f"{p['price']:.2f}",
                    "items": [fill(t) for t in ui["plan_items"]] + list(ui.get(f"plan_{p['key']}_extra", [])),
                    "headline": fill(ui["plan_followers"])})
    return out
