from django.db import migrations

PACKAGES = [
    {
        "name": "Kıvılcım", "slug": "kivilcim", "order": 1, "price": 50000, "price_prefix": "",
        "tagline": "Talebi başlatan sistem. Tek kanalda, net hedefle.",
        "ideal_for": "Özel ders öğretmenleri, tek lokasyonlu yerel işletmeler ve yeni markalar",
        "features": "\n".join([
            "Pazar, rakip ve müşteri analizi",
            "Google veya Meta reklam yönetimi (1 kanal)",
            "Aylık 8 içerik (gönderi + reels)",
            "Kalite filtreli başvuru funnel'ı",
            "Google İşletme profili ve temel SEO",
            "WhatsApp & form lead takibi",
            "Aylık performans raporu",
        ]),
    },
    {
        "name": "İvme", "slug": "ivme", "order": 2, "price": 90000, "price_prefix": "", "is_featured": True,
        "tagline": "Reklam + SEO + içerik aynı hedef için çalışır.",
        "ideal_for": "Büyümek isteyen işletmeler, klinikler, e-ticaret markaları ve eğitim kurumları",
        "features": "\n".join([
            "Kıvılcım'daki her şey",
            "Google + Meta reklam yönetimi",
            "Aylık 16 içerik + ayda 1 gün yerinde çekim",
            "Türkçe anahtar kelime SEO'su ve içerik mimarisi",
            "Programatik SEO sayfaları",
            "AI destekli forum ve soru-cevap içerik yayılımı",
            "Yeniden hedefleme kampanyaları",
            "İki haftada bir strateji görüşmesi",
        ]),
    },
    {
        "name": "Hakimiyet", "slug": "hakimiyet", "order": 3, "price": 150000, "price_prefix": "başlayan",
        "tagline": "Kategorinizde akla ilk gelen marka olun.",
        "ideal_for": "Çok şubeli işletmeler, ulusal e-ticaret markaları ve pazar lideri olmak isteyenler",
        "features": "\n".join([
            "İvme'deki her şey",
            "Marka konumlandırma ve kimlik çalışması",
            "Çok kanallı reklam: Google, Meta, TikTok, YouTube",
            "Aylık 30+ içerik ve sürekli kreatif testi",
            "81 il ölçeğinde programatik SEO",
            "Özel marketing ve dijital PR yayılımı",
            "Landing page / e-ticaret geliştirme",
            "Size özel proje ekibi, haftalık görüşme",
        ]),
    },
]


def seed(apps, schema_editor):
    Package = apps.get_model("core", "Package")
    for data in PACKAGES:
        Package.objects.update_or_create(slug=data["slug"], defaults=data)


def unseed(apps, schema_editor):
    apps.get_model("core", "Package").objects.filter(slug__in=[p["slug"] for p in PACKAGES]).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
