"""Names shared by the growth app that must not pull in the 16-language content
(the admin and models import these at startup)."""

PLATFORMS = ("instagram", "tiktok")
PLATFORM_NAMES = {"instagram": "Instagram", "tiktok": "TikTok"}
PROFILE_URL = {"instagram": "https://www.instagram.com/{}/", "tiktok": "https://www.tiktok.com/@{}"}

# Landing pages for "buy 1000 / 2000 / … followers": how the agency package gets you there.
PACKAGE_PAGES = ("pack_1k", "pack_2k", "pack_3k", "pack_5k", "pack_10k")
# main is the hub: every other page links back to it and it links to all of them.
FOLLOWER_PAGES = ("main", "real", "pricing") + PACKAGE_PAGES + ("agency", "non_drop", "guide_speed", "guide_buy", "legit")
# Everything else we sell as part of the influencer packages, each with its own top-level
# path (subs value starting with "/"), plus the guides that lead to them.
SERVICE_PAGES = ("packages", "likes", "likes_monthly", "likes_gradual", "likes_reels", "views", "views_reels",
                 "views_story", "comments", "comments_custom")
BLOG_PAGES = ("instant", "blog_choose_likes", "blog_views_money", "blog_still_buy", "blog_comment_limit", "blog_more_views")
PAGES = FOLLOWER_PAGES + SERVICE_PAGES + BLOG_PAGES
GUIDES = ("guide_speed", "guide_buy") + BLOG_PAGES
# The hub groups pages like this; each group has a label in the UI ("groups").
GROUPS = {
    "followers": FOLLOWER_PAGES[1:],
    "packages": ("packages",),
    "likes": ("likes", "likes_monthly", "likes_gradual", "likes_reels"),
    "views": ("views", "views_reels", "views_story"),
    "comments": ("comments", "comments_custom"),
    "guides": BLOG_PAGES,
}
# Which package a page preselects in the order form.
PAGE_PLAN = {"pack_1k": "starter", "pack_2k": "rising", "pack_3k": "rising", "pack_5k": "pro", "pack_10k": "pro",
             "packages": "rising"}
# The platform-independent "influencer agency for creators" hub and its guides.
CREATOR_PAGES = ("main", "guide_what", "guide_red_flags", "guide_signed", "guide_small")

# Navbar dropdown label for both platforms, and the account link inside it.
FOLLOWERS_NAV = {
    "en": "Followers", "tr": "Takipçi", "de": "Follower", "nl": "Volgers", "fr": "Abonnés", "it": "Follower",
    "es": "Seguidores", "pl": "Obserwujący", "ru": "Подписчики", "uk": "Підписники", "ar": "متابعين",
    "sv": "Följare", "da": "Følgere", "no": "Følgere", "ro": "Urmăritori", "az": "İzləyici",
}
ACCOUNT_NAV = {
    "en": "My account", "tr": "Hesabım", "de": "Mein Konto", "nl": "Mijn account", "fr": "Mon compte", "it": "Il mio account",
    "es": "Mi cuenta", "pl": "Moje konto", "ru": "Мой аккаунт", "uk": "Мій акаунт", "ar": "حسابي",
    "sv": "Mitt konto", "da": "Min konto", "no": "Min konto", "ro": "Contul meu", "az": "Hesabım",
}

# Version of the terms a customer accepts on the order form (Terms 2a); bump it when 2a changes.
TERMS_VERSION = "2026-11-06"
