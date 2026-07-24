from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.policies.views import (
    PolicyViewSet, PolicyEndorsementViewSet,
    PolicyRenewalViewSet, PolicyCancellationViewSet, PolicyDocumentViewSet,
)

router = DefaultRouter()
router.register(r"", PolicyViewSet, basename="policy")
router.register(r"endorsements", PolicyEndorsementViewSet, basename="policy-endorsement")
router.register(r"renewals", PolicyRenewalViewSet, basename="policy-renewal")
router.register(r"cancellations", PolicyCancellationViewSet, basename="policy-cancellation")
router.register(r"documents", PolicyDocumentViewSet, basename="policy-document")

urlpatterns = [
    path("", include(router.urls)),
]
