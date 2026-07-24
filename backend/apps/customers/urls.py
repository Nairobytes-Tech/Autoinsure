from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.customers.views import (
    CustomerViewSet, CustomerDocumentViewSet,
    CustomerVehicleViewSet, CustomerContactViewSet,
)

router = DefaultRouter()
router.register(r"", CustomerViewSet, basename="customer")
router.register(r"documents", CustomerDocumentViewSet, basename="customer-document")
router.register(r"vehicles", CustomerVehicleViewSet, basename="customer-vehicle")
router.register(r"contacts", CustomerContactViewSet, basename="customer-contact")

urlpatterns = [
    path("", include(router.urls)),
]
