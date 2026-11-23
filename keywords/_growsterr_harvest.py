"""Growsterr keyword plan -> Sterr Agency pages (English).

    python keywords/_growsterr_harvest.py   ->  keywords/growsterr_harvest.csv + keywords/GROWSTERR_HARVEST.md

For every keyword in growsterr's docs/keywords/page-plan.csv decide:
  ADD   the intent has a Sterr Agency page and the keyword is not on it yet
  HAVE  the page already carries it (exact phrase, or all of its meaningful words)
  NEW   the intent has no page on Sterr Agency (a page or section would have to be opened)
  SKIP  not to be moved (rule-breaking, not sold, spam variant, thin)
Reads the growsterr repo next to this one (or $GROWSTERR). No Django, no database."""
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
STERR = HERE.parent
GROW = Path(os.environ.get("GROWSTERR", STERR.parent / "growsterr"))
sys.path.insert(0, str(STERR))

from apps.growth.validate import FORBIDDEN, fold, page_text  # noqa: E402

DATA = {p: import_module(f"apps.growth.pages.{p}.en").DATA for p in ("instagram", "tiktok", "creators")}
ns = {}
exec((GROW / "apps/pages/archive.py").read_text(), ns)
ARCHIVED = ns["ARCHIVED"]

# ---------------------------------------------------------------------------------------------
# Sterr Agency pages (English)


def url(section, page):
    d = DATA[section]
    base = f"/en/{d['base']}/"
    if page == "main":
        return base
    if page.startswith("geo:"):
        return f"{base}{page[4:]}/"
    sub = d["subs"][page]
    return f"/en{sub}" if sub.startswith("/") else f"{base}{sub}/"


def text_of(section, page):
    d = DATA[section]
    if page.startswith("geo:"):
        return page_text(d["geo"][page[4:]])
    return page_text(d[page])


INTL_DATA = import_module("apps.intl.locales.en").DATA
INTL = {  # English agency pages outside the growth app (apps/intl): key -> (url, content)
    "intl:social-media-agency": ("/en/social-media-agency/", INTL_DATA["clusters"]["sosyal-medya-ajansi"]),
    "intl:social-media-management": ("/en/social-media-management/", INTL_DATA["clusters"]["sosyal-medya-yonetimi-ajansi"]),
    "intl:social-media-agency-pricing": ("/en/guides/social-media-agency-pricing/", INTL_DATA["guides"]["sosyal-medya-ajansi-fiyatlari"]),
}

# ---------------------------------------------------------------------------------------------
# Keyword-level rules

STOP = {"buy", "get", "the", "a", "an", "for", "on", "in", "of", "to", "with", "and", "my", "your", "now", "online",
        "is", "how", "do", "you", "can", "that", "it", "by", "at", "from", "are", "does", "what", "which", "i", "u", "or",
        "purchase", "purchasing", "buying", "ig", "insta", "instagram", "tiktok", "youtube", "yt", "s", "there", "why", "me",
        "very", "super", "really", "good", "t", "don", "who", "where", "much", "many", "need", "have", "will", "if",
        "no", "not"}
# Words that mean the same for matching: a keyword word counts as present when any of its group is on the page.
SYNONYMS = [{"site", "sites", "website", "websites"}, {"slow", "slowly", "gradual", "gradually"},
            {"cheap", "cheapest", "lowest", "low"}, {"instant", "instantly"}, {"everyday", "daily"},
            {"legit", "legitimate"}, {"1000", "1k"}, {"2000", "2k"}, {"3000", "3k"}, {"5000", "5k"}, {"10000", "10k"},
            {"20000", "20k"}, {"50000", "50k"}, {"100000", "100k"}, {"1000000", "1m", "million"},
            {"fall", "drop"}, {"last", "stay"}, {"forever", "permanent"}, {"interact", "engage"}]
