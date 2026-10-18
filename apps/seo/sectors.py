"""Sector landing pages — the verticals we bring customers to."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Sector:
    slug: str
    name: str
    title: str
    description: str
    headline: str
    lede: str
    pains: tuple        # what the business struggles with
    system: tuple       # (title, body) — how we bring customers
    searches: tuple     # example Turkish searches we rank/advertise for
    faqs: tuple


SECTORS = [
    Sector(
        slug="ozel-ders-ogretmenleri",
        name="Özel Ders Öğretmenleri",
        title="Özel Ders Öğretmenleri İçin Dijital Pazarlama | Sterr",
        description="Özel ders öğretmenlerine öğrenci getiriyoruz: Google, sosyal medya ve SEO ile dolu bir ders takvimi. Fiyatçı veliyi eleyen başvuru sistemi.",
        headline="Takviminiz boş kalmasın. Öğrenciyi biz getirelim.",
        lede="Özel ders pazarı, platform komisyonları ve fiyat kırmaya çalışan velilerle dolu. Kendi markanızı kurup, doğrudan size ulaşan ve değerinizi bilen öğrencileri getiriyoruz.",
        pains=(
            "Platformlara yüksek komisyon ödemek",
            "Sürekli pazarlık yapan veliler",
            "Dönem arası boşalan takvim",
            "Tavsiyeye bağlı, öngörülemeyen gelir",
        ),
        system=(
            ("Kişisel marka", "Branşınızı, başarı hikâyelerinizi ve yönteminizi anlatan güçlü bir profil ve web sayfası."),
            ("Google'da görünürlük", "Reklam ve SEO ile sizi kolay bulunur kılıyoruz."),
            ("Kalite filtresi", "Seviye, hedef sınav ve bütçe soran başvuru formu — ciddi veliler size ulaşır."),
            ("Sezon planlaması", "LGS, YKS ve dönem başı talep dalgalarına göre önceden kurulan kampanyalar."),
        ),
        searches=("matematik özel ders", "fizik özel ders", "YKS özel ders", "LGS özel ders", "online özel ders", "birebir özel ders fiyatları"),
        faqs=(
            ("Bireysel öğretmenlerle de çalışıyor musunuz?", "Evet. Bireysel öğretmenler, eğitim koçları ve etüt merkezleriyle çalışıyoruz."),
            ("Online ders veriyorum, 81 ilden öğrenci gelir mi?", "Evet. Online derste hedeflemeyi Türkiye geneline açar, yüz yüze derste ise bulunduğunuz il ve ilçelere odaklanırız."),
        ),
    ),
    Sector(
        slug="matematik-ogretmenleri",
        name="Matematik Öğretmenleri",
        title="Matematik Öğretmenleri İçin Öğrenci Bulma Sistemi | Sterr",
        description="Matematik öğretmenleri için öğrenci getiren dijital pazarlama: YKS, LGS ve okul destek aramalarında görünür olun. Nitelikli veli, dolu takvim.",
        headline="Matematikte en iyisi olmak yetmez. Bulunmak gerekir.",
        lede="Veliler \"matematik özel ders\" diye aradığında karşısına çıkan öğretmen kazanır. Sizi o aramaların en üstüne taşıyor, gelen talebi süzüp size ulaştırıyoruz.",
        pains=(
            "Yoğun rekabet ve fiyat baskısı",
            "Deneyiminizi anlatacak bir vitrin olmaması",
            "Sınav dönemleri dışında düşen talep",
            "Sosyal medyaya ayıracak vakit olmaması",
        ),
        system=(
            ("Sınav odaklı konumlandırma", "TYT-AYT, LGS veya okul destek — uzmanlığınıza göre net bir mesaj."),
            ("İçerik ekibi", "Kısa soru çözüm videoları ve ipuçlarıyla güven inşa eden içerik üretimi; çekimi biz yaparız."),
            ("Google & Meta reklamları", "Bölgenizdeki ve online hedef kitledeki velilere doğrudan ulaşan kampanyalar."),
            ("Başvuru süzgeci", "Seviye, hedef ve bütçe bilgisini önceden alan form ile verimli ilk görüşme."),
        ),
        searches=("matematik özel ders", "YKS matematik özel ders", "LGS matematik özel ders", "online matematik dersi", "matematik öğretmeni özel ders fiyatları"),
        faqs=(
            ("Sadece belirli bir ilde mi çalışıyorsunuz?", "Hayır, 81 ilde çalışıyoruz. Yüz yüze derslerde ilinize, online derslerde Türkiye geneline odaklanırız."),
            ("Video çekmek zorunda mıyım?", "Zorunlu değil ama en çok güven oluşturan format bu. Çekim ve kurgu sürecini baştan sona biz yönetiyoruz."),
        ),
    ),
    Sector(
        slug="fizik-ogretmenleri",
        name="Fizik Öğretmenleri",
        title="Fizik Öğretmenleri İçin Dijital Pazarlama | Sterr Agency",
        description="Fizik öğretmenlerine nitelikli öğrenci getiriyoruz. YKS fizik aramalarında görünürlük, içerik üretimi ve fiyatçıyı eleyen başvuru akışı.",
        headline="Fizik zor. Öğrenci bulmak zor olmamalı.",
        lede="Fizik, öğrencilerin en çok destek aradığı derslerden biri. Bu talebi doğru kanallarda yakalayıp, sizinle çalışmaya hazır öğrencileri takviminize yerleştiriyoruz.",
        pains=(
            "Uzmanlığınızın genel ilanlarda kaybolması",
            "Düzensiz öğrenci akışı",
            "Pazarlama bilgisi ve zaman eksikliği",
            "Komisyonlu platform bağımlılığı",
        ),
        system=(
            ("Uzman konumlandırma", "Fizikte fark yaratan yönteminizi öne çıkaran marka dili."),
            ("SEO & reklam", "Google'da görünürlük."),
            ("İçerik yayılımı", "Soru çözümleri ve konu anlatımlarıyla uzman içerikler."),
            ("Filtrelenmiş talep", "Hedef, seviye ve bütçe netleşmiş başvurular."),
        ),
        searches=("fizik özel ders", "YKS fizik özel ders", "AYT fizik özel ders", "online fizik dersi", "fizik öğretmeni özel ders"),
        faqs=(
            ("Grup dersleri için de çalışıyor musunuz?", "Evet. Birebir, grup ve online kurs modellerinin hepsi için ayrı funnel kurgulayabiliyoruz."),
            ("Kaç öğrenci getirebilirsiniz?", "Bu; bölgenize, fiyatlamanıza ve kapasitenize göre değişir. Ön görüşmede hedefinizi birlikte gerçekçi olarak belirliyoruz."),
        ),
    ),
    Sector(
        slug="e-ticaret",
        name="E-Ticaret Markaları",
        title="E-Ticaret Dijital Pazarlama Ajansı | Kurulum + Satış | Sterr",
        description="E-ticaret sistemi kuruyor, trafiği ve satışı getiriyoruz. Google Shopping, Meta reklamları, SEO ve içerik üretimi tek ekipte. Aylık rapor.",
        headline="Mağazayı kuruyoruz. Satışı da getiriyoruz.",
        lede="Bir e-ticaret sitesi, ziyaretçi gelmediği sürece sadece bir katalogdur. Altyapıyı kuruyor, ardından reklam, SEO ve içerikle siparişleri getiriyoruz.",
        pains=(
            "Ziyaretçi var, satış yok",
            "Yükselen reklam maliyetleri (ROAS düşüşü)",
            "Ürün içeriği ve görsel eksikliği",
            "Pazaryeri komisyonlarına bağımlılık",
        ),
        system=(
            ("E-ticaret kurulumu", "Hızlı, mobil uyumlu ve dönüşüm odaklı mağaza altyapısı; ödeme ve kargo entegrasyonları."),
            ("Performans reklamları", "Google Shopping, Performance Max ve Meta katalog reklamlarıyla kârlı büyüme."),
            ("SEO", "Mağazanızın Google'da kalıcı görünürlüğü."),
            ("İçerik prodüksiyonu", "Ürün çekimleri, UGC videolar ve reklam kreatifleri."),
        ),
        searches=("online satış", "e-ticaret sitesi kurmak", "e-ticaret reklam ajansı", "google shopping reklam", "e-ticaret SEO"),
        faqs=(
            ("Hangi altyapıları kullanıyorsunuz?", "İhtiyaca göre Shopify, WooCommerce, İkas, Ticimax veya özel altyapı öneriyoruz."),
            ("Mevcut sitemle çalışabilir misiniz?", "Evet. Önce mevcut sitenizi dönüşüm açısından denetler, ardından büyümeyi planlarız."),
        ),
    ),
    Sector(
        slug="klinik-ve-saglik",
        name="Klinik & Sağlık",
        title="Klinikler İçin Dijital Pazarlama ve Hasta Kazanımı | Sterr",
        description="Klinik, diş hekimi ve sağlık profesyonelleri için mevzuata uygun dijital pazarlama. Güven veren marka, nitelikli randevu talebi.",
        headline="Güven inşa ediyoruz. Randevular geliyor.",
        lede="Sağlıkta tercih, güvenle yapılır. Mevzuata uygun, bilgilendirici içerik ve doğru hedeflenmiş kampanyalarla kliniğinizi bölgesinin ilk tercihi haline getiriyoruz.",
        pains=(
            "Reklam kısıtları ve mevzuat",
            "Güven oluşturmakta zorlanmak",
            "Fiyat soran ama gelmeyen hasta adayları",
            "Yerel aramalarda rakiplerin gerisinde kalmak",
        ),
        system=(
            ("SEO", "Google'da ve Google Haritalar'da görünürlük."),
            ("Bilgilendirici içerik", "Hekim odaklı, güven veren ve mevzuata uygun içerikler."),
            ("Randevu funnel'ı", "Talebi önceden nitelendiren, no-show oranını düşüren başvuru akışı."),
            ("İtibar yönetimi", "Gerçek hasta memnuniyetini görünür kılan yorum stratejisi."),
        ),
        searches=("diş kliniği", "estetik klinik", "fizyoterapist", "psikolog", "diyetisyen"),
        faqs=(
            ("Sağlık reklamlarındaki mevzuata uyuyor musunuz?", "Evet. İçerik ve reklamları sağlık mevzuatı ile platform politikalarına uygun şekilde hazırlıyoruz."),
            ("Tek hekimli muayenehanelerle de çalışıyor musunuz?", "Evet. Paketlerimiz tek hekimden çok şubeli kliniklere kadar ölçeklenir."),
        ),
    ),
    Sector(
        slug="profesyonel-hizmetler",
        name="Profesyonel Hizmetler",
        title="Danışman, Avukat ve Hizmet Firmaları İçin Pazarlama | Sterr",
        description="Danışmanlık, hukuk, mimarlık ve B2B hizmet firmalarına nitelikli müşteri getiriyoruz. Otorite inşa eden içerik, doğru hedeflenen reklam.",
        headline="Uzmanlığınızı görünür kılıyoruz.",
        lede="Profesyonel hizmetlerde müşteri, uzmanlığı gördüğü firmayı seçer. Otorite inşa eden içerik, hedefli reklam ve kalite filtreli başvuru akışıyla doğru müşteriyi getiriyoruz.",
        pains=(
            "Yalnızca tavsiyeye dayalı büyüme",
            "Uzmanlığı anlatmanın zorluğu",
            "Düşük bütçeli, uygun olmayan talepler",
            "Uzun satış döngüsü",
        ),
        system=(
            ("Otorite içeriği", "Makaleler, vaka anlatımları ve LinkedIn içerikleriyle uzmanlık kanıtı."),
            ("Arama niyeti reklamları", "Hizmetinize ihtiyaç duyan kişiyi tam o anda yakalayan Google kampanyaları."),
            ("Nitelikli başvuru", "Bütçe ve kapsamı önceden soran form; zamanınız doğru müşteriye gider."),
            ("Yeniden hedefleme", "Uzun karar sürecinde markanızı akılda tutan kampanyalar."),
        ),
        searches=("avukat", "mali müşavir", "iç mimar", "işletme danışmanı", "kurumsal danışmanlık"),
        faqs=(
            ("B2B firmalarla da çalışıyor musunuz?", "Evet. B2B'de LinkedIn, Google ve içerik odaklı uzun vadeli funnel'lar kuruyoruz."),
            ("Meslek kurallarımız reklam yapmamızı kısıtlıyor, ne yapabiliriz?", "Reklam kısıtı olan mesleklerde bilgilendirici içerik ve SEO odaklı, kurallara uygun bir strateji izliyoruz."),
        ),
    ),
]

SECTOR_BY_SLUG = {s.slug: s for s in SECTORS}
