"""Programmatic-SEO keyword clusters: one landing page per (cluster × province).

Every cluster maps 1:1 to a head keyword from the keyword research
(see keywords/KEYWORDS.md). Variants are the secondary queries the same page
targets, so city pages never cannibalise each other.

Copy placeholders: {city} İstanbul · {loc} İstanbul'da · {abl} İstanbul'dan ·
{gen} İstanbul'un · {region} Marmara Bölgesi · {market} region one-liner.
"""
import hashlib
from dataclasses import dataclass, field

from .cities import City

TITLE_MAX = 60
DESC_MAX = 158


@dataclass(frozen=True)
class Cluster:
    slug: str
    name: str             # "Sosyal Medya Ajansı"
    head: str             # national head keyword
    volume: str           # national monthly volume from research
    city_keywords: tuple  # keyword templates targeted on each city page
    titles: tuple         # ordered by preference; first one that fits wins
    descriptions: tuple
    h1: str
    intros: tuple         # rotated per city for unique copy
    national_intro: str
    deliverables: tuple   # (title, body)
    faqs: tuple           # (question, answer)
    pricing_heading: str
    related_guides: tuple = field(default_factory=tuple)


CLUSTERS = [
    Cluster(
        slug="dijital-pazarlama-ajansi",
        name="Dijital Pazarlama Ajansı",
        head="dijital pazarlama ajansı",
        volume="2.4K",
        city_keywords=(
            "dijital pazarlama ajansı {city}",
            "{city} dijital pazarlama ajansı",
            "dijital pazarlama ajansları {city}",
            "{city} dijital pazarlama ajansları",
            "dijital pazarlama ajansi {ascii}",
            "dijital pazarlama ajansı fiyatları {city}",
            "{city} dijital ajans",
        ),
        titles=(
            "{city} Dijital Pazarlama Ajansı | Müşteri Getiren Sistem",
            "Dijital Pazarlama Ajansı {city} | Sterr Agency",
            "{city} Dijital Pazarlama Ajansı | Sterr",
            "Dijital Pazarlama Ajansı {city}",
        ),
        descriptions=(
            "{loc} dijital pazarlama ajansı mı arıyorsunuz? Reklam, SEO ve içeriği tek sistemde birleştirip size müşteri getiriyoruz. Aylık rapor, net hedef.",
            "{city} için performans odaklı dijital pazarlama: Google & Meta reklam, SEO, içerik üretimi. Beğeni değil, satış ve randevu. Ön görüşme alın.",
            "{loc} işletmenize müşteri getiren dijital pazarlama. Reklam + SEO + AI destekli içerik yayılımı. Paketler aylık 50.000 ₺'den.",
        ),
        h1="{city} Dijital Pazarlama Ajansı",
        intros=(
            "{loc} dijital pazarlama ajansı seçerken sorulacak tek soru var: bu ajans bana kaç müşteri getirecek? Sterr Agency olarak reklamı, SEO'yu ve içerik üretimini ayrı ayrı satmıyoruz; hepsini {gen} pazarına göre kurgulanmış tek bir büyüme sistemine bağlıyoruz.",
            "{city} merkezli ya da {loc} müşterisi olan işletmeler için çalışıyoruz. Amacımız takipçi sayısını değil, telefonunuzun kaç kez çaldığını artırmak. Reklam, arama motoru optimizasyonu ve özel içerik ekibimiz aynı hedef için çalışır.",
            "Bir dijital pazarlama ajansının işi rapor süslemek değil, müşteri getirmektir. {abl} gelen talepleri ölçüyor, fiyat odaklı kitleyi eliyor ve size yalnızca satın almaya hazır kişileri yönlendiriyoruz.",
        ),
        national_intro="Türkiye'nin 81 ilinde işletmelere reklam, SEO, sosyal medya ve AI destekli içerik yayılımını tek bir büyüme sisteminde sunuyoruz. Konumunuz fark etmez; hedefimiz her ay ölçülebilir yeni müşteri.",
        deliverables=(
            ("Google & Meta reklam yönetimi", "{city} ve çevresindeki doğru kitleye, satın alma niyeti yüksek anahtar kelimelerle ulaşan kampanyalar."),
            ("Türkçe SEO & programatik SEO", "Müşterilerinizin Google'da gerçekten aradığı ifadeler için sıralama alan sayfa mimarisi."),
            ("AI destekli içerik yayılımı", "Forumlar, soru-cevap platformları ve sektörel mecralarda markanızı konuşturan özel içerik çalışmaları."),
            ("Kalite filtresi olan funnel", "Fiyat avcılarını eleyen, sadece nitelikli talebi size ileten başvuru akışı."),
            ("İçerik prodüksiyonu", "İçeriğiniz yoksa ekibimiz gelir; video, fotoğraf ve metin üretimini biz yaparız."),
            ("Aylık performans raporu", "Harcanan her liranın kaç görüşmeye ve satışa dönüştüğünü gösteren şeffaf rapor."),
        ),
        faqs=(
            ("{loc} dijital pazarlama ajansı ile çalışmak için ofisinize gelmem gerekiyor mu?", "Hayır. Türkiye'nin 81 ilinde uzaktan çalışıyoruz; strateji görüşmeleri online yapılır. İçerik çekimi gerektiğinde ekibimiz {city} dahil bulunduğunuz yere gelir."),
            ("Dijital pazarlama ajansı fiyatları {loc} ne kadar?", "Paketlerimiz aylık 50.000 ₺'den başlar. İlk ay peşin başlanır, sonraki aylar her ay raporla birlikte faturalandırılır. Reklam bütçesi hizmet bedelinden ayrıdır."),
            ("Ne kadar sürede sonuç alırım?", "Reklam kanalında ilk nitelikli talepler genellikle ilk haftalarda gelir. SEO ve marka yayılımı ise 3–6 ay içinde birikerek büyür; bu yüzden ikisini birlikte kurgularız."),
            ("Hangi sektörlerle çalışıyorsunuz?", "Özel ders öğretmenlerinden e-ticaret markalarına, kliniklerden profesyonel hizmetlere kadar talebin ölçülebildiği her sektörle çalışıyoruz."),
        ),
        pricing_heading="{city} dijital pazarlama ajansı fiyatları",
        related_guides=("dijital-pazarlama-ajansi-ne-is-yapar", "dijital-pazarlama-ajansi-fiyatlari"),
    ),
    Cluster(
        slug="sosyal-medya-ajansi",
        name="Sosyal Medya Ajansı",
        head="sosyal medya ajansı",
        volume="2.4K",
        city_keywords=(
            "sosyal medya ajansı {city}",
            "{city} sosyal medya ajansı",
            "{city} sosyal medya ajans",
            "sosyal medya ajansları {city}",
            "sosyal medya ajans {city}",
            "sosyal medya ajansi {ascii}",
            "sosyal medya ajansı fiyatları {city}",
        ),
        titles=(
            "{city} Sosyal Medya Ajansı | Takipçi Değil Müşteri",
            "Sosyal Medya Ajansı {city} | Sterr Agency",
            "{city} Sosyal Medya Ajansı | Sterr",
            "Sosyal Medya Ajansı {city}",
        ),
        descriptions=(
            "{loc} sosyal medya ajansı arıyorsanız: beğeni değil müşteri getiren içerik + reklam sistemi kuruyoruz. İçerik ekibimiz size gelir. Ön görüşme alın.",
            "{city} sosyal medya ajansı Sterr: Instagram, TikTok ve Meta reklamlarını satışa bağlayan strateji. Aylık rapor, net hedef, 81 ilde hizmet.",
            "{city} için sosyal medya yönetimi, içerik prodüksiyonu ve reklam. Takipçi toplamıyoruz; size talep getiriyoruz. Paketler 50.000 ₺'den.",
        ),
        h1="{city} Sosyal Medya Ajansı",
        intros=(
            "{loc} sosyal medya ajansı çok, müşteri getiren ajans az. Biz paylaşım takvimi doldurmak için değil, {gen} kitlesinin sizi seçmesi için içerik üretiyoruz; her gönderi, her reklam bir başvuru akışına bağlanır.",
            "Sosyal medya bir vitrin değil, bir satış kanalıdır. {city} işletmeleri için Instagram, TikTok ve Meta reklamlarını tek bir stratejiyle yönetiyor, fiyatçı kitleyi eleyip nitelikli talebi size yönlendiriyoruz.",
            "İçeriğiniz mi yok? Sorun değil. Özel içerik ekibimiz {loc} markanız için çekim yapar, metni yazar, reklamı kurar. Siz yalnızca gelen müşterilerle ilgilenirsiniz.",
        ),
        national_intro="Türkiye genelinde işletmelere sosyal medya yönetimi, içerik prodüksiyonu ve performans reklamcılığını tek elden sunuyoruz. Hedef takipçi değil, müşteri.",
        deliverables=(
            ("Strateji & içerik takvimi", "{gen} kitlesinin neye tepki verdiğini analiz edip size özel içerik planı çıkarıyoruz."),
            ("İçerik prodüksiyonu", "Reels, TikTok videoları, ürün ve hizmet çekimleri — içeriğiniz yoksa biz üretiriz."),
            ("Meta & TikTok reklamları", "Konum, ilgi alanı ve davranış hedeflemesiyle doğru kişiye ulaşan dönüşüm kampanyaları."),
            ("Topluluk & DM yönetimi", "Gelen mesajları kaçırmadan cevaplayan, talebi satışa yönlendiren akış."),
            ("Marka konumlandırma", "Sizi rakiplerinizden ayıran net bir mesaj ve görsel dil."),
            ("Aylık rapor", "Erişim değil; kaç mesaj, kaç randevu, kaç satış geldiğini gösteren rapor."),
        ),
        faqs=(
            ("{loc} sosyal medya ajansı fiyatları ne kadar?", "Sosyal medya dahil paketlerimiz aylık 50.000 ₺'den başlar. İçerik prodüksiyonu, reklam yönetimi ve raporlama pakete dahildir; reklam bütçesi ayrıca planlanır."),
            ("İçerik çekimi için {city} işletmeme gelir misiniz?", "Evet. İçeriğiniz yoksa özel içerik ekibimiz Türkiye'nin 81 ilinde yerinde çekim planlar."),
            ("Hangi platformları yönetiyorsunuz?", "Instagram, Facebook, TikTok, YouTube ve LinkedIn. Sektörünüze göre en çok müşteri getiren kanala odaklanırız."),
            ("Sözleşme süresi ne kadar?", "Aylık abonelik modeliyle çalışıyoruz: ilk ay peşin başlanır, sonrasında her ay raporlanır ve faturalandırılır."),
        ),
        pricing_heading="{city} sosyal medya ajansı fiyatları",
        related_guides=("sosyal-medya-ajansi-nedir", "sosyal-medya-ajansi-fiyatlari", "sosyal-medya-ajans-sozlesmesi"),
    ),
    Cluster(
        slug="sosyal-medya-yonetimi-ajansi",
        name="Sosyal Medya Yönetimi Ajansı",
        head="sosyal medya yönetimi ajans",
        volume="30",
        city_keywords=(
            "sosyal medya yönetimi ajansı {city}",
            "{city} sosyal medya yönetimi",
            "sosyal medya yönetimi {city}",
            "{city} sosyal medya yönetimi ajansı",
            "sosyal medya yonetimi {ascii}",
        ),
        titles=(
            "{city} Sosyal Medya Yönetimi | Satış Odaklı Ajans",
            "Sosyal Medya Yönetimi {city} | Sterr Agency",
            "{city} Sosyal Medya Yönetimi | Sterr",
            "Sosyal Medya Yönetimi {city}",
        ),
        descriptions=(
            "{loc} sosyal medya yönetimi: içerik planı, çekim, paylaşım, DM ve reklam tek ekipte. Hesabınızı satış kanalına dönüştürüyoruz. Ön görüşme alın.",
            "{city} işletmeleri için uçtan uca sosyal medya yönetimi. İçerik ekibimiz size gelir, reklamı biz kurarız, müşteriler size gelir.",
            "{city} sosyal medya yönetimi ajansı Sterr: takvim, prodüksiyon, reklam ve aylık rapor. Beğeni değil, talep ölçüyoruz.",
        ),
        h1="{city} Sosyal Medya Yönetimi",
        intros=(
            "{loc} sosyal medya yönetimi, düzenli paylaşım yapmaktan ibaret değil. Hesabınızı; içerik, reklam ve mesaj yönetimiyle birlikte çalışan, ölçülebilir bir satış kanalına dönüştürüyoruz.",
            "Sosyal medyanızı kendiniz yönetmeye çalışırken işinize vakit kalmıyorsa doğru yerdesiniz. {city} işletmeleri için planlama, çekim, paylaşım ve reklamı tek ekipte topluyoruz.",
            "Tutarlı bir marka dili, düzenli üretim ve satışa bağlanan reklam. {gen} rekabetçi pazarında öne çıkmak için sosyal medya yönetimini bir sistem olarak kuruyoruz.",
        ),
        national_intro="Uçtan uca sosyal medya yönetimi: planlama, içerik prodüksiyonu, paylaşım, topluluk yönetimi ve reklam — Türkiye'nin 81 ilinde.",
        deliverables=(
            ("Aylık içerik planı", "Sektörünüze ve {gen} kitlesine göre hazırlanan, onayınıza sunulan içerik takvimi."),
            ("Çekim & kurgu", "Reels, hikâye ve gönderi formatlarında profesyonel prodüksiyon."),
            ("Paylaşım & optimizasyon", "Doğru saat, doğru format, doğru açıklama — algoritmayla uyumlu yayın."),
            ("DM & yorum yönetimi", "Talepleri kaçırmayan, hızlı ve marka diline uygun cevaplar."),
            ("Reklam yönetimi", "Organik içeriği reklamla büyüten, dönüşüm odaklı kampanyalar."),
            ("Rapor & strateji toplantısı", "Her ay neyin işe yaradığını birlikte konuşup planı güncelliyoruz."),
        ),
        faqs=(
            ("{loc} sosyal medya yönetimi hizmetine neler dahil?", "İçerik planı, prodüksiyon, paylaşım, DM/yorum yönetimi, reklam kurulumu ve aylık rapor. Paket seviyesine göre içerik adedi ve kanal sayısı değişir."),
            ("Hesaplarımın erişimi bende kalır mı?", "Evet. Tüm hesaplar ve reklam hesapları sizin mülkiyetinizde kalır; biz yetkili kullanıcı olarak çalışırız."),
            ("Paylaşımları onaylayabilir miyim?", "Evet. Aylık içerik planı yayından önce onayınıza sunulur."),
            ("Fiyatlar nasıl belirleniyor?", "Paketlerimiz aylık 50.000 ₺'den başlar; kanal sayısı, içerik hacmi ve reklam kapsamına göre üç seviye sunuyoruz."),
        ),
        pricing_heading="{city} sosyal medya yönetimi fiyatları",
        related_guides=("sosyal-medya-ajansi-nedir", "sosyal-medya-ajansi-fiyatlari"),
    ),
    Cluster(
        slug="dijital-pazarlama-uzmani",
        name="Dijital Pazarlama Uzmanı",
        head="dijital pazarlama uzmanı",
        volume="720",
        city_keywords=(
            "dijital pazarlama uzmanı {city}",
            "{city} dijital pazarlama uzmanı",
            "dijital pazarlama uzmanları {city}",
            "dijital pazarlama uzmani {ascii}",
            "{city} dijital pazarlama uzmanlığı",
        ),
        titles=(
            "{city} Dijital Pazarlama Uzmanı | Tek Kişi Değil, Ekip",
            "Dijital Pazarlama Uzmanı {city} | Sterr Agency",
            "{city} Dijital Pazarlama Uzmanı | Sterr",
            "Dijital Pazarlama Uzmanı {city}",
        ),
        descriptions=(
            "{loc} dijital pazarlama uzmanı mı arıyorsunuz? Tek bir uzman maaşına reklam, SEO, içerik ve strateji uzmanlarından oluşan bir ekip. Ön görüşme alın.",
            "{city} için dijital pazarlama uzmanları: reklam, SEO, sosyal medya ve içerik ekibi tek pakette. İşe alım yükü yok, sonuç odaklı sistem var.",
            "{loc}ki işletmenize kıdemli dijital pazarlama uzmanları. Google, Meta, SEO ve içerik — aylık rapor, net hedef. Paketler 50.000 ₺'den.",
        ),
        h1="{city} Dijital Pazarlama Uzmanı",
        intros=(
            "{loc} tek bir dijital pazarlama uzmanı işe almak; maaş, eğitim, yazılım ve deneme-yanılma maliyeti demek. Sterr ile aynı bütçeye reklam, SEO, içerik ve strateji uzmanlarından oluşan kıdemli bir ekip kazanırsınız.",
            "İyi bir dijital pazarlama uzmanı her şeyi bilemez; iyi bir ekip bilir. {city} işletmeleri için reklam uzmanı, SEO uzmanı ve içerik ekibi aynı hedef için çalışır.",
            "Kurum içi uzman arayışınız aylar sürebilir. Biz ilk hafta çalışmaya başlar, {gen} pazarını analiz eder ve müşteri getiren sistemi kurarız.",
        ),
        national_intro="Tek bir uzman yerine reklam, SEO, içerik ve strateji uzmanlarından oluşan bir ekip. Türkiye'nin 81 ilindeki işletmelere hizmet veriyoruz.",
        deliverables=(
            ("Performans reklam uzmanı", "Google Ads ve Meta kampanyalarınızı günlük optimize eden uzman."),
            ("SEO uzmanı", "Teknik SEO, içerik mimarisi ve programatik SEO ile organik trafik."),
            ("İçerik & prodüksiyon ekibi", "Metin, video ve görsel üretimi; gerekirse yerinde çekim."),
            ("Strateji direktörü", "Sektörünüzü, rakiplerinizi ve müşterinizi analiz edip yön çizen kıdemli bakış."),
            ("Veri & ölçümleme", "GA4, Search Console ve dönüşüm takibi kurulumu; her şeyi ölçeriz."),
            ("Aylık rapor", "Neyin çalıştığını ve sonraki ayın planını netleştiren rapor."),
        ),
        faqs=(
            ("{loc} dijital pazarlama uzmanı işe almak yerine neden ajans?", "Tek uzman maaşı ve yan maliyetleriyle kıyaslandığında, aynı bütçeyle farklı alanlarda uzmanlaşmış bir ekibe ve kurumsal araçlara erişirsiniz."),
            ("Uzmanlarınızla doğrudan iletişim kurabilir miyim?", "Evet. Size atanan proje sorumlusu ve WhatsApp hattı üzerinden doğrudan iletişim kurarsınız."),
            ("Hangi araçları kullanıyorsunuz?", "Google Ads, Meta Business, GA4, Search Console, SEO araçları ve kendi AI içerik altyapımız."),
            ("Ücretlendirme nasıl?", "Aylık abonelik: paketler 50.000 ₺'den başlar, ilk ay peşin, sonraki aylar aylık faturalandırılır."),
        ),
        pricing_heading="{city} dijital pazarlama uzmanı maliyeti",
        related_guides=("dijital-pazarlama-uzmani-nedir",),
    ),
]

