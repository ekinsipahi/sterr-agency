"""Classify the Instagram-follower keyword export by intent for the $49/mo organic growth product."""
import csv, re, sys
from collections import Counter, defaultdict

SRC, OUT = sys.argv[1], sys.argv[2]
rows = []
for line in open(SRC, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    kw, *rest = line.split("|")
    vol, cpc, pd = (rest + ["", "", ""])[:3]
    rows.append((kw.strip(), vol, cpc, pd))

def has(kw, *words):
    return any(re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", kw) for w in words)

BRANDS = ["buzzoid", "passthevote", "pass the vote", "stormlikes", "famety", "media mister", "goread", "celebian",
          "superviral", "socialwick", "useviral", "stillviral", "still viral", "iginstant", "g2g", "g2a", "eldorado",
          "fameviso", "myinstafollow", "myinsfollower", "mysocialfollowing", "growthx", "social daddy", "promotid",
          "recurpost", "owlet", "businessinsider", "siteframe", "upwork", "trustpilot", "shopee", "etsy",
          "buyfollowersinstag", "kylie jenner", "give me boost", "rizz", "50 cent", "365", "qqtube", "buzz"]
LOW_ARPU = ["india", "indian", "pakistan", "nigeria", "naira", "bangladesh", "bd", "nepal", "kenya", "uganda",
            "philippines", "egypt", "vietnam", "sri lanka", "malaysia", "south africa", "sa", "jaipur", "mumbai",
            "paytm", "upi", "gpay", "gcash", "mpesa", "mobile money", "rupees", "inr", "php", "indian currency"]
GEO = {"usa": ["usa"], "uk": ["uk", "the uk"], "australia": ["australia", "aud"], "europe": ["europe", "germany", "romania"],
       "uae": ["uae", "dubai"]}

PAGES = {
    "main": "/en/instagram-followers/",
    "pricing": "/en/instagram-followers/pricing/",
    "guide_buy": "/en/instagram-followers/should-you-buy-instagram-followers/",
    "guide_speed": "/en/instagram-followers/how-fast-can-you-grow/",
    **{f"geo_{g}": f"/en/instagram-followers/{g}/" for g in GEO},
}

def classify(kw):
    k = kw.lower()
    # 1) excluded: other products, competitor brands, free/hack/app/tools, reseller panels, low-ARPU markets
    if k == "buy instagram followers c2 a0" or k == "buy instagram followers r" or "hilesi" in k or "kaise" in k:
        return "exclude", "junk / other language", "X"
    if has(k, "instagram account", "followers account") or k == "buy ig with followers":
        return "exclude", "buying accounts, different product", "X"
    if (has(k, "likes", "views", "tiktok", "yt", "ytviews", "viewer") and not has(k, "followers")) or has(k, "yt views", "ytviews", "tiktok", "yt", "views", "viewer"):
        return "exclude", "likes / views / other platform", "X"
    if any(has(k, b) for b in BRANDS) or "buzzoid.com" in k:
        return "exclude", "competitor brand (navigational)", "N"
    if has(k, "not indian"):
        return "main", "real / quality", "T"
    if any(has(k, g) for g in LOW_ARPU):
        return "exclude", "low-ARPU market or local payment ($49 doesn't fit)", "T"
    if has(k, "free", "trial", "apk", "mod", "hashtags", "list", "data", "in order", "checker", "no login",
           "without login", "no sign up", "discord", "telegram", "reddit", "panel", "smm", "ssm"):
        return "exclude", "free / tool / forum / reseller intent", "X"
    if has(k, "app", "iphone", "android"):
        return "exclude", "wants a mobile app", "X"
    # 2) informational: should I buy, does it work, bans, legality
    if re.match(r"^(can|do|does|is|what|if|how|why)\b", k) or has(k, "worth it", "legal", "safe", "banned", "ban",
            "legit", "legitimate", "ruin", "without getting banned", "without people knowing", "are they real"):
        if has(k, "legit website"):
            return "main", "trust / reviews", "C"
        return "guide_buy", "should you buy / safety", "I"
    # 3) geo (location targeting is a real feature)
    for g, words in GEO.items():
        if any(has(k, w) for w in words):
            return f"geo_{g}", f"geo: {g}", "T"
    # 4) price / payment
    if has(k, "cheap", "cheapest", "low price", "low cost", "lowest price", "price", "cost", "how much", "discount",
           "package", "dollar", "money", "paid", "under 80", "under 150", "very cheap") or re.search(r"\$|\d\$", k) \
            or has(k, "paypal", "apple pay", "credit card", "debit card", "klarna", "crypto", "bitcoin", "instagram cheap"):
        return "pricing", "price / payment", "T"
    # 5) quantity and instant/fast: our honest answer is organic speed (900–3,000/mo)
    num = re.sub(r"\b20(25|26)\b", "", k)
    if re.search(r"\b\d+(\s?000|k)?\b|million", num) or has(k, "custom amount"):
        return "guide_speed", "follower count goal", "C"
    if has(k, "instant", "fast", "quick", "now", "instant delivery", "fast delivery", "with instant"):
        return "guide_speed", "speed (we are gradual, not instant)", "C"
    # 6) core: real / organic / gradual / targeted / quality / reviews / generic
    if has(k, "review", "reviews", "trusted", "best", "top", "site", "website", "platform", "where", "place", "link", "com", "web", "online"):
        return "main", "trust / where to buy", "C"
    return "main", "real / organic / generic", "T"

out = []
for kw, vol, cpc, pd in rows:
    page, reason, intent = classify(kw)
    out.append({"keyword": kw, "volume": vol, "cpc_usd": cpc, "pd": pd, "intent": intent, "cluster": reason,
                "target_page": PAGES.get(page, "— (exclude)"), "group": page})
order = list(PAGES) + ["exclude"]
out.sort(key=lambda r: (order.index(r["group"]), -int(r["volume"] or 0), r["keyword"]))
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["keyword", "volume", "cpc_usd", "pd", "intent", "cluster", "target_page"])
    w.writeheader()
    for r in out:
        w.writerow({k: r[k] for k in w.fieldnames})
c = Counter(r["group"] for r in out)
print(len(out), dict(c))
by = defaultdict(Counter)
for r in out: by[r["group"]][r["cluster"]] += 1
for g in order: print(g, dict(by[g]))
