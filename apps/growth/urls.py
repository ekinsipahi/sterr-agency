from django.urls import path

from . import accounts, api, views
from .content import creator_routes, routes

app_name = "growth"

urlpatterns = [
    path("growth/order/", views.order, name="order"),
    path("growth/success/", views.success, name="success"),
    path("growth/stripe/webhook/", views.webhook, name="webhook"),
    path("growth/api/subscriptions/", api.subscriptions, name="api_subscriptions"),
    path("growth/api/stats/", api.stats, name="api_stats"),
    path("account/", accounts.account, name="account"),
    path("account/login/", accounts.login_view, name="login"),
    path("account/signup/", accounts.signup_view, name="signup"),
    path("account/logout/", accounts.logout_view, name="logout"),
    path("account/google/", accounts.google_start, name="google"),
    path("account/google/complete/", accounts.google_complete, name="google_complete"),
    path("account/verify/<str:token>/", accounts.verify, name="verify"),
    path("account/verify-again/", accounts.resend_verification, name="verify_again"),
    path("account/subscriptions/<int:sub_id>/start/", accounts.pay, name="pay"),
    path("account/subscriptions/<int:sub_id>/cancel/", accounts.cancel, name="cancel"),
    path("account/subscriptions/<int:sub_id>/resume/", accounts.resume, name="resume"),
    path("account/view/<int:user_id>/", accounts.view_as, name="view_as"),
    path("account/billing/", accounts.billing_portal, name="billing"),
    path("account/password/", accounts.reset_request, name="reset"),
    path("account/password/<str:uidb64>/<str:token>/", accounts.reset_confirm, name="reset_confirm"),
] + [
    path(route, views.page, {"lang": code, "page": page, "platform": platform},
         name=f"{platform}_{code}_{page.replace(':', '_')}")
    for route, code, page, platform in routes()
] + [
    path(route, views.creators, {"lang": code, "page": page}, name=f"creators_{code}_{page}")
    for route, code, page in creator_routes()
]
