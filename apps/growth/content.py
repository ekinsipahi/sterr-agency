"""Real-follower package pages: Instagram and TikTok in 16 languages, YouTube in English.

    apps/growth/i18n/<code>.py               UI: forms, packages, account, shared blocks ({platform} placeholders);
                                             YOUTUBE = {...} there replaces the strings that differ on YouTube
                                             (subscribers, channel, the video link field)
    apps/growth/pages/<platform>/<code>.py   DATA: slugs and the copy of every page in PAGES (+ geo:<key>);
                                             a platform may have its own shorter page list (constants.PLATFORM_PAGES)
    apps/growth/pages/creators/<code>.py     DATA: the "influencer agency for creators" hub (CREATOR_PAGES)

Turkish lives at the site root, the other languages under /<code>/. The main page is the
hub: it links to every other page of its platform, and they all link back.

The follower pages are public in every language they are written in. The creators hub is an
agency page: public only in the languages of apps.core.languages.is_public(); its URLs in the
other languages redirect to the English page (views.creators).
"""
from importlib import import_module

from apps.core.languages import DEFAULT, LANGS, is_public, public_langs

from .constants import (ACCOUNT_NAV, AUDIENCE, CREATOR_PAGES, FOLLOWERS_NAV, GROUPS, GUIDES, PACKAGE_PAGES, PAGE_PLAN, PAGES,  # noqa: F401
                        PLATFORM_NAMES, PLATFORMS, PROFILE_URL, has_language, pages_for)

UI = {}
PLATFORM_UI = {platform: {} for platform in PLATFORMS}   # {platform: {lang: the UI strings that differ on it}}
CONTENT = {platform: {} for platform in PLATFORMS}
CREATORS = {}
for _lang in LANGS:
    try:
        _module = import_module(f"apps.growth.i18n.{_lang.code}")
    except ModuleNotFoundError:
        continue
    UI[_lang.code] = _module.UI
    for _platform in PLATFORMS:
        if getattr(_module, _platform.upper(), None):
            PLATFORM_UI[_platform][_lang.code] = getattr(_module, _platform.upper())
        try:
            CONTENT[_platform][_lang.code] = import_module(f"apps.growth.pages.{_platform}.{_lang.code}").DATA
        except ModuleNotFoundError:
            pass
    try:
        CREATORS[_lang.code] = import_module(f"apps.growth.pages.creators.{_lang.code}").DATA
    except ModuleNotFoundError:
        pass


def ui_for(code, platform):
    """UI strings with {platform} filled in, and the platform's own wording where the language
    has it (YouTube: subscribers). A language without it keeps its general strings."""
    name = PLATFORM_NAMES[platform]

    def fill(value):
        if isinstance(value, str):
            return value.replace("{platform}", name)
        if isinstance(value, (list, tuple)):
            return type(value)(fill(v) for v in value)
        return value

    # English fills any key a language doesn't have yet (the copy check reports it).
    return {k: fill(v) for k, v in {**UI["en"], **UI[code], **PLATFORM_UI[platform].get(code, {})}.items()}


def has_page(code, page, platform="instagram"):
    """Whether a language has this page (new pages go live per language as they're translated)."""
    data = CONTENT[platform].get(code)
    kind, _, geo = page.partition(":")
    if data is None:
        return False
    if kind == "geo":
        return geo in data.get("geo", {})
    return kind == "main" or (kind in data.get("subs", {}) and kind in data)


def page_path(code, page, platform="instagram"):
    data = CONTENT[platform][code]
    prefix = "" if code == "tr" else f"/{code}"
    kind, _, geo = page.partition(":")
    if kind == "main":
        return f"{prefix}/{data['base']}/"
    if kind == "geo":
        return f"{prefix}/{data['base']}/{geo}/"
    sub = data["subs"][kind]
    if sub.startswith("/"):  # a page of its own, outside the followers section
        return f"{prefix}{sub}"
    return f"{prefix}/{data['base']}/{sub}/"


def routes():
    """(path without leading slash, lang, page, platform) for every growth page."""
    out = []
    for platform in PLATFORMS:
        for code, data in CONTENT[platform].items():
            for page in PAGES:
                if has_page(code, page, platform):
                    out.append((page_path(code, page, platform)[1:], code, page, platform))
            for geo in data.get("geo", {}):
                out.append((page_path(code, f"geo:{geo}", platform)[1:], code, f"geo:{geo}", platform))
    return out


def alternates(page, platform="instagram"):
    """hreflang set: core pages exist in every language; geo pages only in English."""
    if page.startswith("geo:"):
        return []
    alts = [(lang.code, page_path(lang.code, page, platform)) for lang in LANGS if has_page(lang.code, page, platform)]
    return alts + [("x-default", page_path(DEFAULT, page, platform))] if has_page(DEFAULT, page, platform) else alts


def lang_links(page, platform="instagram"):
    target = "main" if page.startswith("geo:") else page
    return [(lang, page_path(lang.code, target if has_page(lang.code, target, platform) else "main", platform))
            for lang in LANGS if lang.code in CONTENT[platform]]


def creator_path(code, page):
    data = CREATORS[code]
    prefix = "" if code == "tr" else f"/{code}"
    if page == "main":
        return f"{prefix}/{data['base']}/"
    return f"{prefix}/{data['base']}/{data['subs'][page]}/"


def creator_routes():
    """(path without leading slash, lang, page) for the creators hub."""
    return [(creator_path(code, page)[1:], code, page) for code in CREATORS for page in CREATOR_PAGES]


def creator_lang_links(page):
    """Language menu rows (Lang, url) of a creators page: the public languages only."""
    return [(lang, creator_path(lang.code, page)) for lang in public_langs() if lang.code in CREATORS]


def creator_alternates(page):
    alts = [(lang.code, url) for lang, url in creator_lang_links(page)]
    return alts + [("x-default", creator_path(DEFAULT, page))] if DEFAULT in CREATORS else alts


def platform_home(code, platform):
    """(language, url) of a platform's hub for a visitor in `code`: their language when the
    platform has pages in it, else English; None when it has neither."""
    for lang in (code, DEFAULT):
        if lang in CONTENT[platform]:
            return lang, page_path(lang, "main", platform)
    return None


def followers_menu(code):
    """[(label, url)] for the navbar 'Followers' dropdown: per platform followers, packages, likes,
    views and comments; then creators and the account. A platform this language has no pages
    for (YouTube outside English) gets one link to its English hub."""
    from django.urls import reverse

    items = []
    for p in PLATFORMS:
        if code in CONTENT[p]:
            data = CONTENT[p][code]
            items.append((data["nav"], page_path(code, "main", p)))
            navs = data.get("navs", {})
            items += [(navs[page], page_path(code, page, p)) for page in ("packages", "likes", "views", "comments")
                      if page in navs and has_page(code, page, p)]
        elif DEFAULT in CONTENT[p]:
            items.append((f"{PLATFORM_NAMES[p]} (EN)", page_path(DEFAULT, "main", p)))
    if code in CREATORS and is_public(code):
        items.append((CREATORS[code]["nav"], creator_path(code, "main")))
    if items:
        items.append((ACCOUNT_NAV.get(code, ACCOUNT_NAV["en"]), f"{reverse('growth:account')}?lang={code}"))
    return items
