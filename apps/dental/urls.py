from django.urls import path, re_path

from . import views

app_name = "dental"

urlpatterns = [
    path("dental-tourism/send/", views.send, name="send"),
    path("dental-tourism/thank-you/", views.thanks, name="thanks"),
    # /dental-tourism/ · /dental-tourism/<slug>/ (English) · /dental-tourism/<lang>/[<slug>/]
    re_path(r"^dental-tourism/(?:(?P<lang>[a-z]{2})/)?(?:(?P<slug>[-a-z0-9]+)/)?$", views.dental_page, name="page"),
]
