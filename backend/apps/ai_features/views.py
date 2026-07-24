from rest_framework import viewsets
from apps.ai_features.models import AIModel, AIPrediction, FraudAlert
from apps.ai_features.serializers import (
    AIModelListSerializer, AIModelDetailSerializer,
    AIPredictionSerializer, FraudAlertSerializer,
)
from apps.core.permissions import IsPlatformAdmin, IsClaimsOfficer
from apps.core.pagination import StandardResultsPagination


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.select_related("configured_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "model_type", "accuracy_score", "created_at"]
    filterset_fields = ["model_type", "is_active"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AIModelListSerializer
        return AIModelDetailSerializer
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class AIPredictionViewSet(viewsets.ModelViewSet):
    queryset = AIPrediction.objects.select_related("model", "accepted_by").all()
    serializer_class = AIPredictionSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["entity_type", "prediction_label"]
    filterset_fields = ["model", "entity_type", "is_accepted"]
    ordering_fields = ["confidence_score", "risk_score", "response_time_ms", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class FraudAlertViewSet(viewsets.ModelViewSet):
    queryset = FraudAlert.objects.select_related(
        "claim", "policy", "customer", "prediction", "assigned_to", "resolved_by",
    ).all()
    serializer_class = FraudAlertSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["title", "description", "alert_type"]
    filterset_fields = ["alert_status", "severity", "assigned_to", "claim", "policy", "customer"]
    ordering_fields = ["severity", "fraud_score", "created_at"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsClaimsOfficer()]
        return [IsPlatformAdmin()]
