"""Checks a language's growth copy against the English source: same keys and shapes,
meta lengths, wording rules, and that every keyword assigned to a page appears on it.
Body sections, FAQ counts and keyword lists are each language's own: English carries
sections and questions for English-only searches that the other languages don't have.
Used by the tests and by `manage.py check_growth_copy <code>` (which only imports the
files of the languages it checks, so a half-written translation elsewhere can't break it)."""
import json
import re
from importlib import import_module

from .constants import CREATOR_PAGES, PLATFORMS, has_language, pages_for

TITLE_MAX, DESCRIPTION_MAX = 68, 165
# Never on the site: search-engine talk, promises we can't make, competitor brands,
# selling accounts or engagement, and made-up reviews.
FORBIDDEN = re.compile(r"\bSEO\b|guarantee|garanti|garan[țt]|gwaranc|гарант|zəmanət|ضمان|bedava|ücretsiz|buzzoid|passthevote|stormlikes|goread|socialwick|superviral|famety|"
                       r"bulkoid|megafamous|useviral|media ?mister|smm panel|\bfree\b|gratis|gratuit|"
                       r"\bpaypal\b|crypto|bitcoin|5[- ]star|★", re.I)

# Prices and delivery windows of the one-time packages the monthly agency package replaced.
STALE = re.compile(r"34[.,]99|59[.,]99|124[.,]99|229[.,]99|\b(?:7|14|24|30|60)[–-](?:14|24|36|60|120)\b")


# A page of one platform must not talk about the others (each has its own section).
OTHER_PLATFORMS = {"instagram": ("tiktok",), "tiktok": ("instagram",), "youtube": ("instagram", "tiktok")}


def sections(code):
    """The platforms that have pages in this language, plus the creators hub."""
    return tuple(p for p in PLATFORMS if has_language(p, code)) + ("creators",)


def load(code):
    """(UI, {platform: its UI overrides}, {section: DATA}) of a language."""
    module = import_module(f"apps.growth.i18n.{code}")
    extras = {p: getattr(module, p.upper()) for p in PLATFORMS if getattr(module, p.upper(), None)}
    pages = {p: import_module(f"apps.growth.pages.{p}.{code}").DATA for p in sections(code)}
    return module.UI, extras, pages


def shape(value, skip=("body", "faqs", "keywords", "geo", "subs")):
    if isinstance(value, dict):
        return {k: shape(v, skip) for k, v in value.items() if k not in skip}
    if isinstance(value, (list, tuple)):
        return [shape(v, skip) for v in value]
    return type(value).__name__


def fold(text):
    """Lowercase for keyword matching; Turkish "İ" lowercases to "i" + a combining dot, drop the dot."""
    return text.lower().replace("i\u0307", "i")


def page_text(page):
    return fold(json.dumps({k: v for k, v in page.items() if k != "minutes"}, ensure_ascii=False))


