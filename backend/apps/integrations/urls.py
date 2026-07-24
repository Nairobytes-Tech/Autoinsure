from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.integrations.views import IntegrationViewSet, IntegrationLogViewSet

router = DefaultRouter()
router.register(r"", IntegrationViewSet, basename="integration")
router.register(r"logs", IntegrationLogViewSet, basename="integration-log")

urlpatterns = [
    path("", include(router.urls)),
]
