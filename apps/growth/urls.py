from django.urls import path

from . import accounts, api, views
from .content import creator_routes, routes

app_name = "growth"

urlpatterns = [
    path("growth/order/", views.order, name="order"),
    path("growth/success/", views.success, name="success"),
    path("growth/stripe/webhook/", views.webhook, name="webhook"),
    path("growth/api/orders/", api.orders, name="api_orders"),
    path("growth/api/progress/", api.progress, name="api_progress"),
    path("account/", accounts.account, name="account"),
    path("account/login/", accounts.login_view, name="login"),
    path("account/signup/", accounts.signup_view, name="signup"),
    path("account/logout/", accounts.logout_view, name="logout"),
    path("account/verify/<str:token>/", accounts.verify, name="verify"),
    path("account/verify-again/", accounts.resend_verification, name="verify_again"),
    path("account/orders/<int:order_id>/pay/", accounts.pay, name="pay"),
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
