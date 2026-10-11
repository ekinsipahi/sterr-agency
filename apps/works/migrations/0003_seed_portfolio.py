"""Seed our own live projects as case studies (editable / removable in the admin).

Covers are screenshots from static/img/works/, copied into media storage once.
Only facts we can stand behind go in here; clinic patient numbers etc. are added
later in the admin when the real figures are in.
"""
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import migrations

PROJECTS = [
    {
        "slug": "linksterr-saas-3000-kullanici",
        "title": "Link$terr: 5 ayda 3.000 kullanıcıya ulaşan SaaS",
        "client": "Link$terr",
        "sector": "SaaS",
        "city": "",
        "summary": "Kullanıcılarına her tıklamada kazandıran link kısaltma platformu. Ürünü, sitesini ve büyüme "
                   "sistemini kurduk; lansmandan sonraki 5 ayda 3.000 kullanıcıya ulaştı.",
        "website_url": "https://linksterr.com/",
        "cover": "linksterr.webp",
        "metrics": [("3.000", "kullanıcı"), ("5 ay", "lansmandan itibaren")],
        "featured": True,
        "order": 1,
    },
    {
        "slug": "dentaltourism-tr-16-dil",
        "title": "dentaltourism.tr: 16 dilde diş turizmi platformu",
        "client": "dentaltourism.tr",
        "sector": "Sağlık turizmi",
        "city": "İstanbul",
        "summary": "Yurt dışından hasta getirmek için kurduğumuz, 16 dilde programatik SEO ile çalışan diş turizmi "
                   "platformu. Her dilde tedavi, rehber ve ülke sayfaları; hreflang ve sitemap ile.",
        "website_url": "https://dentaltourism.tr/",
        "cover": "dentaltourism.webp",
        "metrics": [("16", "dil")],
        "featured": True,
        "order": 2,
    },
    {
        "slug": "drdevrim-sisli-dis-klinigi",
        "title": "Dr. Devrim Biriken Sipahi: Şişli diş kliniği sitesi",
        "client": "Dr. Dt. Devrim Biriken Sipahi",
        "sector": "Klinik / sağlık",
        "city": "İstanbul",
        "summary": "35 yıllık deneyime sahip Şişli diş hekimi için çok dilli klinik sitesi: randevu ve WhatsApp "
                   "akışı, Google yorumları ve yerel SEO.",
        "website_url": "https://drdevrim.com/",
        "cover": "drdevrim.webp",
        "metrics": [],
        "featured": True,
        "order": 3,
    },
    {
        "slug": "devrimbirikensipahi-yerel-seo",
        "title": "devrimbirikensipahi.com.tr: Şişli diş hekimi için yerel SEO sitesi",
        "client": "Dr. Dt. Devrim Biriken Sipahi",
        "sector": "Klinik / sağlık",
        "city": "İstanbul",
        "summary": "Şişli'de diş hekimi aramalarında görünür olmak için kurulan ikinci klinik sitesi; Türkçe, "
                   "İngilizce, Felemenkçe ve Almanca.",
        "website_url": "https://devrimbirikensipahi.com.tr/",
        "cover": "devrimbirikensipahi.webp",
        "metrics": [],
        "featured": False,
        "order": 4,
    },
]


def seed(apps, schema_editor):
    CaseStudy = apps.get_model("works", "CaseStudy")
    CaseMetric = apps.get_model("works", "CaseMetric")
    for p in PROJECTS:
        if CaseStudy.objects.filter(slug=p["slug"]).exists():
            continue
        cover = f"works/covers/{p['cover']}"
        if not default_storage.exists(cover):
            src = settings.BASE_DIR / "static" / "img" / "works" / p["cover"]
            if src.exists():
                with src.open("rb") as fh:
                    cover = default_storage.save(cover, File(fh))
            else:
                cover = ""
        case = CaseStudy.objects.create(
            slug=p["slug"], title=p["title"], client=p["client"], sector=p["sector"], city=p["city"],
            summary=p["summary"], website_url=p["website_url"], cover=cover,
            is_featured=p["featured"], is_published=True, order=p["order"],
        )
        for i, (value, label) in enumerate(p["metrics"]):
            CaseMetric.objects.create(case=case, value=value, label=label, order=i)


def unseed(apps, schema_editor):
    apps.get_model("works", "CaseStudy").objects.filter(slug__in=[p["slug"] for p in PROJECTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("works", "0002_casestudy_website_url")]
    operations = [migrations.RunPython(seed, unseed)]
