from rest_framework import viewsets
from apps.underwriting.models import UnderwritingRule, UnderwritingDecision, ReferralQueue
from apps.underwriting.serializers import (
    UnderwritingRuleSerializer, UnderwritingDecisionSerializer, ReferralQueueSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsUnderwriter
from apps.core.pagination import StandardResultsPagination


class UnderwritingRuleViewSet(viewsets.ModelViewSet):
    queryset = UnderwritingRule.objects.select_related("product", "product_category").all()
    serializer_class = UnderwritingRuleSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "rule_type", "priority", "effective_from"]
    filterset_fields = ["rule_type", "product", "product_category", "is_automated", "requires_manual_review"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsUnderwriter()]


class UnderwritingDecisionViewSet(viewsets.ModelViewSet):
    queryset = UnderwritingDecision.objects.select_related(
        "policy", "quote", "underwriter", "approved_by",
    ).all()
    serializer_class = UnderwritingDecisionSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["policy__policy_number", "quote__quote_number"]
    ordering_fields = ["decision_type", "risk_level", "risk_score", "decision_date"]
    filterset_fields = ["decision_type", "risk_level", "policy", "quote", "underwriter"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsUnderwriter()]


class ReferralQueueViewSet(viewsets.ModelViewSet):
    queryset = ReferralQueue.objects.select_related("decision", "assigned_to", "escalated_by").all()
    serializer_class = ReferralQueueSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["decision", "priority", "assigned_to", "escalated"]
    ordering_fields = ["priority", "created_at"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsUnderwriter()]
