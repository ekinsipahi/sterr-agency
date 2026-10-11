import re

from django.test import TestCase
from django.urls import reverse

from .cities import CITIES
from .services import CLUSTERS, city_page
from .turkish import genitive, locative, slugify_tr


class TurkishTests(TestCase):
    def test_suffixes(self):
        cases = {"İstanbul": "İstanbul'da", "İzmir": "İzmir'de", "Muş": "Muş'ta", "Kars": "Kars'ta",
                 "Tokat": "Tokat'ta", "Gaziantep": "Gaziantep'te", "Elazığ": "Elazığ'da", "Van": "Van'da"}
        for name, expected in cases.items():
            self.assertEqual(locative(name), expected)
        self.assertEqual(genitive("Ankara"), "Ankara'nın")
        self.assertEqual(genitive("Bingöl"), "Bingöl'ün")
        self.assertEqual(slugify_tr("Şanlıurfa"), "sanliurfa")
        self.assertEqual(slugify_tr("Iğdır"), "igdir")


class ProgrammaticSeoTests(TestCase):
    def test_81_unique_provinces(self):
        self.assertEqual(len(CITIES), 81)
        self.assertEqual(len({c.slug for c in CITIES}), 81)

    def test_meta_lengths_and_uniqueness(self):
        titles, descs = set(), set()
        for cl in CLUSTERS:
            for c in CITIES:
                p = city_page(cl, c)
                self.assertLessEqual(len(p["title"]), 60, p["title"])
                self.assertLessEqual(len(p["description"]), 158, p["description"])
                self.assertIn(c.name, p["title"])
                titles.add(p["title"])
                descs.add(p["description"])
        self.assertEqual(len(titles), len(CLUSTERS) * 81)
        self.assertEqual(len(descs), len(CLUSTERS) * 81)

    def test_city_page_renders(self):
        resp = self.client.get(reverse("seo:city", args=["sosyal-medya-ajansi", "izmir"]))
        self.assertContains(resp, "<h1")
        self.assertContains(resp, "İzmir Sosyal Medya Ajansı")
        self.assertContains(resp, '"@type":"FAQPage"')

    def test_unknown_city_404(self):
        resp = self.client.get("/sosyal-medya-ajansi/atlantis/")
        self.assertEqual(resp.status_code, 404)

    def test_sitemap_lists_all_city_pages(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertEqual(len(re.findall(r"<loc>[^<]*/dijital-pazarlama-ajansi/", body)), 82)  # hub + 81
