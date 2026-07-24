from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payments.views import PaymentMethodViewSet, PaymentViewSet, InvoiceViewSet, ReceiptViewSet

router = DefaultRouter()
router.register(r"methods", PaymentMethodViewSet, basename="payment-method")
router.register(r"", PaymentViewSet, basename="payment")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"receipts", ReceiptViewSet, basename="receipt")

urlpatterns = [
    path("", include(router.urls)),
]
