from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.audit.views import AuditLogViewSet, DataChangeLogViewSet

router = DefaultRouter()
router.register(r"logs", AuditLogViewSet, basename="audit-log")
router.register(r"changes", DataChangeLogViewSet, basename="data-change-log")

urlpatterns = [
    path("", include(router.urls)),
]
