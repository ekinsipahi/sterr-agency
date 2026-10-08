"""The 81 provinces of Türkiye with plate code, region and market tier.

Tier drives copy only (competition level), never pricing or availability —
every province gets the same service.
"""
from dataclasses import dataclass
from functools import cached_property

from .turkish import ablative, genitive, locative, slugify_tr

METRO, LARGE, GROWING = "metro", "large", "growing"


@dataclass(frozen=True)
class City:
    plate: int
    name: str
    region: str
    tier: str = GROWING

    @cached_property
    def slug(self) -> str:
        return slugify_tr(self.name)

    @property
    def loc(self) -> str:  # İstanbul'da
        return locative(self.name)

    @property
    def abl(self) -> str:  # İstanbul'dan
        return ablative(self.name)

    @property
    def gen(self) -> str:  # İstanbul'un
        return genitive(self.name)

    @property
    def region_obj(self) -> "Region":
        return REGIONS[self.region]


@dataclass(frozen=True)
class Region:
    key: str
    name: str
    market: str  # one-line honest description of the local demand landscape


REGIONS = {
    r.key: r
    for r in [
        Region("marmara", "Marmara Bölgesi",
               "sanayi, ticaret ve hizmet sektörünün en yoğun olduğu, dijital reklam rekabetinin en sert yaşandığı bölge"),
        Region("ege", "Ege Bölgesi",
               "turizm, tarım-ihracat ve güçlü KOBİ ağıyla hem yerel hem ulusal satış potansiyeli taşıyan bölge"),
        Region("akdeniz", "Akdeniz Bölgesi",
               "turizm, tarım ve lojistiğin iç içe geçtiği, sezonluk talep dalgalarının iyi yönetilmesi gereken bölge"),
        Region("ic-anadolu", "İç Anadolu Bölgesi",
               "üniversite şehirleri, üretim merkezleri ve kamu ekosistemiyle istikrarlı, sadakati yüksek bir pazar"),
        Region("karadeniz", "Karadeniz Bölgesi",
               "güçlü yerel markalar ve güvene dayalı satın alma alışkanlıklarıyla, doğru konumlanan işletmenin hızla öne çıktığı bölge"),
        Region("dogu-anadolu", "Doğu Anadolu Bölgesi",
               "dijital rekabetin henüz düşük olduğu, erken davranan markaların arama sonuçlarını sahiplenebildiği bölge"),
        Region("guneydogu-anadolu", "Güneydoğu Anadolu Bölgesi",
               "hızla büyüyen genç nüfusu, ticaret ve üretim gücüyle dijital talebi her yıl artan bölge"),
    ]
}

_M, _E, _A, _I, _K, _D, _G = (
    "marmara", "ege", "akdeniz", "ic-anadolu", "karadeniz", "dogu-anadolu", "guneydogu-anadolu"
)

CITIES: list[City] = [
    City(1, "Adana", _A, LARGE), City(2, "Adıyaman", _G), City(3, "Afyonkarahisar", _E),
    City(4, "Ağrı", _D), City(5, "Amasya", _K), City(6, "Ankara", _I, METRO),
    City(7, "Antalya", _A, LARGE), City(8, "Artvin", _K), City(9, "Aydın", _E, LARGE),
    City(10, "Balıkesir", _M, LARGE), City(11, "Bilecik", _M), City(12, "Bingöl", _D),
    City(13, "Bitlis", _D), City(14, "Bolu", _K), City(15, "Burdur", _A),
    City(16, "Bursa", _M, LARGE), City(17, "Çanakkale", _M), City(18, "Çankırı", _I),
    City(19, "Çorum", _K), City(20, "Denizli", _E, LARGE), City(21, "Diyarbakır", _G, LARGE),
    City(22, "Edirne", _M), City(23, "Elazığ", _D), City(24, "Erzincan", _D),
    City(25, "Erzurum", _D, LARGE), City(26, "Eskişehir", _I, LARGE), City(27, "Gaziantep", _G, LARGE),
    City(28, "Giresun", _K), City(29, "Gümüşhane", _K), City(30, "Hakkari", _D),
    City(31, "Hatay", _A, LARGE), City(32, "Isparta", _A), City(33, "Mersin", _A, LARGE),
    City(34, "İstanbul", _M, METRO), City(35, "İzmir", _E, METRO), City(36, "Kars", _D),
    City(37, "Kastamonu", _K), City(38, "Kayseri", _I, LARGE), City(39, "Kırklareli", _M),
    City(40, "Kırşehir", _I), City(41, "Kocaeli", _M, LARGE), City(42, "Konya", _I, LARGE),
    City(43, "Kütahya", _E), City(44, "Malatya", _D, LARGE), City(45, "Manisa", _E, LARGE),
    City(46, "Kahramanmaraş", _A, LARGE), City(47, "Mardin", _G), City(48, "Muğla", _E, LARGE),
    City(49, "Muş", _D), City(50, "Nevşehir", _I), City(51, "Niğde", _I),
    City(52, "Ordu", _K), City(53, "Rize", _K), City(54, "Sakarya", _M, LARGE),
    City(55, "Samsun", _K, LARGE), City(56, "Siirt", _G), City(57, "Sinop", _K),
    City(58, "Sivas", _I), City(59, "Tekirdağ", _M, LARGE), City(60, "Tokat", _K),
    City(61, "Trabzon", _K, LARGE), City(62, "Tunceli", _D), City(63, "Şanlıurfa", _G, LARGE),
    City(64, "Uşak", _E), City(65, "Van", _D, LARGE), City(66, "Yozgat", _I),
    City(67, "Zonguldak", _K), City(68, "Aksaray", _I), City(69, "Bayburt", _K),
    City(70, "Karaman", _I), City(71, "Kırıkkale", _I), City(72, "Batman", _G),
    City(73, "Şırnak", _G), City(74, "Bartın", _K), City(75, "Ardahan", _D),
    City(76, "Iğdır", _D), City(77, "Yalova", _M), City(78, "Karabük", _K),
    City(79, "Kilis", _G), City(80, "Osmaniye", _A), City(81, "Düzce", _K),
]

CITY_BY_SLUG = {c.slug: c for c in CITIES}
CITIES_ALPHA = sorted(CITIES, key=lambda c: slugify_tr(c.name))


def cities_in_region(region_key: str, exclude: City | None = None) -> list[City]:
    return [c for c in CITIES_ALPHA if c.region == region_key and c != exclude]


def cities_by_region() -> list[tuple[Region, list[City]]]:
    return [(r, cities_in_region(k)) for k, r in REGIONS.items()]
