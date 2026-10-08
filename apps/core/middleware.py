from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """301 www.sterragency.com → sterragency.com (the host in SITE_URL), so Google
    sees one origin. Other hosts (localhost, health checks) pass through."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical = urlsplit(settings.SITE_URL).hostname or ""

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        if self.canonical and host == f"www.{self.canonical}":
            return HttpResponsePermanentRedirect(f"{settings.SITE_URL}{request.get_full_path()}")
        return self.get_response(request)
