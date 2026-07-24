from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.claims.views import (
    ClaimViewSet, ClaimActivityViewSet, ClaimDocumentViewSet,
    ClaimAssessmentViewSet, ClaimPaymentViewSet, ClaimInvestigationViewSet,
)

router = DefaultRouter()
router.register(r"", ClaimViewSet, basename="claim")
router.register(r"activities", ClaimActivityViewSet, basename="claim-activity")
router.register(r"documents", ClaimDocumentViewSet, basename="claim-document")
router.register(r"assessments", ClaimAssessmentViewSet, basename="claim-assessment")
router.register(r"payments", ClaimPaymentViewSet, basename="claim-payment")
router.register(r"investigations", ClaimInvestigationViewSet, basename="claim-investigation")

urlpatterns = [
    path("", include(router.urls)),
]
