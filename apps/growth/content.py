"""Organic Instagram growth product pages in 16 languages.

Page keys: main · pricing · guide_buy · guide_speed, plus geo:<key> (English only).
Turkish lives at the site root, the other languages under /<code>/.
"""
from importlib import import_module

from apps.core.languages import DEFAULT, LANGS

CONTENT = {}
for _lang in LANGS:
    try:
        CONTENT[_lang.code] = import_module(f"apps.growth.locales.{_lang.code}").DATA
    except ModuleNotFoundError:
        pass

PAGES = ("main", "pricing", "guide_buy", "guide_speed")
GEO_KEYS = tuple(CONTENT.get("en", {}).get("geo", {}))


def page_path(code, page):
    data = CONTENT[code]
    prefix = "" if code == "tr" else f"/{code}"
    kind, _, geo = page.partition(":")
    if kind == "main":
        return f"{prefix}/{data['base']}/"
    if kind == "geo":
        return f"{prefix}/{data['base']}/{geo}/"
    return f"{prefix}/{data['base']}/{data['subs'][kind]}/"


def routes():
    """(path without leading slash, lang, page) for every growth page."""
    out = []
    for code in CONTENT:
        for page in PAGES:
            out.append((page_path(code, page)[1:], code, page))
        for geo in CONTENT[code].get("geo", {}):
            out.append((page_path(code, f"geo:{geo}")[1:], code, f"geo:{geo}"))
    return out


def alternates(page):
    """hreflang set: the four core pages exist in every language; geo pages only in English."""
    if page.startswith("geo:"):
        return []
    alts = [(lang.code, page_path(lang.code, page)) for lang in LANGS if lang.code in CONTENT]
    return alts + [("x-default", page_path(DEFAULT, page))]


def lang_links(page):
    target = "main" if page.startswith("geo:") else page
    return [(lang, page_path(lang.code, target)) for lang in LANGS if lang.code in CONTENT]
