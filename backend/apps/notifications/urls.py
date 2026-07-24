from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notifications.views import (
    NotificationTemplateViewSet, NotificationViewSet, NotificationPreferenceViewSet,
)

router = DefaultRouter()
router.register(r"templates", NotificationTemplateViewSet, basename="notification-template")
router.register(r"", NotificationViewSet, basename="notification")
router.register(r"preferences", NotificationPreferenceViewSet, basename="notification-preference")

urlpatterns = [
    path("", include(router.urls)),
]