CLUSTER_BY_SLUG = {c.slug: c for c in CLUSTERS}

# Market-size copy. Tier only changes the argument, never the offer.
TIER_COPY = {
    "metro": "{city}, Türkiye'nin en rekabetçi dijital pazarlarından biri. Tıklama maliyetleri yüksek, her sektörde onlarca rakip aynı müşteriye ulaşmaya çalışıyor. Burada kazanan, en çok harcayan değil; bütçesini en isabetli kullanan ve fiyatçıyı en erken eleyen marka oluyor.",
    "large": "{city} hızla büyüyen ve dijital rekabetin her yıl sertleştiği bir pazar. Rakipleriniz reklama yeni yeni yatırım yaparken; reklam, SEO ve içerik yayılımını birlikte kuran işletmeler arama sonuçlarında kalıcı bir yer ediniyor.",
    "growing": "{loc} dijital rekabet henüz düşük; bu büyük bir fırsat. Arama sonuçlarını ve sosyal medya akışını erken sahiplenen işletme, rakipleri harekete geçtiğinde çoktan bölgenin bilinen markası olmuş oluyor.",
}

# Closing paragraph that works the secondary keyword variants in naturally.
CLOSING = {
    "dijital-pazarlama-ajansi": "{city} dijital pazarlama ajansları arasında karar verirken portföye, raporlama şeffaflığına ve müşteri getirme sistemine bakın. Dijital pazarlama ajansı fiyatları {loc} kapsamına göre değişir; biz her paketin içeriğini açıkça yazıyor ve her ay ne getirdiğimizi raporluyoruz.",
    "sosyal-medya-ajansi": "{city} sosyal medya ajansları çoğunlukla paylaşım adedi satar. Biz ise içerik, reklam ve mesaj yönetimini tek bir satış akışına bağlarız. Sosyal medya ajansı fiyatları {loc} kapsamına göre değişir; paketlerimizin neleri içerdiğini aşağıda açıkça görebilirsiniz.",
    "sosyal-medya-yonetimi-ajansi": "{loc} sosyal medya yönetimi hizmeti alırken hesapların sizde kalmasına, içerik onay sürecine ve raporlamanın satış odaklı olmasına dikkat edin. Sosyal medya yönetimi ajansı olarak bu üçünü sözleşmemizde garanti altına alıyoruz.",
    "dijital-pazarlama-uzmani": "{city} dijital pazarlama uzmanları arasında seçim yapmak yerine, farklı alanlarda uzmanlaşmış bir ekiple çalışın. Dijital pazarlama uzmanlığı gerektiren her işi — reklam, SEO, içerik, analiz — tek bir aylık bedelle yönetiyoruz.",
}