def check(code):
    """List of problems (empty when the language is complete and clean)."""
    problems = []
    ref_ui, _, ref_pages = load("en")
    try:
        ui, extras, pages = load(code)
    except Exception as exc:  # noqa: BLE001 - report import/syntax errors as a problem
        return [f"{code}: cannot import: {exc!r}"]

    if set(ui) != set(ref_ui):
        problems.append(f"{code} UI keys: missing {sorted(set(ref_ui) - set(ui))}, extra {sorted(set(ui) - set(ref_ui))}")
    for key, value in ref_ui.items():
        if key in ui and shape(ui[key]) != shape(value):
            problems.append(f"{code} UI[{key!r}] shape differs from English")
        pairs = [(value, ui.get(key))] if isinstance(value, str) else (
            list(zip(value, ui[key])) if isinstance(value, (list, tuple)) and key in ui else [])
        for ref_text, text in pairs:
            for ph in re.findall(r"\{[a-z_]+\}", ref_text) if isinstance(ref_text, str) else []:
                if text is not None and ph not in text:
                    problems.append(f"{code} UI[{key!r}] lost placeholder {ph}")
    # A platform's own wording replaces general strings: same shape and placeholders as what it replaces.
    for platform, extra in extras.items():
        if not has_language(platform, code):
            problems.append(f"{code}: {platform.upper()} wording for a platform this language has no pages for")
        for key, value in extra.items():
            if key in ref_ui and shape(value) != shape(ref_ui[key]):
                problems.append(f"{code} {platform.upper()}[{key!r}] shape differs from UI[{key!r}]")
            for ph in re.findall(r"\{[a-z_]+\}", ref_ui[key]) if isinstance(ref_ui.get(key), str) else []:
                if ph != "{platform}" and ph not in value:
                    problems.append(f"{code} {platform.upper()}[{key!r}] lost placeholder {ph}")
    everything = json.dumps([ui, extras, pages], ensure_ascii=False)
    for stale in STALE.findall(everything):
        problems.append(f"{code}: left over from the one-time packages: {stale!r}")
    if FORBIDDEN.search(json.dumps([ui, extras], ensure_ascii=False)):
        problems.append(f"{code} UI: forbidden word {FORBIDDEN.search(json.dumps([ui, extras], ensure_ascii=False)).group(0)!r}")

    for platform in sections(code):
        data, ref = pages[platform], ref_pages[platform]
        page_keys = CREATOR_PAGES if platform == "creators" else pages_for(platform)
        where = f"{code}/{platform}"
        if shape(data) != shape(ref):
            problems.append(f"{where}: page structure differs from English (keys, tuple sizes, list lengths)")
        if set(data.get("subs", {})) != set(page_keys) - {"main"}:
            problems.append(f"{where}: subs must cover {sorted(set(page_keys) - {'main'})}")
        slugs = list(data.get("subs", {}).values())
        if len(set(slugs)) != len(slugs) or not re.fullmatch(r"[a-z0-9-]+", data.get("base", "")) or any(
                not re.fullmatch(r"[a-z0-9-]+|(/[a-z0-9-]+)+/", s) for s in slugs):
            problems.append(f"{where}: slugs must be unique, lowercase ASCII and hyphens (or /a-path/ for pages of their own)")
        titles = set()
        for page in page_keys:
            p = data.get(page)
            if not p:
                continue
            for field in ("body", "faqs"):
                if field in ref[page] and not p.get(field):
                    problems.append(f"{where}/{page}: empty {field}")
            if any(not (isinstance(qa, (list, tuple)) and len(qa) == 2 and all(isinstance(x, str) and x.strip() for x in qa))
                   for qa in p.get("faqs", [])):
                problems.append(f"{where}/{page}: every FAQ must be a (question, answer) pair")
            if len(p["title"]) > TITLE_MAX:
                problems.append(f"{where}/{page}: title {len(p['title'])} > {TITLE_MAX}: {p['title']}")
            if len(p["description"]) > DESCRIPTION_MAX:
                problems.append(f"{where}/{page}: description {len(p['description'])} > {DESCRIPTION_MAX}")
            titles.add(p["title"])
            text = page_text(p)
            if "{platform}" in text:
                problems.append(f"{where}/{page}: '{{platform}}' placeholder in page copy (write the name out)")
            m = FORBIDDEN.search(text)
            if m:
                problems.append(f"{where}/{page}: forbidden word {m.group(0)!r}")
            for other in OTHER_PLATFORMS.get(platform, ()):
                if other in text:
                    problems.append(f"{where}/{page}: mentions {other}")
            for kw in data.get("keywords", {}).get(page, []):
                if fold(kw) not in text:
                    problems.append(f"{where}/{page}: keyword not used: {kw!r}")
        for key, g in data.get("geo", {}).items():
            if len(g["title"]) > TITLE_MAX or len(g["description"]) > DESCRIPTION_MAX:
                problems.append(f"{where}/geo:{key}: title or description too long")
            if FORBIDDEN.search(page_text(g)):
                problems.append(f"{where}/geo:{key}: forbidden word {FORBIDDEN.search(page_text(g)).group(0)!r}")
        if len(titles) != len(page_keys):
            problems.append(f"{where}: page titles must be unique")
        if set(data.get("keywords", {})) != set(page_keys):
            problems.append(f"{where}: keywords must list every page")
    return problems
