from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class TenantMiddleware(MiddlewareMixin):
    EXEMPT_PATHS = [
        "/api/v1/auth/",
        "/api/schema/",
        "/api/docs/",
        "/api/redoc/",
        "/admin/",
        "/health/",
        "/health",
    ]

    def process_request(self, request):
        request.tenant = None

        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None

        if hasattr(request, "user") and request.user and request.user.is_authenticated:
            if hasattr(request.user, "tenant"):
                request.tenant = request.user.tenant
            elif hasattr(request.user, "primary_tenant"):
                request.tenant = request.user.primary_tenant

        return None