SYN = {w: group for group in SYNONYMS for w in group}
# Rules the site already enforces (validate.FORBIDDEN) plus the product rules behind them.
RULES = [
    (re.compile(r"\bfree\b|gratis|no cost|without paying"), "ücretsiz/deneme paketi yok (sitede yasak kelime)"),
    (re.compile(r"paypal|crypto|bitcoin|\bbtc\b|ethereum|usdt|gcash|paytm|\bupi\b|mpesa|m-pesa|momo|mobile money|klarna|"
                r"coins app|afterpay|cash app|venmo|naira|skrill"), "bu ödeme yöntemi yok (yalnız kart, Apple Pay, Google Pay)"),
    (re.compile(r"smm|panel|reseller|discord|telegram|marketplace|wholesale|\bapi\b|fiverr|upwork|etsy|ebay|g2g|shopee|"
                r"playerup|z2u"), "panel/bayilik/pazar yeri: farklı ürün"),
    (re.compile(r"verified|celebrit|kylie|jenner|famous people|blue tick|blue check"), "verified/ünlü vaadi yok"),
    (re.compile(r"female|\bmale\b|women|girls|\bmen\b"), "cinsiyet hedefleme yapılamıyor"),
    (re.compile(r"(?<!no )\bbots?\b"), "bot satılmıyor (yalnızca 'instant = bot' anlatımında geçer)"),
    (re.compile(r"account for sale|buy (an )?(instagram|tiktok|youtube) accounts?$|accounts? with followers"), "hesap satışı yok"),
    (re.compile(r"hack|generator|\bmod\b|apk|cheat|script|termux|github|\bcode\b|coupon|promo code|discount code"),
     "hile/araç/kupon araması: niyet uyuşmuyor"),
    (re.compile(r"reddit|quora|trustpilot|twitter|facebook|linkedin|twitch|telegram|snapchat|threads|spotify|pinterest"),
     "başka platform ya da forum araması"),
    (re.compile(r"kaise|kare\b|\bke\b|\bme\b followers|hindi|rupees?|\binr\b|\bpkr\b|naira|shillings?"), "yerel dil/para birimi (Hindistan vb.): hedef pazar değil"),
    (re.compile(r"\b(2019|202[0-5])\b"), "eski yıl"),
    (re.compile(r"\$ ?0?\.\d+|\b\d+ ?[$€]|[$€] ?\d|\bunder \d+|\bfor \d+ ?(dollars?|bucks?)"), "fiyat vaadi içeren arama ('1$' vb.)"),
    (re.compile(r"guarantee|refill|warranty|lifetime"), "garanti/refill yok (sitede yasak kelime)"),
    (re.compile(r"\bapps?\b"), "uygulama araması (uygulamamız yok)"),
    (re.compile(r"near me"), "yerel arama ('near me')"),
    (re.compile(r"\b(dm|clipping|pr|web|ugc|feed|handling) agency\b|\bagent\b"), "sunulmayan hizmet türü ya da anlamsız varyasyon"),
    (re.compile(r"(?<!go )\blive\b(?! on)"), "canlı yayın izleyicisi/beğenisi paketi yok"),
    (re.compile(r"instant(ly)?\b|immediately|in seconds|in minutes"), None),  # allowed: answered on the instant page
]
# Keyword-tool permutations with no intent of their own (the spam part of growsterr's lists).
JUNK_TAIL = re.compile(r"\b(buy|com|social|web|page|link|viewer|views views|buzz|by tv|instagram followers instagram|"
                       r"from tiktok|from youtube|ssm|in order|easy|real website|likes increase|instant and active)$")
COMPETITORS = re.compile(r"buzzoid|stormlikes|famety|goread|socialwick|superviral|bulkoid|megafamous|useviral|media ?mister|"
                         r"passthevote|blastup|boostme|buzzvoice|poprey|promotid|qqtube|socialboom|socialboosting|stillviral|"
                         r"ytviews|zeru|mysocialfollowing|delivered social|youtube market|buyyoutubeviews|twicsy|ampfluence|kicksta")
NON_TARGET_COUNTRY = re.compile(r"\b(india|indian|pakistan|pakistani|nigeria|nigerian|kenya|ghana|uganda|bangladesh|nepal|"
                                r"sri lanka|philippines|vietnam|cambodia|egypt|lebanon|south africa|africa|malaysia|indonesia)\b")


def keyword_rule(kw):
    """A reason this keyword is not moved whatever its cluster, or None."""
    if COMPETITORS.search(kw):
        return "rakip marka (marka hakkı riski; testle engelli)"
    for pattern, reason in RULES:
        if reason and pattern.search(kw):
            return reason
    if FORBIDDEN.search(kw):
        return "sitede yasak kelime"
    words = kw.split()
    if JUNK_TAIL.search(kw) or any(a == b for a, b in zip(words, words[1:])):
        return "anlamsız varyasyon (keyword aracı tekrarı)"
    return None


def keyword_platform(kw, default):
    """The platform a keyword names (payment and guide clusters mix platforms)."""
    hits = [p for p, pat in (("instagram", r"instagram|\big\b|insta\b|reels?\b"), ("tiktok", r"tiktok|tik tok|fyp\b"),
                              ("youtube", r"youtube|\byt\b|shorts\b|subscribers?|\bsubs\b")) if re.search(pat, kw)]
    return hits[0] if len(hits) == 1 else default


# ---------------------------------------------------------------------------------------------
# Cluster-level mapping: growsterr variant -> page key of the 31-page template

