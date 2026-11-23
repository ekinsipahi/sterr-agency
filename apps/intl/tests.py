import re
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings

from apps.core.languages import INTL_CODES

from .content import CONTENT, PAGE_KEYS, active_codes, alternates, page_path, resolve
from .models import FxRate, IntlLead, Market
from .pricing import fmt, nice_round, price_for


def shape(value):
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [shape(v) for v in value]
    return type(value).__name__


def meta_pages(data):
    yield data["home"]
    yield data["sectors_index"]
    yield data["guides_index"]
    yield data["about"]
    for group in ("clusters", "sectors", "guides"):
        yield from data[group].values()


class ContentTests(TestCase):
    def test_fifteen_languages_same_structure_as_english(self):
        self.assertEqual(len(INTL_CODES), 15)
        reference = shape(CONTENT["en"])
        for code in INTL_CODES:
            with self.subTest(code=code):
                self.assertEqual(shape(CONTENT[code]), reference)

    def test_meta_lengths_and_unique_titles(self):
        titles = set()
        for code in INTL_CODES:
            for p in meta_pages(CONTENT[code]):
                with self.subTest(code=code, title=p["title"]):
                    self.assertLessEqual(len(p["title"]), 68)
                    self.assertLessEqual(len(p["description"].replace("{price}", "1.000 €")), 165)
                titles.add(p["title"])
        self.assertEqual(len(titles), 15 * 20)

    def test_urls_resolve_back_to_their_key(self):
        for code in INTL_CODES:
            for key in PAGE_KEYS:
                parts = page_path(code, key).strip("/").split("/")[1:]
                with self.subTest(code=code, key=key):
                    self.assertEqual(resolve(code, *parts), key)

    def test_alternates_cover_turkish_site_and_x_default(self):
        alts = dict(alternates("cluster:sosyal-medya-ajansi"))
        self.assertEqual(alts["tr"], "/sosyal-medya-ajansi/")
        self.assertEqual(alts["x-default"], alts["en"])
        self.assertEqual(set(alts), {"tr", "en", "x-default"})   # the public languages only

    def test_only_english_is_public_besides_turkish(self):
        self.assertEqual(active_codes(), ["en"])
        with override_settings(AGENCY_LANGS=["en", "de"]):
            self.assertEqual(active_codes(), ["en", "de"])
            self.assertEqual(set(dict(alternates("home"))), {"tr", "en", "de", "x-default"})


class PricingTests(TestCase):
    def test_rounding_and_format(self):
        self.assertEqual(nice_round(862), 860)
        self.assertEqual(nice_round(3694), 3700)
        self.assertEqual(fmt("de", 1600), "1.600 €")
        self.assertEqual(fmt("en", 1000), "$1,000")

    def test_market_price_uses_stored_rate(self):
        from django.core.cache import cache
        FxRate.objects.update_or_create(currency="PLN", defaults={"rate": 4})
        cache.clear()
        Market.objects.filter(pk="pl").update(usd_price=900)
        price = price_for("pl")
        self.assertEqual((price["amount"], price["currency"]), (3600, "PLN"))
        self.assertEqual(len(price["tiers"]), 3)

    def test_reduced_markets_seeded(self):
        self.assertEqual(Market.objects.get(pk="az").usd_price, 900)
        self.assertEqual(Market.objects.get(pk="de").usd_price, 1000)


