"""The 16 site languages. Turkish = the main site at /, the other 15 have their own
international pages (/<code>/) and dental tourism pages (/dental-tourism/<code>/).

Only the follower pages (Instagram, TikTok, YouTube) are public in every language they are
written in. Everything else (agency, dental tourism, the creators hub) is public in Turkish
and the languages of settings.AGENCY_LANGS: is_public(). The other languages' URLs redirect
to the English page; their content stays in the repo, so a language comes back with the setting."""
from dataclasses import dataclass

from django.conf import settings


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
DEFAULT = "en"  # x-default
LANG_BY_CODE = {lang.code: lang for lang in LANGS}
INTL_CODES = [lang.code for lang in LANGS if lang.code != "tr"]


def is_public(code):
    """Whether the agency, dental tourism and creators pages are public in this language."""
    return code == "tr" or code in settings.AGENCY_LANGS


def public_langs():
    """The languages of is_public(), in menu order."""
    return [lang for lang in LANGS if is_public(lang.code)]
