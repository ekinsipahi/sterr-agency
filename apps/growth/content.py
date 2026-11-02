"""Organic follower growth pages (Instagram and TikTok) in 16 languages.

Page keys: main · pricing · guide_buy · guide_speed, plus geo:<key> (Instagram, English only).
Turkish lives at the site root, the other languages under /<code>/.
TikTok locales hold only what differs from the Instagram content of the same language;
everything else (form, payment, cancellation texts) is inherited.
"""
from importlib import import_module

from apps.core.languages import DEFAULT, LANGS

PLATFORMS = ("instagram", "tiktok")
PLATFORM_NAMES = {"instagram": "Instagram", "tiktok": "TikTok"}
PROFILE_URL = {"instagram": "https://www.instagram.com/{}/", "tiktok": "https://www.tiktok.com/@{}"}
PAGES = ("main", "pricing", "guide_buy", "guide_speed")

# Navbar dropdown label for both platforms.
FOLLOWERS_NAV = {
    "en": "Followers", "tr": "Takipçi", "de": "Follower", "nl": "Volgers", "fr": "Abonnés", "it": "Follower",
    "es": "Seguidores", "pl": "Obserwujący", "ru": "Подписчики", "uk": "Підписники", "ar": "متابعين",
    "sv": "Följare", "da": "Følgere", "no": "Følgere", "ro": "Urmăritori", "az": "İzləyici",
}


def _merge(base, over):
    out = dict(base)
    for key, value in over.items():
        out[key] = {**base[key], **value} if isinstance(value, dict) and isinstance(base.get(key), dict) else value
    return out


CONTENT = {platform: {} for platform in PLATFORMS}
for _lang in LANGS:
    try:
        _ig = import_module(f"apps.growth.locales.{_lang.code}").DATA
    except ModuleNotFoundError:
        continue
    CONTENT["instagram"][_lang.code] = _ig
    try:
        _tt = import_module(f"apps.growth.tiktok.{_lang.code}").DATA
    except ModuleNotFoundError:
        continue
    _base = {k: v for k, v in _ig.items() if k != "geo"}
    CONTENT["tiktok"][_lang.code] = _merge(_base, _tt)


def page_path(code, page, platform="instagram"):
    data = CONTENT[platform][code]
    prefix = "" if code == "tr" else f"/{code}"
    kind, _, geo = page.partition(":")
    if kind == "main":
        return f"{prefix}/{data['base']}/"
    if kind == "geo":
        return f"{prefix}/{data['base']}/{geo}/"
    return f"{prefix}/{data['base']}/{data['subs'][kind]}/"


def routes():
    """(path without leading slash, lang, page, platform) for every growth page."""
    out = []
    for platform in PLATFORMS:
        for code, data in CONTENT[platform].items():
            for page in PAGES:
                out.append((page_path(code, page, platform)[1:], code, page, platform))
            for geo in data.get("geo", {}):
                out.append((page_path(code, f"geo:{geo}", platform)[1:], code, f"geo:{geo}", platform))
    return out


def alternates(page, platform="instagram"):
    """hreflang set: core pages exist in every language; geo pages only in English."""
    if page.startswith("geo:"):
        return []
    alts = [(lang.code, page_path(lang.code, page, platform)) for lang in LANGS if lang.code in CONTENT[platform]]
    return alts + [("x-default", page_path(DEFAULT, page, platform))]


def lang_links(page, platform="instagram"):
    target = "main" if page.startswith("geo:") else page
    return [(lang, page_path(lang.code, target, platform)) for lang in LANGS if lang.code in CONTENT[platform]]


def followers_menu(code):
    """[(label, url)] for the navbar 'Followers' dropdown."""
    return [(PLATFORM_NAMES[p], page_path(code, "main", p)) for p in PLATFORMS if code in CONTENT[p]]
