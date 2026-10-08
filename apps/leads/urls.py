from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("basvuru/", views.apply, name="apply"),
    path("basvuru/gonder/", views.submit, name="submit"),
    path("basvuru/tesekkurler/", views.thanks, name="thanks"),
]
