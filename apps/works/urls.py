from django.urls import path

from . import views

app_name = "works"

urlpatterns = [
    path("calismalarimiz/", views.case_list, name="list"),
    path("calismalarimiz/<slug:slug>/", views.case_detail, name="detail"),
]
