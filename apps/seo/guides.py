"""Informational guides — each one owns a cluster of question-type keywords.

Body copy lives in templates/seo/guides/<slug>.html.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Guide:
    slug: str
    title: str        # <title>
    description: str  # meta description
    h1: str
    lede: str
    keywords: tuple   # queries this guide targets
    minutes: int
    faqs: tuple = ()


GUIDES = [
    Guide(
        slug="dijital-pazarlama-ajansi-ne-is-yapar",
        title="Dijital Pazarlama Ajansı Ne İş Yapar? 2026 Rehberi | Sterr",
        description="Dijital pazarlama ajansı ne iş yapar, hangi hizmetleri verir, doğru ajans nasıl seçilir? Reklam, SEO ve içeriğin müşteriye dönüştüğü sistemi anlatıyoruz.",
        h1="Dijital pazarlama ajansı ne iş yapar?",
        lede="Kısa cevap: iyi bir dijital pazarlama ajansı size müşteri getirir. Uzun cevap aşağıda — ve ajans seçerken sormanız gereken soruları da ekledik.",
        keywords=("dijital pazarlama ajansı ne iş yapar", "dijital pazarlama ajansı nedir", "dijital pazarlama ajansı ne yapar", "dijital ajans ne iş yapar"),
        minutes=6,
        faqs=(
            ("Dijital pazarlama ajansı ile reklam ajansı arasındaki fark nedir?", "Klasik reklam ajansı genellikle yaratıcı kampanya üretir. Dijital pazarlama ajansı ise reklam, SEO, sosyal medya ve veri analizini birlikte yöneterek ölçülebilir satış hedefiyle çalışır."),
            ("Küçük işletmeler dijital pazarlama ajansıyla çalışmalı mı?", "Müşteri başı değeri ajans maliyetini karşılayan her işletme için evet. Ajans; uzman ekip, araç ve deneyimi tek bir aylık bedelle sunar."),
        ),
    ),
    Guide(
        slug="dijital-pazarlama-ajansi-fiyatlari",
        title="Dijital Pazarlama Ajansı Fiyatları 2026 | Neye Göre Değişir?",
        description="Dijital pazarlama ajansı fiyatları neye göre belirlenir? Aylık hizmet bedeli, reklam bütçesi ve gizli maliyetler. Sterr paketleri 50.000 ₺'den başlar.",
        h1="Dijital pazarlama ajansı fiyatları: 2026'da gerçekçi bütçe",
        lede="Ucuz ajans pahalıya patlar; pahalı ajans da her zaman iyi değildir. Fiyatı belirleyen unsurları ve kendi paket fiyatlarımızı şeffafça anlatıyoruz.",
        keywords=("dijital pazarlama ajansı fiyatları", "dijital ajans fiyatları", "dijital pazarlama fiyatları", "dijital pazarlama ajansı ücretleri"),
        minutes=5,
        faqs=(
            ("Reklam bütçesi ajans ücretine dahil mi?", "Hayır. Reklam bütçesi doğrudan Google ve Meta'ya ödenir; ajans ücreti yönetim, strateji ve içerik üretimini kapsar."),
            ("Neden 50.000 ₺'den başlıyorsunuz?", "Çünkü tek bir kanalı değil; reklam, SEO, içerik ve funnel'ı birlikte kuruyoruz. Bu kapsamın altında müşteri getiren bir sistem kurmak gerçekçi değil."),
        ),
    ),
    Guide(
        slug="sosyal-medya-ajansi-nedir",
        title="Sosyal Medya Ajansı Nedir, Ne Yapar? | Sterr Agency",
        description="Sosyal medya ajansı nedir, ne demek, ne yapar? Hizmet kapsamı, çalışma modeli ve doğru ajansı seçmek için kontrol listesi.",
        h1="Sosyal medya ajansı nedir, ne yapar?",
        lede="Sosyal medya ajansı; markanızın sosyal medya hesaplarını strateji, içerik, reklam ve topluluk yönetimiyle büyüten ekiptir. Peki iyisini nasıl anlarsınız?",
        keywords=("sosyal medya ajansı nedir", "sosyal medya ajansı ne demek", "sosyal medya ajansı ne yapar", "sosyal medya ajansları"),
        minutes=5,
        faqs=(
            ("Sosyal medya ajansı takipçi satın alır mı?", "Ciddi bir ajans almaz. Sahte takipçi etkileşimi düşürür ve reklam performansını bozar. Biz takipçi değil, müşteri hedefliyoruz."),
            ("Sosyal medya ajansı ile freelancer arasındaki fark nedir?", "Freelancer genellikle tek bir alanda (tasarım, paylaşım) çalışır. Ajans; strateji, prodüksiyon, reklam ve raporlamayı ekip olarak yürütür."),
        ),
    ),
    Guide(
        slug="sosyal-medya-ajansi-fiyatlari",
        title="Sosyal Medya Ajansı Fiyatları 2026 | Ücretler ve Paketler",
        description="Sosyal medya ajansı fiyatları ve ajans ücretleri 2026'da ne kadar? Paket kapsamları, içerik adedi, reklam yönetimi ve dikkat edilmesi gerekenler.",
        h1="Sosyal medya ajansı fiyatları ve ücretleri",
        lede="\"Aylık 5.000 ₺'ye sosyal medya yönetimi\" teklifleri ile \"aylık 100.000 ₺\" teklifleri arasında ne fark var? Paketin içini açıyoruz.",
        keywords=("sosyal medya ajansı fiyatları", "sosyal medya ajans fiyatları", "sosyal medya ajans ücretleri", "sosyal medya yönetimi fiyatları"),
        minutes=5,
        faqs=(
            ("Sosyal medya ajansı ücretleri neden bu kadar farklı?", "Kapsam farklı. Yalnızca paylaşım yapan hizmet ile çekim, reklam, strateji ve raporlama içeren hizmet aynı iş değildir."),
            ("Sözleşme süresi fiyatı etkiler mi?", "Bizde aylık abonelik modeli var; ilk ay peşin başlar, sonraki aylar raporla birlikte faturalandırılır."),
        ),
    ),
    Guide(
        slug="sosyal-medya-ajans-sozlesmesi",
        title="Sosyal Medya Ajans Sözleşmesi: Olması Gereken 10 Madde",
        description="Sosyal medya ajans sözleşmesi imzalamadan önce kontrol etmeniz gereken 10 madde: hesap mülkiyeti, içerik hakları, raporlama, fesih ve daha fazlası.",
        h1="Sosyal medya ajans sözleşmesinde olması gereken 10 madde",
        lede="İyi bir sözleşme iki tarafı da korur. İmzalamadan önce bu maddeleri kontrol edin — biz kendi sözleşmelerimizde hepsini açıkça yazıyoruz.",
        keywords=("sosyal medya ajans sözleşmesi", "sosyal medya yönetimi sözleşmesi", "ajans hizmet sözleşmesi"),
        minutes=6,
    ),
    Guide(
        slug="dijital-pazarlama-uzmani-nedir",
        title="Dijital Pazarlama Uzmanı Nedir, Ne İş Yapar? | Uzman mı Ajans mı?",
        description="Dijital pazarlama uzmanı nedir, ne iş yapar? İşletmeniz için uzman mı işe almalı, ajansla mı çalışmalısınız? Maliyet ve verim karşılaştırması.",
        h1="Dijital pazarlama uzmanı nedir, ne iş yapar?",
        lede="Dijital pazarlama uzmanı; bir markanın çevrim içi kanallardaki büyümesini planlayan ve yöneten kişidir. İşletme sahibi için asıl soru ise şu: uzman mı, ajans mı?",
        keywords=("dijital pazarlama uzmanı nedir", "dijital pazarlama uzmanı ne iş yapar", "dijital pazarlama uzmanlığı nedir", "dijital pazarlama uzmanı", "dijital pazarlama uzmanları"),
        minutes=5,
        faqs=(
            ("Dijital pazarlama uzmanı hangi araçları kullanır?", "Google Ads, Meta Business, GA4, Search Console, SEO araçları, tasarım ve otomasyon yazılımları."),
            ("Tek bir uzman her kanalı yönetebilir mi?", "Temel düzeyde evet, ama reklam, SEO ve içerik prodüksiyonunun her birinde derin uzmanlık gerekir. Bu yüzden ekip modeli daha hızlı sonuç verir."),
        ),
    ),
]

GUIDE_BY_SLUG = {g.slug: g for g in GUIDES}
