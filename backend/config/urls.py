from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/tenants/", include("apps.tenants.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/customers/", include("apps.customers.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/policies/", include("apps.policies.urls")),
    path("api/v1/quotes/", include("apps.quotes.urls")),
    path("api/v1/claims/", include("apps.claims.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/commissions/", include("apps.commissions.urls")),
    path("api/v1/agents/", include("apps.agents.urls")),
    path("api/v1/brokers/", include("apps.brokers.urls")),
    path("api/v1/dealers/", include("apps.dealers.urls")),
    path("api/v1/branches/", include("apps.branches.urls")),
    path("api/v1/underwriting/", include("apps.underwriting.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/documents/", include("apps.documents.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/integrations/", include("apps.integrations.urls")),
    path("api/v1/ai/", include("apps.ai_features.urls")),
    path("api/v1/workflows/", include("apps.workflows.urls")),
    # Schema endpoints
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