class PageTests(TestCase):
    def test_public_pages_render(self):
        for code in active_codes():
            for key in PAGE_KEYS:
                url = page_path(code, key)
                with self.subTest(url=url):
                    r = self.client.get(url)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertIn(f'<html lang="{code}"', html)
                    self.assertEqual(len(re.findall(r'<link rel="alternate" hreflang=', html)), 3)   # tr, en, x-default
                    self.assertNotIn("{price}", html)

    def test_retired_languages_redirect_to_the_english_page(self):
        retired = [code for code in INTL_CODES if code not in active_codes()]
        self.assertEqual(len(retired), 14)
        for code in retired:
            for key in PAGE_KEYS:
                url = page_path(code, key)
                with self.subTest(url=url):
                    r = self.client.get(url)
                    self.assertEqual(r.status_code, 301)
                    self.assertEqual(r["Location"], page_path("en", key))
        r = self.client.get(page_path("de", "home") + "?utm_source=x")
        self.assertEqual(r["Location"], "/en/?utm_source=x")

    def test_a_language_can_be_brought_back(self):
        with override_settings(AGENCY_LANGS=["en", "de"]):
            r = self.client.get(page_path("de", "cluster:sosyal-medya-ajansi"))
            self.assertEqual(r.status_code, 200)
            self.assertEqual(len(re.findall(r'<link rel="alternate" hreflang=', r.content.decode())), 4)

    def test_follower_pages_of_a_retired_language_do_not_link_to_its_agency_pages(self):
        from apps.growth.content import page_path as growth_path

        hub = growth_path("de", "main", "instagram")
        html = self.client.get(hub).content.decode()
        self.assertIn(f'<a href="{hub}" class="brand"', html)          # the logo stays in the language
        for key in PAGE_KEYS:
            self.assertNotIn(f'href="{page_path("de", key)}"', html)   # no link into a redirect
        english = self.client.get(growth_path("en", "main", "instagram")).content.decode()
        self.assertIn('<a href="/en/" class="brand"', english)
        self.assertIn(f'href="{page_path("en", "about")}"', english)

    def test_unknown_slug_404(self):
        self.assertEqual(self.client.get("/de/nope/").status_code, 404)
        self.assertEqual(self.client.get("/de/branchen/nope/").status_code, 404)

    def test_turkish_pages_link_to_translations(self):
        html = self.client.get("/rehber/sosyal-medya-ajans-sozlesmesi/").content.decode()
        self.assertIn(f'hreflang="en" href="{page_path("en", "guide:sosyal-medya-ajans-sozlesmesi")}"', html.replace("https://sterragency.com", "").replace("http://localhost:8000", ""))
        self.assertIn(f'href="{page_path("en", "guide:sosyal-medya-ajans-sozlesmesi")}" hreflang="en"', html)
        self.assertNotIn('hreflang="de"', html)

    def test_sitemap_has_intl_pages(self):
        body = self.client.get("/sitemaps/agency.xml").content.decode()
        self.assertIn(f"{page_path('en', 'guide:sosyal-medya-ajans-sozlesmesi')}</loc>", body)
        self.assertEqual(body.count("<loc>"), len(PAGE_KEYS))                  # English only
        for code in INTL_CODES:
            if code != "en":
                self.assertNotIn(f"/{code}/", body)                            # no retired language, in loc or hreflang


@override_settings(LEAD_NOTIFY_EMAILS=["owner@example.com"],
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LeadTests(TestCase):
    data = {"lang": "de", "page_key": "cluster:sosyal-medya-ajansi", "interest": "sosyal-medya-ajansi",
            "name": "Max Muster", "email": "max@example.com", "phone": "+49 151 2345678",
            "country": "Deutschland", "consent": "on"}

    def test_valid_lead(self):
        r = self.client.post("/intl/send/", self.data)
        self.assertRedirects(r, "/intl/thank-you/?lang=de", fetch_redirect_response=False)
        lead = IntlLead.objects.get()
        self.assertEqual(lead.usd_price, 1000)
        self.assertTrue(lead.quoted_price)
        self.assertEqual(mail.outbox[0].reply_to, ["max@example.com"])
        self.assertIn("intl_agency", self.client.get("/intl/thank-you/?lang=de").content.decode())

    def test_errors_in_page_language(self):
        r = self.client.post("/intl/send/", {**self.data, "email": "x", "consent": ""})
        self.assertEqual(r.status_code, 400)
        self.assertIn("gültige E-Mail-Adresse", r.content.decode())

    def test_fx_fetch_failure_keeps_fallback(self):
        from .pricing import refresh_rates
        with mock.patch("apps.intl.pricing.requests.get", side_effect=OSError):
            self.assertFalse(refresh_rates(force=True))
        self.assertTrue(price_for("sv")["display"])
