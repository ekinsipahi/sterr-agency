"""Small Turkish-language helpers: case-correct lowercasing, slugs and suffixes."""

BACK_VOWELS = set("aıou")
FRONT_VOWELS = set("eiöü")
HARD_CONSONANTS = set("fstkçşhp")  # "fıstıkçı şahap"

_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜâîû", "cgiosuCGIOSUaiu")


def tr_lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def tr_upper(text: str) -> str:
    return text.replace("i", "İ").replace("ı", "I").upper()


def ascii_fold(text: str) -> str:
    return text.translate(_ASCII)


def slugify_tr(text: str) -> str:
    out = []
    for ch in ascii_fold(tr_lower(text)):
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def _last_vowel(word: str) -> str:
    for ch in reversed(tr_lower(word)):
        if ch in BACK_VOWELS or ch in FRONT_VOWELS:
            return ch
    return "a"


def locative(name: str) -> str:
    """İstanbul → İstanbul'da, İzmir → İzmir'de, Muş → Muş'ta, Tokat → Tokat'ta."""
    last = tr_lower(name)[-1]
    d = "t" if last in HARD_CONSONANTS else "d"
    v = "a" if _last_vowel(name) in BACK_VOWELS else "e"
    return f"{name}'{d}{v}"


def ablative(name: str) -> str:
    """İstanbul → İstanbul'dan, Kars → Kars'tan."""
    last = tr_lower(name)[-1]
    d = "t" if last in HARD_CONSONANTS else "d"
    v = "a" if _last_vowel(name) in BACK_VOWELS else "e"
    return f"{name}'{d}{v}n"


def genitive(name: str) -> str:
    """İstanbul → İstanbul'un, Ankara → Ankara'nın, İzmir → İzmir'in."""
    low = tr_lower(name)
    lv = _last_vowel(name)
    harmony = {"a": "ı", "ı": "ı", "o": "u", "u": "u", "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[lv]
    buffer = "n" if low[-1] in BACK_VOWELS | FRONT_VOWELS else ""
    return f"{name}'{buffer}{harmony}n"
