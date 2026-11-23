"""International agency pages: content loading, URLs and hreflang.

Page keys are shared with the Turkish site so every page links to its equivalent
in the other languages:
    home · cluster:<tr-slug> · sectors · sector:<tr-slug> · guides · guide:<tr-slug> · about
Turkish versions are the existing Turkish pages; the other languages live under
/<code>/ with localized slugs from apps/intl/locales/<code>.py.

Only the languages in settings.AGENCY_LANGS (plus Turkish) are public: active_codes(). The
content of the other languages stays loaded, because their follower pages use its menus and
their old URLs must resolve to a page key to redirect to the English page.
"""
from importlib import import_module

from django.conf import settings

from apps.core.languages import DEFAULT, INTL_CODES, LANGS

from .about import ABOUT

CONTENT = {code: import_module(f"apps.intl.locales.{code}").DATA for code in INTL_CODES}
for _code, _data in CONTENT.items():
    _data["about"] = ABOUT[_code]
    _data["slugs"]["about"] = ABOUT[_code]["slug"]
    _data["ui"]["nav_about"] = ABOUT[_code]["nav"]

CLUSTER_KEYS = ("dijital-pazarlama-ajansi", "sosyal-medya-ajansi", "sosyal-medya-yonetimi-ajansi", "dijital-pazarlama-uzmani")
SECTOR_KEYS = ("ozel-ders-ogretmenleri", "matematik-ogretmenleri", "fizik-ogretmenleri", "e-ticaret",
               "klinik-ve-saglik", "profesyonel-hizmetler")
GUIDE_KEYS = ("dijital-pazarlama-ajansi-ne-is-yapar", "dijital-pazarlama-ajansi-fiyatlari", "sosyal-medya-ajansi-nedir",
              "sosyal-medya-ajansi-fiyatlari", "sosyal-medya-ajans-sozlesmesi", "dijital-pazarlama-uzmani-nedir")
PAGE_KEYS = (["home"] + [f"cluster:{k}" for k in CLUSTER_KEYS] + ["sectors"] + [f"sector:{k}" for k in SECTOR_KEYS]
             + ["guides"] + [f"guide:{k}" for k in GUIDE_KEYS] + ["about"])


def _tr_path(key):
    kind, _, slug = key.partition(":")
    return {
        "home": "/",
        "cluster": f"/{slug}/",
        "sectors": "/sektorler/",
        "sector": f"/sektorler/{slug}/",
        "guides": "/rehber/",
        "guide": f"/rehber/{slug}/",
        "about": "/hakkimizda/",
    }[kind]


def page_path(code, key):
    if code == "tr":
        return _tr_path(key)
    c = CONTENT[code]
    kind, _, slug = key.partition(":")
    if kind == "home":
        return f"/{code}/"
    if kind == "cluster":
        return f"/{code}/{c['clusters'][slug]['slug']}/"
    if kind in ("sectors", "guides", "about"):
        return f"/{code}/{c['slugs'][kind]}/"
    group = "sectors" if kind == "sector" else "guides"
    return f"/{code}/{c['slugs'][group]}/{c[group][slug]['slug']}/"


def active_codes():
    """The /<code>/ languages whose agency pages are public (settings.AGENCY_LANGS)."""
    return [code for code in INTL_CODES if code in settings.AGENCY_LANGS]


def is_active(code):
    """Whether the agency pages are public in this language (Turkish is the main site)."""
    return code == "tr" or code in settings.AGENCY_LANGS


def alternates(key):
    """[(hreflang, path)] for the public languages plus x-default (English)."""
    return ([(lang.code, page_path(lang.code, key)) for lang in LANGS if is_active(lang.code)]
            + [("x-default", page_path(DEFAULT, key))])


def lang_links(key):
    """Language menu rows (Lang, url) pointing at the same page in every public language."""
    return [(lang, page_path(lang.code, key)) for lang in LANGS if is_active(lang.code)]


def resolve(code, first=None, second=None):
    """Page key for /<code>/<first>/<second>/, or None."""
    c = CONTENT.get(code)
    if c is None:
        return None
    if first is None:
        return "home"
    if second is None:
        for key, cl in c["clusters"].items():
            if cl["slug"] == first:
                return f"cluster:{key}"
        for kind in ("sectors", "guides", "about"):
            if c["slugs"][kind] == first:
                return kind
        return None
    for kind, group in (("sector", "sectors"), ("guide", "guides")):
        if c["slugs"][group] == first:
            for key, item in c[group].items():
                if item["slug"] == second:
                    return f"{kind}:{key}"
    return None


def fill(value, **kw):
    """Deep-replace {price}-style placeholders in locale content."""
    if isinstance(value, str):
        for k, v in kw.items():
            value = value.replace("{" + k + "}", str(v))
        return value
    if isinstance(value, dict):
        return {k: fill(v, **kw) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(fill(v, **kw) for v in value)
    return value
