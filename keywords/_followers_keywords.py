"""Dump every follower/creator page's keyword list, in all 16 languages, to a CSV:
    python keywords/_followers_keywords.py  ->  keywords/followers_keywords.csv
Columns: language, section (instagram/tiktok/creators), page, url, keyword."""
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from apps.growth.content import CONTENT, CREATORS, creator_path, page_path  # noqa: E402

with open(ROOT / "keywords" / "followers_keywords.csv", "w", newline="", encoding="utf-8") as fh:
    out = csv.writer(fh)
    out.writerow(["language", "section", "page", "url", "keyword"])
    for platform, langs in CONTENT.items():
        for code, data in langs.items():
            for page, words in data["keywords"].items():
                for kw in words:
                    out.writerow([code, platform, page, page_path(code, page, platform), kw])
    for code, data in CREATORS.items():
        for page, words in data["keywords"].items():
            for kw in words:
                out.writerow([code, "creators", page, creator_path(code, page), kw])
print("wrote keywords/followers_keywords.csv")