PACKS = {1000: "pack_1k", 2000: "pack_2k", 3000: "pack_3k", 5000: "pack_5k", 10000: "pack_10k"}
GEO = {"us": "geo:usa", "gb": "geo:uk", "au": "geo:australia", "ae": "geo:uae",
       "de": "geo:europe", "fr": "geo:europe", "es": "geo:europe", "it": "geo:europe", "nl": "geo:europe", "gr": "geo:europe",
       "se": "geo:europe", "no": "geo:europe", "dk": "geo:europe", "fi": "geo:europe", "pl": "geo:europe", "pt": "geo:europe",
       "ch": "geo:europe", "ie": "geo:europe"}
SKIP_MOD = {"free": "ücretsiz paket yok", "free-trial": "deneme paketi yok", "smm-panel": "panel/bayilik: farklı ürün",
            "verified": "verified/ünlü vaadi yok", "female": "cinsiyet hedefleme yapılamıyor"}
AUDIENCE = {"real": "real", "organic": "real", "active": "real", "targeted": "real", "gradual": "guide_speed",
            "no-drop": "non_drop", "safe": "legit", "private-account": "guide_buy", "viral": "main", "monthly": "pricing",
            "cheap": "pricing", "fast": "instant", "promote": "agency", "live": "guide_speed"}
PROMOTE_NEW = "'TikTok Promote işe yarar mı' rehberi (yeni sayfa)"
LIKES = {"real": "likes", "organic": "likes", "safe": "likes", "no-drop": "likes_gradual", "private-account": "likes",
         "viral": "likes", "cheap": "likes", "monthly": "likes_monthly", "gradual": "likes_gradual", "reels": "likes_reels",
         "shorts": "likes_reels", "comment-likes": "comments", "fast": "instant"}
VIEWS = {"real": "views", "organic": "views", "safe": "views", "no-drop": "views", "cheap": "views", "gradual": "views",
         "monthly": "views", "high-retention": "views", "promote": "NEW:promote", "fyp": "blog_more_views",
         "reels": "views_reels", "shorts": "views_reels", "fast": "instant"}
COMMENTS = {"custom": "comments_custom", "ai": "comments_custom", "reels": "comments", "shorts": "comments",
            "cheap": "comments", "real": "comments", "fast": "instant"}


def grid_page(platform, service, quantity, modifier, country, archived):
    """(page key | None, skip reason | None, note)."""
    if modifier in SKIP_MOD:
        return None, SKIP_MOD[modifier], ""
    if archived:
        return None, "growsterr'da da ince sayfa diye kaldırılmış", ""
    if not service:
        return "packages", None, ""
    if country:
        if service not in ("followers", "subscribers"):
            return None, "ülke × beğeni/izlenme/yorum: ince sayfa", ""
        return GEO.get(country), (None if country in GEO else "hedef pazar değil (yerel ödeme/fiyat beklentisi uymuyor)"), ""
    if service in ("followers", "subscribers"):
        if quantity:
            return PACKS.get(quantity, f"pack_{quantity}"), None, ""
        return AUDIENCE.get(modifier, "main") if modifier else "main", None, ""
    table = {"likes": LIKES, "views": VIEWS, "comments": COMMENTS}[service]
    if modifier == "live":
        return None, "canlı yayın izleyicisi/beğenisi paketi yok", ""
    if quantity:
        return service, None, "adet: sayfadaki 'küçük paket satmıyoruz' bölümüne"
    return (table.get(modifier, service) if modifier else service), None, ""


