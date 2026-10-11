"""The 16 languages of the /dental-tourism/ cluster.

English is the x-default and lives at /dental-tourism/; every other language at
/dental-tourism/<code>/. Order = order in the language menu.
"""
from importlib import import_module

from apps.core.languages import DEFAULT, LANG_BY_CODE, LANGS, Lang  # noqa: F401

PAGES = ("hub", "partners")

# Content lives in apps/dental/locales/<code>.py as DATA = {...}
CONTENT = {lang.code: import_module(f"apps.dental.locales.{lang.code}").DATA for lang in LANGS}


def page_path(code, page):
    """URL path of `page` in language `code`."""
    base = "/dental-tourism/" if code == DEFAULT else f"/dental-tourism/{code}/"
    if page == "hub":
        return base
    return f"{base}{CONTENT[code]['slugs'][page]}/"


def resolve(code, slug):
    """(code, page) for a URL, or None."""
    if code not in CONTENT:
        return None
    if not slug:
        return code, "hub"
    for page, s in CONTENT[code]["slugs"].items():
        if s == slug:
            return code, page
    return None


def alternates(page):
    """[(hreflang, path)] for every language version of `page`, plus x-default."""
    alts = [(lang.code, page_path(lang.code, page)) for lang in LANGS]
    return alts + [("x-default", page_path(DEFAULT, page))]
