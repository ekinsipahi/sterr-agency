from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from apps.core.models import Package

from .cities import CITIES_ALPHA, CITY_BY_SLUG, cities_by_region, cities_in_region
from .guides import GUIDE_BY_SLUG, GUIDES
from .sectors import SECTOR_BY_SLUG, SECTORS
from .services import CLUSTER_BY_SLUG, CLUSTERS, city_page


def _cluster_or_404(slug):
    try:
        return CLUSTER_BY_SLUG[slug]
    except KeyError:
        raise Http404


def cluster(request, cluster):
    c = _cluster_or_404(cluster)
    return render(request, "seo/cluster.html", {
        "cluster": c,
        "regions": cities_by_region(),
        "packages": Package.objects.filter(is_active=True),
        "guides": [GUIDE_BY_SLUG[g] for g in c.related_guides],
        "other_clusters": [x for x in CLUSTERS if x != c],
        "crumbs": [("Hizmet bölgeleri", reverse("seo:regions")), (c.name, None)],
    })


def city(request, cluster, city):
    c = _cluster_or_404(cluster)
    ct = CITY_BY_SLUG.get(city)
    if ct is None:
        raise Http404
    return render(request, "seo/city.html", {
        "cluster": c,
        "city": ct,
        "page": city_page(c, ct),
        "nearby": cities_in_region(ct.region, exclude=ct),
        "other_clusters": [x for x in CLUSTERS if x != c],
        "packages": Package.objects.filter(is_active=True),
        "guides": [GUIDE_BY_SLUG[g] for g in c.related_guides],
        "crumbs": [(c.name, reverse("seo:cluster", args=[c.slug])), (ct.name, None)],
    })


def regions(request):
    return render(request, "seo/regions.html", {
        "regions": cities_by_region(), "clusters": CLUSTERS, "city_count": len(CITIES_ALPHA),
        "crumbs": [("Hizmet bölgeleri", None)],
    })


def sectors(request):
    return render(request, "seo/sectors.html", {"sectors": SECTORS, "crumbs": [("Sektörler", None)]})


def sector(request, slug):
    s = SECTOR_BY_SLUG.get(slug)
    if s is None:
        raise Http404
    return render(request, "seo/sector.html", {
        "sector": s,
        "others": [x for x in SECTORS if x != s],
        "crumbs": [("Sektörler", reverse("seo:sectors")), (s.name, None)],
        "packages": Package.objects.filter(is_active=True),
    })


def guides(request):
    return render(request, "seo/guides.html", {"guides": GUIDES, "crumbs": [("Rehber", None)]})


def guide(request, slug):
    g = GUIDE_BY_SLUG.get(slug)
    if g is None:
        raise Http404
    return render(request, "seo/guide.html", {
        "guide": g,
        "body_template": f"seo/guides/{g.slug}.html",
        "others": [x for x in GUIDES if x != g][:3],
        "crumbs": [("Rehber", reverse("seo:guides")), (g.h1, None)],
        "packages": Package.objects.filter(is_active=True),
    })