# growsterr article key -> (section, page) on Sterr Agency, or ("SKIP", reason), or ("NEW", label)
ARTICLES = {
    "best-instagram-growth-services": ("instagram", "legit"),
    "best-tiktok-growth-services": ("tiktok", "legit"),
    "best-youtube-growth-services": ("youtube", "legit"),
    "buying-tiktok-followers-and-creator-rewards": ("tiktok", "blog_views_money"),
    "buying-youtube-subscribers-and-monetization": ("youtube", "blog_views_money"),
    "can-you-buy-instagram-comments": ("instagram", "blog_still_buy"),
    "can-you-buy-tiktok-comments": ("tiktok", "blog_still_buy"),
    "do-celebrities-buy-followers": ("instagram", "guide_buy"),
    "does-buying-instagram-followers-work": ("instagram", "guide_buy"),
    "does-buying-tiktok-followers-work": ("tiktok", "guide_buy"),
    "does-buying-youtube-subscribers-work": ("youtube", "guide_buy"),
    "does-tiktok-promote-work": ("NEW", "'TikTok Promote işe yarar mı' rehberi (yeni sayfa)"),
    "how-to-get-instagram-followers": ("SKIP", "yerel dil (Hindistan): hedef pazar değil"),
    "how-to-get-instagram-followers-on-your-phone": ("instagram", "guide_buy"),
    "how-to-get-on-the-tiktok-fyp": ("tiktok", "blog_more_views"),
    "how-to-get-tiktok-followers-on-your-phone": ("tiktok", "guide_buy"),
    "instagram-comment-limits": ("instagram", "blog_comment_limit"),
    "tiktok-comment-limits": ("tiktok", "blog_comment_limit"),
    "tiktok-creator-rewards-program": ("tiktok", "blog_views_money"),
    "tiktok-live-1000-followers": ("tiktok", "pack_1k"),
    "why-instagram-posts-get-zero-likes": ("instagram", "blog_more_views"),
    "why-tiktok-videos-get-zero-views": ("tiktok", "blog_more_views"),
    "instagram-growth-by-country": ("instagram", "likes"),
    "tiktok-growth-by-country": ("tiktok", "main"),
    "youtube-growth-by-country": ("youtube", "views"),
    "tiktok-reposts": ("NEW", "'TikTok paylaşım, kaydetme, repost' sayfası (yeni sayfa)"),
    "tiktok-saves": ("NEW", "'TikTok paylaşım, kaydetme, repost' sayfası (yeni sayfa)"),
    "tiktok-shares": ("NEW", "'TikTok paylaşım, kaydetme, repost' sayfası (yeni sayfa)"),
    "tiktok-shop-growth": ("tiktok", "main"),
    "tiktok-sound-promotion": ("SKIP", "müzik/ses tanıtımı hizmeti yok"),
    "pay-with-apple-pay": ("*", "pricing"), "pay-with-credit-card": ("*", "pricing"),
    "pay-with-debit-card": ("*", "pricing"), "pay-with-google-pay": ("*", "pricing"),
    # agency
    "agency-pricing": ("intl", "intl:social-media-agency-pricing"),
    "ai-influencer-marketing": ("SKIP", "marka tarafı / sunulan bir hizmet değil"),
    "ai-instagram-growth": ("SKIP", "AI ajan ürünü yok"),
    "best-influencer-agencies": ("creators", "main"),
    "creators": ("creators", "main"),
    "creators-apply": ("creators", "guide_signed"),
    "how-influencer-agencies-work": ("creators", "guide_what"),
    "influencer-agency": ("creators", "main"),
    "influencer-agency-fashion": ("creators", "main"),
    "influencer-agency-gaming": ("creators", "main"),
    "influencer-campaigns": ("SKIP", "marka tarafı (outreach, PR, gifting): bunu marka arar, creator değil"),
    "influencer-marketing-facebook-linkedin": ("SKIP", "başka platform"),
    "influencer-marketing-instagram": ("creators", "main"),
    "influencer-marketing-platform": ("SKIP", "marka tarafı (platform/yazılım araması)"),
    "influencer-marketing-report-2026": ("SKIP", "haber/rapor araması: niyet uyuşmuyor"),
    "influencer-marketing-tiktok": ("creators", "main"),
    "influencer-marketing-youtube": ("creators", "main"),
    "instagram-ads-agency": ("intl", "intl:social-media-agency"),
    "instagram-content-agency": ("intl", "intl:social-media-management"),
    "instagram-growth-agency": ("instagram", "agency"),
    "instagram-marketing-agency": ("intl", "intl:social-media-agency"),
    "tiktok-agency": ("tiktok", "agency"),
    "tiktok-ugc-agency": ("SKIP", "UGC üretim hizmeti yok"),
    "what-is-influencer-marketing": ("SKIP", "tanım araması: niyet uyuşmuyor"),
}
# Country keywords the creators page can carry in ONE "where we work" sentence; cities and the rest stay out.
AGENCY_GEO_KEEP = {"influencer agency usa", "influencer agency in usa", "influencer agency in uk", "influencer agency canada",
                   "influencer agency europe", "influencer agency uae", "influencer talent agency australia"}
BRAND_SIDE = re.compile(r"for brands?|brand (deals?|agency)|outreach|gifting|seeding|\bpr\b|campaign|platform|software|"
                        r"near me|jobs?|salary|careers?|meaning|definition|examples?|news|report|statistics|"
                        r"influencer marketing(?! gigs)|booking|casting|\bkol\b|agency (list|reviews)|roster")
# A keyword whose only missing words are these is a small wording variant, not a new intent.
MINOR = {"viral", "original", "2026", "global", "everyday", "engagement", "fast", "cheap", "greece", "increase", "boost", "best"}


def present(word, vocabulary):
    return any(w in vocabulary or w.rstrip("s") in vocabulary or w + "s" in vocabulary for w in SYN.get(word, {word}))


