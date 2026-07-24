from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.underwriting.views import UnderwritingRuleViewSet, UnderwritingDecisionViewSet, ReferralQueueViewSet

router = DefaultRouter()
router.register(r"rules", UnderwritingRuleViewSet, basename="underwriting-rule")
router.register(r"decisions", UnderwritingDecisionViewSet, basename="underwriting-decision")
router.register(r"referrals", ReferralQueueViewSet, basename="referral-queue")

urlpatterns = [
    path("", include(router.urls)),
]
