from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.policies.models import Policy, PolicyEndorsement, PolicyRenewal, PolicyCancellation, PolicyDocument
from apps.policies.serializers import (
    PolicyListSerializer, PolicyDetailSerializer,
    PolicyEndorsementSerializer, PolicyRenewalSerializer,
    PolicyCancellationSerializer, PolicyDocumentSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsUnderwriter
from apps.core.pagination import StandardResultsPagination


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.select_related(
        "customer", "product", "product_variant", "quote", "agent", "broker", "dealer", "branch",
    ).all()
    pagination_class = StandardResultsPagination
    search_fields = ["policy_number", "customer__first_name", "customer__last_name", "customer__email"]
    ordering_fields = ["policy_number", "policy_status", "payment_status", "start_date", "end_date", "created_at"]
    filterset_fields = ["policy_status", "payment_status", "policy_type", "product", "customer", "agent", "broker", "branch"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return PolicyListSerializer
        return PolicyDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsUnderwriter()]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        policy = self.get_object()
        policy.approve(request.user)
        return Response({"status": "Policy approved."})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        policy = self.get_object()
        policy.activate()
        return Response({"status": "Policy activated."})

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        policy = self.get_object()
        reason = request.data.get("reason", "")
        policy.suspend(reason)
        return Response({"status": "Policy suspended."})

    @action(detail=True, methods=["get"])
    def endorsements(self, request, pk=None):
        policy = self.get_object()
        endorsements = PolicyEndorsement.objects.filter(policy=policy)
        serializer = PolicyEndorsementSerializer(endorsements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def renewals(self, request, pk=None):
        policy = self.get_object()
        renewals = PolicyRenewal.objects.filter(policy=policy)
        serializer = PolicyRenewalSerializer(renewals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        policy = self.get_object()
        docs = PolicyDocument.objects.filter(policy=policy)
        serializer = PolicyDocumentSerializer(docs, many=True)
        return Response(serializer.data)


class PolicyEndorsementViewSet(viewsets.ModelViewSet):
    queryset = PolicyEndorsement.objects.select_related("policy", "requested_by", "approved_by").all()
    serializer_class = PolicyEndorsementSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["endorsement_number", "policy__policy_number"]
    filterset_fields = ["policy", "endorsement_type", "is_approved"]
    ordering_fields = ["effective_date", "created_at"]
    
    def get_permissions(self):
        return [IsUnderwriter()]


class PolicyRenewalViewSet(viewsets.ModelViewSet):
    queryset = PolicyRenewal.objects.select_related("policy", "new_policy", "renewed_by", "renewal_quote").all()
    serializer_class = PolicyRenewalSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["renewal_number", "policy__policy_number"]
    filterset_fields = ["policy", "renewal_status", "auto_renewed"]
    ordering_fields = ["renewal_date", "created_at"]
    
    def get_permissions(self):
        return [IsUnderwriter()]


class PolicyCancellationViewSet(viewsets.ModelViewSet):
    queryset = PolicyCancellation.objects.select_related("policy", "approved_by").all()
    serializer_class = PolicyCancellationSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["cancellation_number", "policy__policy_number"]
    filterset_fields = ["policy", "reason", "refund_status", "is_approved"]
    ordering_fields = ["cancellation_date", "created_at"]
    
    def get_permissions(self):
        return [IsUnderwriter()]


class PolicyDocumentViewSet(viewsets.ModelViewSet):
    queryset = PolicyDocument.objects.select_related("policy", "generated_by").all()
    serializer_class = PolicyDocumentSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["title", "policy__policy_number"]
    filterset_fields = ["policy", "document_type", "is_primary"]
    ordering_fields = ["document_type", "created_at"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]
