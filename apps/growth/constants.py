"""Names shared by the growth app that must not pull in the 16-language content
(the admin and models import these at startup)."""

PLATFORMS = ("instagram", "tiktok")
PLATFORM_NAMES = {"instagram": "Instagram", "tiktok": "TikTok"}
PROFILE_URL = {"instagram": "https://www.instagram.com/{}/", "tiktok": "https://www.tiktok.com/@{}"}

PACKAGE_PAGES = ("pack_1k", "pack_2k", "pack_3k", "pack_5k", "pack_10k")
# main is the hub: every other page links back to it and it links to all of them.
PAGES = ("main", "real", "pricing") + PACKAGE_PAGES + ("agency", "non_drop", "guide_speed", "guide_buy", "legit")
GUIDES = ("guide_speed", "guide_buy")
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
