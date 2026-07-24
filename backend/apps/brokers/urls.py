from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.brokers.views import BrokerViewSet

router = DefaultRouter()
router.register(r"", BrokerViewSet, basename="broker")

urlpatterns = [
    path("", include(router.urls)),
]