def missing_words(kw, vocabulary):
    kw = re.sub(r"(?<=\d) (?=000\b)", "", kw)   # "10 000" -> "10000"
    return [w for w in re.findall(r"[a-z0-9$€]+", kw) if w not in STOP and not present(w, vocabulary)]


VOCAB = {}


def _text(section, page):
    key = (section, page)
    if key not in VOCAB:
        text = page_text(INTL[page][1]) if section == "agency (intl)" else text_of(section, page)
        text = re.sub(r"(?<=\d)[,.](?=\d{3}\b)", "", text)   # 1,000 -> 1000
        VOCAB[key] = (text, set(re.findall(r"[a-z0-9$€]+", text)))
    return VOCAB[key]


def section_pages(section):
    d = DATA[section]
    return [k for k in d["keywords"]] + [f"geo:{g}" for g in d.get("geo", {})]


def coverage(section, page, kw):
    """('exact' | 'words' | 'missing', [missing words], page): the page may change when another
    page of the same section already carries the phrase word for word."""
    text, vocabulary = _text(section, page)
    if fold(kw) in text:
        return "exact", [], page
    if section in DATA:
        for other in section_pages(section):
            if other != page and fold(kw) in _text(section, other)[0]:
                return "exact", [], other
    miss = missing_words(kw, vocabulary)
    return ("words", [], page) if not miss else ("missing", miss, page)