def _ctx(city: City) -> dict:
    from .turkish import ascii_fold, tr_lower

    return {
        "city": city.name,
        "loc": city.loc,
        "abl": city.abl,
        "gen": city.gen,
        "region": city.region_obj.name,
        "market": city.region_obj.market,
        "ascii": ascii_fold(tr_lower(city.name)),
    }


def _pick(options: tuple, city: City, salt: str) -> str:
    h = int(hashlib.md5(f"{salt}:{city.slug}".encode()).hexdigest(), 16)
    return options[h % len(options)]


def _fit(templates: tuple, ctx: dict, limit: int) -> str:
    for tpl in templates:
        text = tpl.format(**ctx)
        if len(text) <= limit:
            return text
    return min((t.format(**ctx) for t in templates), key=len)


def _rotated(templates: tuple, city: City, salt: str) -> tuple:
    """Start from a per-city choice so neighbouring pages don't share a meta line."""
    h = int(hashlib.md5(f"{salt}:{city.slug}".encode()).hexdigest(), 16) % len(templates)
    return templates[h:] + templates[:h]


def city_page(cluster: Cluster, city: City) -> dict:
    ctx = _ctx(city)
    fmt = lambda s: s.format(**ctx)  # noqa: E731
    return {
        "title": _fit(cluster.titles, ctx, TITLE_MAX),
        "description": _fit(_rotated(cluster.descriptions, city, cluster.slug), ctx, DESC_MAX),
        "h1": fmt(cluster.h1),
        "intro": fmt(_pick(cluster.intros, city, cluster.slug)),
        "keywords": [fmt(k) for k in cluster.city_keywords],
        "deliverables": [(fmt(t), fmt(b)) for t, b in cluster.deliverables],
        "faqs": [(fmt(q), fmt(a)) for q, a in cluster.faqs],
        "pricing_heading": fmt(cluster.pricing_heading),
        "tier_text": fmt(TIER_COPY[city.tier]),
        "closing": fmt(CLOSING[cluster.slug]),
        "ctx": ctx,
    }
