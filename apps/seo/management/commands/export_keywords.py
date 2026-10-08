"""Write the keyword/pSEO inventory to keywords/*.csv.

    python manage.py export_keywords
"""
import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from apps.seo.cities import CITIES_ALPHA
from apps.seo.services import CLUSTERS, city_page
from apps.seo.turkish import ascii_fold, tr_lower

# Every commercial keyword from the research → the cluster whose city page owns it.
CITY_SEEDS = [
    ("dijital pazarlama ajansı", "dijital-pazarlama-ajansi"),
    ("dijital pazarlama ajansları", "dijital-pazarlama-ajansi"),
    ("dijital pazarlama ajansı fiyatları", "dijital-pazarlama-ajansi"),
    ("dijital ajans", "dijital-pazarlama-ajansi"),
    ("sosyal medya ajansı", "sosyal-medya-ajansi"),
    ("sosyal medya ajansları", "sosyal-medya-ajansi"),
    ("sosyal medya ajans", "sosyal-medya-ajansi"),
    ("sosyal medya ajansı fiyatları", "sosyal-medya-ajansi"),
    ("sosyal medya ajans fiyatları", "sosyal-medya-ajansi"),
    ("sosyal medya ajans ücretleri", "sosyal-medya-ajansi"),
    ("sosyal medya yönetimi ajansı", "sosyal-medya-yonetimi-ajansi"),
    ("sosyal medya yönetimi", "sosyal-medya-yonetimi-ajansi"),
    ("dijital pazarlama uzmanı", "dijital-pazarlama-uzmani"),
    ("dijital pazarlama uzmanları", "dijital-pazarlama-uzmani"),
    ("dijital pazarlama uzman", "dijital-pazarlama-uzmani"),
]


class Command(BaseCommand):
    help = "Export il × keyword variations and the programmatic page inventory to keywords/"

    def handle(self, *args, **opts):
        out = Path(settings.BASE_DIR) / "keywords"
        out.mkdir(exist_ok=True)

        with open(out / "il_keyword_varyasyonlari.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["keyword", "varyasyon_tipi", "ana_keyword", "il", "plaka", "bolge", "hedef_url"])
            rows = 0
            for seed, cluster in CITY_SEEDS:
                for c in CITIES_ALPHA:
                    url = settings.SITE_URL + reverse("seo:city", args=[cluster, c.slug])
                    il_lower = tr_lower(c.name)
                    variants = [
                        (f"{seed} {il_lower}", "keyword + il"),
                        (f"{il_lower} {seed}", "il + keyword"),
                        (f"{ascii_fold(seed)} {ascii_fold(il_lower)}", "türkçe karaktersiz"),
                    ]
                    seen = set()
                    for kw, kind in variants:
                        if kw in seen:
                            continue
                        seen.add(kw)
                        w.writerow([kw, kind, seed, c.name, c.plate, c.region_obj.name, url])
                        rows += 1

        with open(out / "pseo_sayfalar.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["url", "kume", "il", "plaka", "bolge", "pazar", "meta_title", "title_len",
                        "meta_description", "desc_len", "h1", "hedef_keywordler"])
            pages = 0
            for cl in CLUSTERS:
                for c in CITIES_ALPHA:
                    p = city_page(cl, c)
                    w.writerow([
                        settings.SITE_URL + reverse("seo:city", args=[cl.slug, c.slug]),
                        cl.name, c.name, c.plate, c.region_obj.name, c.tier,
                        p["title"], len(p["title"]), p["description"], len(p["description"]),
                        p["h1"], " | ".join(p["keywords"]),
                    ])
                    pages += 1

        self.stdout.write(self.style.SUCCESS(
            f"{rows} il varyasyonu → keywords/il_keyword_varyasyonlari.csv\n"
            f"{pages} pSEO sayfası → keywords/pseo_sayfalar.csv"
        ))