def volumes():
    out = {}
    for name in ("instagram", "youtube", "agency"):
        with open(GROW / f"docs/keywords/{name}.csv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if (r.get("volume") or "").strip():
                    out[re.sub(r"\s+", " ", r["keyword"].strip().lower())] = r["volume"].strip()
    return out


def main():
    vol = volumes()
    rows = list(csv.DictReader(open(GROW / "docs/keywords/page-plan.csv", encoding="utf-8")))
    out = []
    for r in rows:
        archived = r["page"] in ARCHIVED
        kws = [re.sub(r"\s+", " ", k.strip().lower()) for k in r["keywords"].split("|") if k.strip()]
        article = r["article"]
        for kw in kws:
            row = {"keyword": kw, "volume": vol.get(kw, ""), "grow_page": r["page"], "grow_file": r["file"],
                   "grow_status": "arşiv" if archived else "yayında", "decision": "", "section": "", "page": "",
                   "url": "", "coverage": "", "missing_words": "", "priority": "", "reason": ""}
            out.append(row)
            rule = keyword_rule(kw)
            if rule:
                row.update(decision="SKIP", reason=rule)
                continue
            if article:
                if r["file"] in ("articles_alternative", "articles_agency_alternatives"):
                    row.update(decision="SKIP", reason="rakip marka sayfası")
                    continue
                if r["file"] == "articles_agency_countries":
                    if kw in AGENCY_GEO_KEEP:
                        row.update(decision="ADD", section="creators", page="main", url=url("creators", "main"),
                                   coverage="eksik", reason="tek 'nerede çalışıyoruz' cümlesi: ülke adları bir arada")
                    else:
                        row.update(decision="SKIP", reason="şehir/ülke × ajans: ince sayfa (yurt dışında şehir sayfası açmıyoruz)")
                    continue
                target = ARTICLES.get(article)
                if target is None or (archived and r["file"] == "articles_payment"):
                    row.update(decision="SKIP", reason="growsterr'da da kaldırılmış" if archived else "eşleşme tanımlı değil")
                    continue
                if target[0] == "SKIP":
                    row.update(decision="SKIP", reason=target[1])
                    continue
                if target[0] == "NEW":
                    row.update(decision="NEW", section="tiktok", page=target[1], reason="bu niyete sayfa yok")
                    continue
                section, page = target
                if section == "*":
                    section = keyword_platform(kw, r["platform"])
                if section == "creators" and BRAND_SIDE.search(kw):
                    row.update(decision="SKIP", reason="marka tarafı araması (bunu marka arar, creator değil)")
                    continue
                if section == "intl":
                    state, miss, _ = coverage("agency (intl)", page, kw)
                    row.update(section="agency (intl)", page=page, url=INTL[page][0],
                               decision="HAVE" if state != "missing" else "ADD",
                               coverage={"exact": "aynen geçiyor", "words": "kelimeleri geçiyor", "missing": "eksik"}[state],
                               missing_words=" ".join(miss), reason="İngilizce ajans sayfası")
                    continue
                platform = section
            else:
                platform = r["platform"]
                page, skip, note = grid_page(platform, r["service"], int(r["quantity"] or 0), r["modifier"], r["country"], archived)
                if skip or page is None:
                    row.update(decision="SKIP", reason=skip or "eşleşme yok")
                    continue
                row["reason"] = note
                section = platform
            if section in ("instagram", "tiktok", "youtube"):
                named = keyword_platform(kw, platform)   # a keyword that names another platform goes to that platform
                if named != platform:
                    platform = section = named
                    row["reason"] = (row["reason"] + "; " if row["reason"] else "") + "keyword başka platformu adlandırıyor"
            if platform == "tiktok" and "go live" in kw:
                page = "pack_1k"   # 1,000 followers unlock TikTok LIVE
            if page == "NEW:promote":
                if platform == "tiktok":
                    row.update(decision="NEW", section="tiktok", page=PROMOTE_NEW, reason="bu niyete sayfa yok")
                else:
                    row.update(decision="SKIP", reason="reklam ürünü araması (AdWords vb.)")
                continue
            if platform == "youtube":
                row.update(decision="NEW", section="youtube", page=page, reason="sterr-agency'de YouTube bölümü yok")
                continue
            if page.startswith("geo:") and platform != "instagram":
                row.update(decision="NEW", section=platform, page=page, reason="TikTok'ta ülke sayfası yok (yalnız Instagram'da var)")
                continue
            if page.startswith("pack_") and page not in DATA[platform]:
                row.update(decision="NEW", section=platform, page=page, reason="bu adet için hedef sayfası yok")
                continue
            if page.startswith("geo:") and page[4:] not in DATA[platform].get("geo", {}):
                row.update(decision="NEW", section=platform, page=page, reason="bu ülke sayfası yok")
                continue
            state, miss, page = coverage(section, page, kw)
            if state == "missing" and NON_TARGET_COUNTRY.search(kw):
                row.update(decision="SKIP", reason="hedef pazar değil (yerel ödeme/fiyat beklentisi uymuyor)")
                continue
            row.update(section=section, page=page, url=url(section, page),
                       decision="HAVE" if state != "missing" else "ADD",
                       coverage={"exact": "aynen geçiyor", "words": "kelimeleri geçiyor", "missing": "eksik"}[state],
                       missing_words=" ".join(miss))
    for row in out:
        if row["decision"] == "ADD":
            miss = set(row["missing_words"].split())
            row["priority"] = "küçük" if miss and miss <= MINOR else "ana"
    with open(HERE / "growsterr_harvest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    write_report(out, len(rows))
    print("keywords:", len(out), dict(Counter(r["decision"] for r in out)))


# ---------------------------------------------------------------------------------------------
# The report for the owner (Turkish)

HOW = {
    ("tiktok", "views"): "5 kısa ekleme: (1) 'high retention' SSS'i; (2) 'non drop / don't drop' SSS'i; (3) organic, targeted, high quality, safe ve legit kelimelerini taşıyan bir paragraf; (4) izlenmenin zamana yayıldığını anlatan cümle (slowly, drip feed, over time, auto views, multiple videos); (5) adet paragrafı: 1.000, 5.000, 10k, 100k ve 1 milyon izlenme arayanlara 'bine göre izlenme satmıyoruz, paket şöyle getirir'.",
    ("tiktok", "blog_more_views"): "'For You sayfasına düşmek / viral olmak' bölümü ve '0 izlenme neden olur' SSS'i.",
    ("tiktok", "likes"): "'Küçük paket satmıyoruz' bölümüne 100, 1.000, 5.000 ve 10k adetleri; gizli hesap SSS'i (hesap açık olmalı).",
    ("tiktok", "blog_views_money"): "Creator Rewards şartları (10k takipçi) ve 'takipçi satın almak para kazanmayı etkiler mi' SSS'i.",
    ("tiktok", "guide_buy"): "3 SSS: 'belli olur mu', 'işe yarar mı', 'güvenli mi'.",
    ("tiktok", "pack_1k"): "'Canlı yayın için 1.000 takipçi' bölümü: TikTok LIVE eşiği ve paketin oraya nasıl götürdüğü.",
    ("tiktok", "main"): "TikTok Shop hesapları için bir SSS; metinde '2026'.",
    ("tiktok", "packages"): "Paketin etkileşimi nasıl getirdiğini anlatan cümlede 'engagement'.",
    ("instagram", "agency"): "boost, engagement ve 'increase followers' ifadeleri tek paragrafta.",
    ("instagram", "real"): "'local' için hedef konum seçimini anlatan cümle; 'every day' ifadesi.",
    ("instagram", "likes"): "Gizli hesap SSS'i; metinde '2026'.",
    ("instagram", "packages"): "'followers and engagement' ifadesi.",
    ("instagram", "main"): "Metinde '2026'; 'viral' küçük bir ekleme.",
    ("instagram", "guide_buy"): "'Belli olur mu / kimse bilmeden' SSS'i.",
    ("instagram", "blog_more_views"): "'0 beğeni neden olur' bölümü.",
    ("instagram", "likes_reels"): "'video likes' ifadesi.",
    ("instagram", "geo:europe"): "Ülke listesine Yunanistan.",
    ("instagram", "pricing"): "'Ucuz ve hızlı' arayanlara tek cümle: ikisi birden bot demek.",
    ("creators", "main"): "Niş cümlesi (fashion, micro); tek bir 'nerede çalışıyoruz' cümlesi (ABD, İngiltere, Kanada, Avustralya, BAE, Avrupa). Şehir adı yok.",
    ("creators", "guide_signed"): "'apply', 'recruitment' ve 'gigs' ifadeleri.",
    ("creators", "guide_what"): "'Ajanslar nasıl kazanır' paragrafı (revenue).",
    ("agency (intl)", "intl:social-media-management"): "Instagram için yaptıklarımızı sayan cümle: branding, creative, personal branding, Reels.",
    ("agency (intl)", "intl:social-media-agency"): "'Instagram marketing agency' ve 'Instagram advertising agency' ifadeleri.",
    ("agency (intl)", "intl:social-media-agency-pricing"): "'Instagram marketing agency pricing' alt başlığı.",
}
NEW_GROUPS = [
    ("YouTube bölümü", lambda r: r["section"] == "youtube",
     "Sterr Agency'de YouTube yok (yalnız Instagram ve TikTok). Açılırsa aynı sayfa şablonu kullanılır; sipariş formuna ve Linksterr teslimatına YouTube eklenmesi gerekir. Karar senin."),
    ("TikTok paylaşım, kaydetme, repost sayfası", lambda r: "paylaşım" in r["page"],
     "Tek yeni sayfa: paylaşım, kaydetme ve repost'un pakette nasıl geldiğini anlatır (ayrı satılmaz)."),
    ("'TikTok Promote işe yarar mı' rehberi", lambda r: "Promote" in r["page"],
     "Tek yeni rehber: TikTok'un kendi Promote aracı ile gerçek kişilerle büyümenin farkı."),
    ("TikTok ülke sayfaları", lambda r: r["section"] == "tiktok" and r["page"].startswith("geo:"),
     "Instagram'da olan 5 ülke sayfasının (ABD, İngiltere, Avustralya, Avrupa, BAE) TikTok karşılığı."),
    ("20k, 50k ve 100k hedef sayfaları", lambda r: r["page"].startswith("pack_") and r["section"] != "youtube",
     "Şu an 1k, 2k, 3k, 5k ve 10k hedef sayfası var. Bu adetler için sayfa yok; keyword sayısı az, öncelik düşük."),
]


HEAD_TERMS = [
    ("buy instagram followers", "instagram", "main"), ("instagram followers", "instagram", "main"),
    ("buy tiktok followers", "tiktok", "main"), ("tiktok followers", "tiktok", "main"),
    ("buy followers", "instagram", "main"), ("follower bot", "instagram", "instant"),
    ("youtube subscribers", None, None),
]


def head_terms():
    """One table row per head term: the page that owns it and how many English pages mention it."""
    out = []
    for term, section, page in HEAD_TERMS:
        if section is None:
            out.append(f"| {term} | **Yok.** Sterr Agency'de YouTube bölümü yok; bu listenin en büyük boşluğu (bölüm 2). |")
            continue
        mentions = sum(1 for sec in ("instagram", "tiktok") for pg in section_pages(sec) if term in _text(sec, pg)[0])
        owner = url(section, page)
        own = term in _text(section, page)[0]
        if own:
            out.append(f"| {term} | `{owner}` sayfasında geçiyor; toplam {mentions} İngilizce sayfada var. |")
        else:
            bots = sum(1 for sec in ("instagram", "tiktok") for pg in section_pages(sec) if re.search(r"\bbots?\b", _text(sec, pg)[0]))
            out.append(f"| {term} | Bu kalıpla geçmiyor. Konu ('bot' kelimesi) {bots} İngilizce sayfada işleniyor; en yakın sayfa `{owner}`. "
                       "Guest post bu aramayı karşılıyor. |")
    return out


def write_report(out, clusters):
    by = defaultdict(list)
    for r in out:
        by[r["decision"]].append(r)
    add, new, skip, have = by["ADD"], by["NEW"], by["SKIP"], by["HAVE"]

    def kw(r):
        return r["keyword"] + (f" ({r['volume']})" if r["volume"] else "")

    lines = [
        "# Growsterr'dan Sterr Agency'ye taşınacak keyword'ler",
        "",
        f"Kaynak: growsterr'ın keyword planı (`docs/keywords/page-plan.csv`): {clusters} sayfa kümesi, {len(out)} İngilizce keyword. "
        "Her keyword, Sterr Agency'nin İngilizce sayfalarıyla niyet bazında eşleştirildi ve sayfa metninde geçip geçmediğine bakıldı. "
        "Tam liste: [`growsterr_harvest.csv`](growsterr_harvest.csv). Yeniden üretmek için: `python keywords/_growsterr_harvest.py`.",
        "",
        "Parantez içindeki sayılar aylık arama hacmidir (growsterr'ın listesinde olanlar için).",
        "",
        "| Karar | Keyword | Anlamı |",
        "|---|---|---|",
        f"| Mevcut sayfaya eklenecek | {len(add)} | Niyeti bir sayfamızla tutuyor ama o sayfada geçmiyor |",
        f"| Sayfası yok | {len(new)} | Niyetin karşılığı olan sayfa ya da bölüm bizde yok |",
        f"| Zaten karşılanıyor | {len(have)} | İlgili sayfada aynen ya da bütün kelimeleriyle geçiyor |",
        f"| Taşınmayacak | {len(skip)} | Kural dışı, satmadığımız bir şey, spam varyasyonu ya da ince sayfa |",
        "",
        "## Şu an hedeflediğimiz ana keyword'ler nerede duruyor",
        "",
        "| Keyword | Sterr Agency'de durum |",
        "|---|---|",
        *head_terms(),
        "",
        f"## 1. Mevcut sayfalara ekleyeceklerim ({len(add)})",
        "",
        "Yıldızlı (*) olanlar yeni bir niyet değil, küçük bir kelime farkı: cümle içine tek kelimeyle girer.",
        "",
    ]
    pages = defaultdict(list)
    for r in add:
        pages[(r["section"], r["page"], r["url"])].append(r)
    order = {"instagram": 0, "tiktok": 1, "creators": 2, "agency (intl)": 3}
    for (section, page, link), rs in sorted(pages.items(), key=lambda x: (order.get(x[0][0], 9), -len(x[1]))):
        lines += [f"### `{link}` ({len(rs)})", "",
                  "**Nasıl:** " + HOW.get((section, page), "İlgili paragrafa doğal cümleyle."), "",
                  "**Keyword'ler:** " + "; ".join(kw(r) + ("*" if r["priority"] == "küçük" else "") for r in rs), ""]
    lines += [f"## 2. Sayfası olmayanlar ({len(new)})", "",
              "Bunların niyeti hiçbir sayfamızla tutmuyor. Eklemek için sayfa ya da bölüm açmak gerekir.", ""]
    for title, test, note in NEW_GROUPS:
        rs = [r for r in new if test(r)]
        if not rs:
            continue
        lines += [f"### {title} ({len(rs)})", "", note, ""]
        if title.startswith("YouTube"):
            sub = defaultdict(list)
            for r in rs:
                sub[r["page"]].append(r)
            lines += ["| Açılacak sayfa (şablondaki karşılığı) | Keyword | Örnekler |", "|---|---|---|"]
            for page, items in sorted(sub.items(), key=lambda x: -len(x[1])):
                items.sort(key=lambda r: -int(r["volume"] or 0))
                lines.append(f"| {page} | {len(items)} | {'; '.join(kw(r) for r in items[:5])} |")
            lines.append("")
        else:
            lines += ["**Keyword'ler:** " + "; ".join(kw(r) for r in rs), ""]
    lines += [f"## 3. Taşımayacaklarım ({len(skip)})", "",
              "| Neden | Keyword | Örnekler |", "|---|---|---|"]
    reasons = defaultdict(list)
    for r in skip:
        reasons[r["reason"]].append(r)
    for reason, rs in sorted(reasons.items(), key=lambda x: -len(x[1])):
        lines.append(f"| {reason} | {len(rs)} | {'; '.join(r['keyword'] for r in rs[:3])} |")
    lines += ["", f"## 4. Zaten karşılananlar ({len(have)})", "",
              "Bu keyword'ler ilgili sayfada geçiyor; bir şey eklemek gerekmiyor.", "",
              "| Bölüm | Aynen geçiyor | Kelimeleri geçiyor |", "|---|---|---|"]
    sections = defaultdict(Counter)
    for r in have:
        sections[r["section"]][r["coverage"]] += 1
    for section, c in sorted(sections.items(), key=lambda x: order.get(x[0], 9)):
        lines.append(f"| {section} | {c['aynen geçiyor']} | {c['kelimeleri geçiyor']} |")
    lines.append("")
    (HERE / "GROWSTERR_HARVEST.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
