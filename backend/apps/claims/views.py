from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.claims.models import (
    Claim, ClaimActivity, ClaimDocument, ClaimAssessment, ClaimPayment, ClaimInvestigation,
)
from apps.claims.serializers import (
    ClaimListSerializer, ClaimDetailSerializer,
    ClaimActivitySerializer, ClaimDocumentSerializer,
    ClaimAssessmentSerializer, ClaimPaymentSerializer, ClaimInvestigationSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsClaimsOfficer
from apps.core.pagination import StandardResultsPagination


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.select_related(
        "policy", "customer", "assigned_to", "assigned_by", "closed_by",
    ).all()
    pagination_class = StandardResultsPagination
    search_fields = ["claim_number", "customer__first_name", "customer__last_name", "policy__policy_number"]
    ordering_fields = ["claim_number", "claim_status", "claim_type", "incident_date", "reported_date", "created_at"]
    filterset_fields = ["claim_status", "claim_type", "priority", "policy", "customer", "assigned_to", "fraud_flag"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ClaimListSerializer
        return ClaimDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsClaimsOfficer()]

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        claim = self.get_object()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_id = request.data.get("user_id")
        assigned_to = User.objects.get(id=user_id)
        claim.assign(assigned_to, assigned_by=request.user)
        return Response({"status": "Claim assigned."})

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        claim = self.get_object()
        amount = request.data.get("amount")
        claim.approve(amount, request.user)
        return Response({"status": "Claim approved."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        claim = self.get_object()
        reason = request.data.get("reason", "")
        claim.reject(reason, request.user)
        return Response({"status": "Claim rejected."})

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        claim = self.get_object()
        claim.close(request.user)
        return Response({"status": "Claim closed."})

    @action(detail=True, methods=["get"])
    def activities(self, request, pk=None):
        claim = self.get_object()
        activities = ClaimActivity.objects.filter(claim=claim)
        serializer = ClaimActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        claim = self.get_object()
        docs = ClaimDocument.objects.filter(claim=claim)
        serializer = ClaimDocumentSerializer(docs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def assessments(self, request, pk=None):
        claim = self.get_object()
        assessments = ClaimAssessment.objects.filter(claim=claim)
        serializer = ClaimAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        claim = self.get_object()
        payments = ClaimPayment.objects.filter(claim=claim)
        serializer = ClaimPaymentSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def investigations(self, request, pk=None):
        claim = self.get_object()
        investigations = ClaimInvestigation.objects.filter(claim=claim)
        serializer = ClaimInvestigationSerializer(investigations, many=True)
        return Response(serializer.data)


class ClaimActivityViewSet(viewsets.ModelViewSet):
    queryset = ClaimActivity.objects.select_related("claim", "performed_by").all()
    serializer_class = ClaimActivitySerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["claim", "action_type"]
    ordering_fields = ["action_type", "created_at"]
    
    def get_permissions(self):
        return [IsClaimsOfficer()]


class ClaimDocumentViewSet(viewsets.ModelViewSet):
    queryset = ClaimDocument.objects.select_related("claim", "verified_by").all()
    serializer_class = ClaimDocumentSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["title"]
    filterset_fields = ["claim", "document_type", "is_verified"]
    ordering_fields = ["document_type", "created_at"]
    
    def get_permissions(self):
        return [IsClaimsOfficer()]


class ClaimAssessmentViewSet(viewsets.ModelViewSet):
    queryset = ClaimAssessment.objects.select_related("claim", "assessor", "accepted_by").all()
    serializer_class = ClaimAssessmentSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["claim", "assessment_type", "is_accepted"]
    ordering_fields = ["assessment_date", "created_at"]
    
    def get_permissions(self):
        return [IsClaimsOfficer()]


class ClaimPaymentViewSet(viewsets.ModelViewSet):
    queryset = ClaimPayment.objects.select_related("claim", "approved_by", "processed_by").all()
    serializer_class = ClaimPaymentSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["transaction_reference", "payee_name"]
    filterset_fields = ["claim", "payment_type", "payment_method"]
    ordering_fields = ["payment_date", "created_at"]
    
    def get_permissions(self):
        return [IsClaimsOfficer()]


class ClaimInvestigationViewSet(viewsets.ModelViewSet):
    queryset = ClaimInvestigation.objects.select_related("claim", "investigator").all()
    serializer_class = ClaimInvestigationSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["case_reference"]
    filterset_fields = ["claim", "investigation_type", "investigation_status"]
    ordering_fields = ["opened_date", "created_at"]
    
    def get_permissions(self):
        return [IsClaimsOfficer()]
