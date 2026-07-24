from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ai_features.views import AIModelViewSet, AIPredictionViewSet, FraudAlertViewSet

router = DefaultRouter()
router.register(r"models", AIModelViewSet, basename="ai-model")
router.register(r"predictions", AIPredictionViewSet, basename="ai-prediction")
router.register(r"fraud-alerts", FraudAlertViewSet, basename="fraud-alert")

urlpatterns = [
    path("", include(router.urls)),
]
