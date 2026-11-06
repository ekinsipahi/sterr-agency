"""Customer account activity for dispute evidence: every sign-in (any method), dashboard
visits (once an hour) and visits to the cancel page."""
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from django.dispatch import receiver

from apps.leads.views import _client_ip

from .models import AccountActivity


def record(request, user, kind):
    if user is None or not user.is_authenticated or user.is_staff:
        return
    if kind == "dashboard":
        key = f"growth-activity:{user.pk}"
        if cache.get(key):
            return
        cache.set(key, 1, 60 * 60)
    AccountActivity.objects.create(user=user, kind=kind, ip=_client_ip(request) or None,
                                   user_agent=request.META.get("HTTP_USER_AGENT", "")[:300])


@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    if request is not None:
        record(request, user, "login")
