"""Real-follower package pages (Instagram and TikTok) in 16 languages.

    apps/growth/i18n/<code>.py               UI: forms, packages, account, shared blocks ({platform} placeholders)
    apps/growth/pages/<platform>/<code>.py   DATA: slugs and the copy of every page in PAGES (+ geo:<key>)
    apps/growth/pages/creators/<code>.py     DATA: the "influencer agency for creators" hub (CREATOR_PAGES)

Turkish lives at the site root, the other languages under /<code>/. The main page is the
hub: it links to every other page of its platform, and they all link back.
"""
from importlib import import_module

from apps.core.languages import DEFAULT, LANGS

from .constants import ACCOUNT_NAV, CREATOR_PAGES, FOLLOWERS_NAV, GUIDES, PACKAGE_PAGES, PAGES, PLATFORM_NAMES, PLATFORMS, PROFILE_URL  # noqa: F401

UI = {}
CONTENT = {platform: {} for platform in PLATFORMS}
CREATORS = {}
for _lang in LANGS:
    try:
        UI[_lang.code] = import_module(f"apps.growth.i18n.{_lang.code}").UI
    except ModuleNotFoundError:
        continue
    for _platform in PLATFORMS:
        try:
            CONTENT[_platform][_lang.code] = import_module(f"apps.growth.pages.{_platform}.{_lang.code}").DATA
        except ModuleNotFoundError:
            pass
    try:
        CREATORS[_lang.code] = import_module(f"apps.growth.pages.creators.{_lang.code}").DATA
    except ModuleNotFoundError:
        pass


def ui_for(code, platform):
    """UI strings with {platform} filled in."""
    name = PLATFORM_NAMES[platform]

    def fill(value):
        if isinstance(value, str):
            return value.replace("{platform}", name)
        if isinstance(value, (list, tuple)):
            return type(value)(fill(v) for v in value)
        return value

    return {k: fill(v) for k, v in UI[code].items()}


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
    return alts + [("x-default", page_path(DEFAULT, page, platform))] if DEFAULT in CONTENT[platform] else alts


def lang_links(page, platform="instagram"):
    target = "main" if page.startswith("geo:") else page
    return [(lang, page_path(lang.code, target, platform)) for lang in LANGS if lang.code in CONTENT[platform]]


def creator_path(code, page):
    data = CREATORS[code]
    prefix = "" if code == "tr" else f"/{code}"
    if page == "main":
        return f"{prefix}/{data['base']}/"
    return f"{prefix}/{data['base']}/{data['subs'][page]}/"


def creator_routes():
    """(path without leading slash, lang, page) for the creators hub."""
    return [(creator_path(code, page)[1:], code, page) for code in CREATORS for page in CREATOR_PAGES]


def creator_alternates(page):
    alts = [(lang.code, creator_path(lang.code, page)) for lang in LANGS if lang.code in CREATORS]
    return alts + [("x-default", creator_path(DEFAULT, page))] if DEFAULT in CREATORS else alts


def followers_menu(code):
    """[(label, url)] for the navbar 'Followers' dropdown: both platforms, creators, then the account."""
    from django.urls import reverse

    items = [(PLATFORM_NAMES[p], page_path(code, "main", p)) for p in PLATFORMS if code in CONTENT[p]]
    if code in CREATORS:
        items.append((CREATORS[code]["nav"], creator_path(code, "main")))
    if items:
        items.append((ACCOUNT_NAV.get(code, ACCOUNT_NAV["en"]), f"{reverse('growth:account')}?lang={code}"))
    return items
