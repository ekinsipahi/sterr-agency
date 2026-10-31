from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "works"

urlpatterns = [
    path("calismalarimiz/", views.case_list, name="list"),
    path("calismalarimiz/devrimbirikensipahi-yerel-seo/",
         RedirectView.as_view(url="/calismalarimiz/devrimbirikensipahi-klinik-sitesi/", permanent=True)),
    path("calismalarimiz/<slug:slug>/", views.case_detail, name="detail"),
]
