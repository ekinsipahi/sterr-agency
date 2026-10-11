from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.templatetags.static import static
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from apps.dental.languages import LANGS, PAGES, alternates, page_path
from apps.seo.cities import CITIES_ALPHA
from apps.seo.guides import GUIDES
from apps.seo.sectors import SECTORS
from apps.seo.services import CLUSTERS
from apps.works.models import CaseStudy

from .models import Package, SiteSettings, Testimonial

HOME_FAQS = [
    ("Paketleriniz ne kadar?", "Paketlerimiz aylık 50.000 ₺'den başlar. Üç seviye sunuyoruz; kapsam, kanal sayısı ve içerik hacmine göre değişir. Reklam bütçesi hizmet bedelinden ayrıdır ve doğrudan platformlara ödenir."),
    ("Nasıl faturalandırıyorsunuz?", "Aylık abonelik modeliyle çalışıyoruz. İlk ay peşin başlıyoruz; sonrasında her ay sonuçları raporluyor ve aylık faturalandırıyoruz."),
    ("Hangi şehirlerde hizmet veriyorsunuz?", "Türkiye'nin 81 ilinin tamamında. Strateji ve raporlama online yürür; içerik çekimi gerektiğinde ekibimiz bulunduğunuz yere gelir."),
    ("İçeriğimiz yok, yine de çalışabilir miyiz?", "Kesinlikle. Özel içerik ekibimiz çekim, kurgu ve metin üretimini üstlenir. Sizden yalnızca işinizi anlatmanızı isteriz."),
    ("Neden bir başvuru formu var?", "Çünkü her işletmeyle çalışmıyoruz. Kapasitemizi, gerçekten büyümek isteyen ve sistemimizden fayda görecek işletmelere ayırıyoruz. Formu dolduran herkese 24 saat içinde dönüş yapıyoruz."),
    ("Sonuçları nasıl takip edeceğim?", "Her ay; gelen talepleri, reklam harcamasını, müşteri başı maliyeti ve organik büyümeyi gösteren bir rapor alırsınız. Search Console, Analytics ve reklam panellerine erişiminiz her zaman sizde kalır."),
]


def home(request):
    return render(request, "core/home.html", {
        "packages": Package.objects.filter(is_active=True),
        "cases": CaseStudy.objects.filter(is_published=True, is_featured=True)[:3],
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
        "sectors": SECTORS,
        "faqs": HOME_FAQS,
        "clusters": CLUSTERS,
    })


def services(request):
    return render(request, "core/services.html", {"clusters": CLUSTERS, "sectors": SECTORS})


def packages(request):
    return render(request, "core/packages.html", {
        "packages": Package.objects.filter(is_active=True),
        "faqs": HOME_FAQS[:3],
    })


def method(request):
    return render(request, "core/method.html")


def about(request):
    return render(request, "core/about.html")


def legal(request, template):
    return render(request, f"legal/{template}.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /basvuru/gonder/",
        "Disallow: /basvuru/tesekkurler/",
        "Disallow: /dental-tourism/send/",
        "Disallow: /dental-tourism/thank-you/",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_urls():
    """(path, priority) pairs for every indexable page."""
    urls = [(reverse("core:home"), "1.0")]
    for name in ("core:services", "core:packages", "core:method", "core:about", "works:list",
                 "seo:sectors", "seo:guides", "seo:regions", "leads:apply"):
        urls.append((reverse(name), "0.8"))
    for name in ("core:privacy", "core:terms", "core:kvkk", "core:cookies"):
        urls.append((reverse(name), "0.2"))
    urls += [(reverse("seo:sector", args=[s.slug]), "0.7") for s in SECTORS]
    urls += [(reverse("seo:guide", args=[g.slug]), "0.6") for g in GUIDES]
    urls += [(c.get_absolute_url(), "0.6") for c in CaseStudy.objects.filter(is_published=True)]
    for cluster in CLUSTERS:
        urls.append((reverse("seo:cluster", args=[cluster.slug]), "0.9"))
        urls += [(reverse("seo:city", args=[cluster.slug, city.slug]), "0.7") for city in CITIES_ALPHA]
    return urls


def dental_sitemap_urls():
    """(path, priority, alternates) for every language version of the dental tourism pages."""
    return [
        (page_path(lang.code, page), "0.9" if page == "hub" else "0.8", alternates(page))
        for page in PAGES for lang in LANGS
    ]


@cache_page(60 * 60)
def sitemap_xml(request):
    site = settings.SITE_URL
    body = "".join(f"<url><loc>{site}{path}</loc><priority>{prio}</priority></url>" for path, prio in sitemap_urls())
    body += "".join(
        f"<url><loc>{site}{path}</loc><priority>{prio}</priority>"
        + "".join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{site}{alt}"/>' for code, alt in alts)
        + "</url>"
        for path, prio, alts in dental_sitemap_urls()
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
           f"{body}</urlset>")
    return HttpResponse(xml, content_type="application/xml")


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def favicon_ico(request):
    # Browsers and crawlers request /favicon.ico at the root regardless of <link> tags.
    return HttpResponsePermanentRedirect(static("img/favicon.ico"))


def review_redirect(request):
    """sterragency.com/yorum/ → Google 'write a review' link, easy to send to clients."""
    url = SiteSettings.load().google_review_url or SiteSettings.load().google_business_url
    if not url:
        raise Http404
    return HttpResponseRedirect(url)
