"""The 16 languages of the /dental-tourism/ cluster.

English is the x-default and lives at /dental-tourism/; every other language at
/dental-tourism/<code>/. Order = order in the language menu.
"""
from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True)
class Lang:
    code: str           # URL prefix + hreflang
    name: str           # native name shown in the menu
    og_locale: str
    django: str         # Django locale used for form error messages
    rtl: bool = False

    @property
    def flag(self):
        return f"img/flags/{self.code}.png"

    @property
    def flag_2x(self):
        return f"img/flags/{self.code}@2x.png"


LANGS = [
    Lang("en", "English", "en_GB", "en"),
    Lang("de", "Deutsch", "de_DE", "de"),
    Lang("nl", "Nederlands", "nl_NL", "nl"),
    Lang("fr", "Français", "fr_FR", "fr"),
    Lang("it", "Italiano", "it_IT", "it"),
    Lang("es", "Español", "es_ES", "es"),
    Lang("pl", "Polski", "pl_PL", "pl"),
    Lang("ru", "Русский", "ru_RU", "ru"),
    Lang("uk", "Українська", "uk_UA", "uk"),
    Lang("ar", "العربية", "ar_AR", "ar", rtl=True),
    Lang("sv", "Svenska", "sv_SE", "sv"),
    Lang("da", "Dansk", "da_DK", "da"),
    Lang("no", "Norsk", "nb_NO", "nb"),
    Lang("ro", "Română", "ro_RO", "ro"),
    Lang("az", "Azərbaycanca", "az_AZ", "az"),
    Lang("tr", "Türkçe", "tr_TR", "tr"),
]
DEFAULT = "en"
LANG_BY_CODE = {lang.code: lang for lang in LANGS}
PAGES = ("hub", "partners", "insurance")

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
