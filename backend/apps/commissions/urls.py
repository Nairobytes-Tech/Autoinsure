from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.commissions.views import CommissionStructureViewSet, CommissionViewSet, CommissionPaymentViewSet

router = DefaultRouter()
router.register(r"structures", CommissionStructureViewSet, basename="commission-structure")
router.register(r"", CommissionViewSet, basename="commission")
router.register(r"payments", CommissionPaymentViewSet, basename="commission-payment")

urlpatterns = [
    path("", include(router.urls)),
]
