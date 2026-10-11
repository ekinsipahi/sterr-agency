import re

from django.core import mail
from django.test import TestCase, override_settings

from .languages import CONTENT, LANGS, PAGES, page_path
from .models import DentalInquiry


def shape(value):
    """Structure of a content dict: keys and list lengths, not the text."""
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [shape(v) for v in value]
    return type(value).__name__


class ContentTests(TestCase):
    def test_sixteen_languages(self):
        self.assertEqual(len(LANGS), 16)
        self.assertEqual(len({lang.code for lang in LANGS}), 16)

    def test_every_language_matches_english_structure(self):
        reference = shape(CONTENT["en"])
        for lang in LANGS:
            with self.subTest(lang=lang.code):
                self.assertEqual(shape(CONTENT[lang.code]), reference)

    def test_meta_lengths_and_uniqueness(self):
        titles, descs = set(), set()
        for lang in LANGS:
            for page in PAGES:
                p = CONTENT[lang.code][page]
                with self.subTest(lang=lang.code, page=page):
                    self.assertLessEqual(len(p["title"]), 65, p["title"])
                    self.assertLessEqual(len(p["description"]), 165, p["description"])
                titles.add(p["title"])
                descs.add(p["description"])
        self.assertEqual(len(titles), 16 * len(PAGES))
        self.assertEqual(len(descs), 16 * len(PAGES))


class PageTests(TestCase):
    def test_all_32_pages_render_with_hreflang(self):
        for lang in LANGS:
            for page in PAGES:
                url = page_path(lang.code, page)
                with self.subTest(url=url):
                    r = self.client.get(url)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertIn(f'<html lang="{lang.code}"', html)
                    self.assertEqual(len(re.findall(r'<link rel="alternate" hreflang=', html)), 17)
                    self.assertIn(CONTENT[lang.code][page]["h1"].replace("'", "&#x27;"), html)

    def test_arabic_is_rtl(self):
        self.assertIn('dir="rtl"', self.client.get("/dental-tourism/ar/").content.decode())

    def test_english_prefix_redirects_and_unknown_404(self):
        self.assertRedirects(self.client.get("/dental-tourism/en/partners/"), "/dental-tourism/partners/",
                             status_code=301)
        self.assertEqual(self.client.get("/dental-tourism/xx/").status_code, 404)
        self.assertEqual(self.client.get("/dental-tourism/de/partners/").status_code, 404)  # German slug is "partner"

    def test_sitemap_lists_dental_pages_with_alternates(self):
        body = self.client.get("/sitemap.xml").content.decode()
        for lang in LANGS:
            self.assertIn(f"{page_path(lang.code, 'partners')}</loc>", body)
        self.assertIn('hreflang="x-default"', body)

    def test_language_menu_on_turkish_site(self):
        html = self.client.get("/").content.decode()
        self.assertIn('class="lang-menu"', html)
        self.assertIn('href="/de/" hreflang="de"', html)


@override_settings(LEAD_NOTIFY_EMAILS=["owner@example.com"],
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InquiryTests(TestCase):
    data = {"lang": "de", "page": "hub", "kind": "patient", "name": "Anna Müller", "email": "anna@example.com",
            "phone": "+49 151 2345678", "country": "Deutschland", "treatment": "implants", "consent": "on"}

    def test_valid_inquiry_saved_and_notified(self):
        r = self.client.post("/dental-tourism/send/", self.data)
        self.assertRedirects(r, "/dental-tourism/thank-you/?lang=de", fetch_redirect_response=False)
        inquiry = DentalInquiry.objects.get()
        self.assertEqual((inquiry.lang, inquiry.kind), ("de", "patient"))
        self.assertTrue(inquiry.notified)
        self.assertEqual(mail.outbox[0].reply_to, ["anna@example.com"])
        thanks = self.client.get("/dental-tourism/thank-you/?lang=de").content.decode()
        self.assertIn("dental_patient", thanks)

    def test_errors_in_page_language(self):
        r = self.client.post("/dental-tourism/send/", {**self.data, "email": "nope", "consent": ""})
        self.assertEqual(r.status_code, 400)
        self.assertIn("gültige E-Mail-Adresse", r.content.decode())
        self.assertFalse(DentalInquiry.objects.exists())

    def test_honeypot(self):
        self.client.post("/dental-tourism/send/", {**self.data, "fax": "spam"})
        self.assertFalse(DentalInquiry.objects.exists())
