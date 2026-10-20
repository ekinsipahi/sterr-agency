from django.urls import path

from . import views
from .content import routes

app_name = "growth"

urlpatterns = [
    path("growth/checkout/", views.checkout, name="checkout"),
    path("growth/success/", views.success, name="success"),
    path("growth/manage/", views.manage, name="manage"),
    path("growth/manage/<str:token>/", views.portal, name="portal"),
    path("growth/stripe/webhook/", views.webhook, name="webhook"),
] + [
    path(route, views.page, {"lang": code, "page": page}, name=f"{code}_{page.replace(':', '_')}")
    for route, code, page in routes()
]
