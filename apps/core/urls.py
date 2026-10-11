from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("hizmetler/", views.services, name="services"),
    path("paketler/", views.packages, name="packages"),
    path("yontem/", views.method, name="method"),
    path("hakkimizda/", views.about, name="about"),
    path("gizlilik-politikasi/", views.legal, {"template": "privacy"}, name="privacy"),
    path("kullanim-kosullari/", views.legal, {"template": "terms"}, name="terms"),
    path("kvkk-aydinlatma-metni/", views.legal, {"template": "kvkk"}, name="kvkk"),
    path("cerez-politikasi/", views.legal, {"template": "cookies"}, name="cookies"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("favicon.ico", views.favicon_ico, name="favicon"),
    path("yorum/", views.review_redirect, name="review"),
]
