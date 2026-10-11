from django.urls import path, re_path

from apps.core.languages import INTL_CODES

from . import views

app_name = "intl"
LANG_RE = "|".join(INTL_CODES)

urlpatterns = [
    path("intl/send/", views.send, name="send"),
    path("intl/thank-you/", views.thanks, name="thanks"),
    re_path(rf"^(?P<lang>{LANG_RE})/(?:(?P<first>[-a-z0-9]+)/)?(?:(?P<second>[-a-z0-9]+)/)?$", views.intl_page, name="page"),
]
