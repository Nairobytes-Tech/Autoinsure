from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.commissions.models import CommissionStructure, Commission, CommissionPayment
from apps.commissions.serializers import (
    CommissionStructureSerializer, CommissionListSerializer,
    CommissionDetailSerializer, CommissionPaymentSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsFinanceOfficer
from apps.core.pagination import StandardResultsPagination


class CommissionStructureViewSet(viewsets.ModelViewSet):
    queryset = CommissionStructure.objects.select_related("product", "product_category").all()
    serializer_class = CommissionStructureSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code"]
    ordering_fields = ["name", "channel_type", "effective_from"]
    filterset_fields = ["channel_type", "calculation_type", "product", "is_renewal_applicable"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class CommissionViewSet(viewsets.ModelViewSet):
    queryset = Commission.objects.select_related(
        "policy", "structure", "agent", "broker", "dealer", "approved_by",
    ).all()
    pagination_class = StandardResultsPagination
    search_fields = ["policy__policy_number"]
    ordering_fields = ["commission_status", "earned_by_type", "commission_amount", "calculation_date"]
    filterset_fields = ["commission_status", "earned_by_type", "agent", "broker", "dealer", "policy", "is_renewal"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return CommissionListSerializer
        return CommissionDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsFinanceOfficer()]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        commission = self.get_object()
        commission.approve(request.user)
        return Response({"status": "Commission approved."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        commission = self.get_object()
        reason = request.data.get("reason", "")
        commission.reject(reason, request.user)
        return Response({"status": "Commission rejected."})


class CommissionPaymentViewSet(viewsets.ModelViewSet):
    queryset = CommissionPayment.objects.select_related(
        "agent", "broker", "dealer", "approved_by", "processed_by",
    ).all()
    serializer_class = CommissionPaymentSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["transaction_reference"]
    filterset_fields = ["payment_status", "agent", "broker", "dealer", "payment_method"]
    ordering_fields = ["payment_date", "amount"]
    
    def get_permissions(self):
        return [IsFinanceOfficer()]

    @action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        payment = self.get_object()
        payment.process(request.user)
        return Response({"status": "Commission payment processed."})
