from django.urls import path, register_converter

from . import views
from .services import CLUSTERS


class ClusterConverter:
    """Only matches known cluster slugs so city pages can't shadow other routes."""
    regex = "|".join(c.slug for c in CLUSTERS)

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(ClusterConverter, "cluster")

app_name = "seo"

urlpatterns = [
    path("hizmet-bolgeleri/", views.regions, name="regions"),
    path("sektorler/", views.sectors, name="sectors"),
    path("sektorler/<slug:slug>/", views.sector, name="sector"),
    path("rehber/", views.guides, name="guides"),
    path("rehber/<slug:slug>/", views.guide, name="guide"),
    path("<cluster:cluster>/", views.cluster, name="cluster"),
    path("<cluster:cluster>/<slug:city>/", views.city, name="city"),
]
