from django.http import HttpResponse


class HealthCheckMiddleware:
    """Answer /healthz before host validation and the HTTPS redirect, so Render's
    health checks pass whatever Host header or scheme they use."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthz":
            return HttpResponse("ok", content_type="text/plain")
        return self.get_response(request)
