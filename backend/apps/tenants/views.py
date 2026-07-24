from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.tenants.models import Tenant, TenantInvitation
from apps.tenants.serializers import TenantListSerializer, TenantDetailSerializer, TenantInvitationSerializer
from apps.core.permissions import IsPlatformAdmin, IsTenantAdmin
from apps.core.pagination import StandardResultsPagination


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "email"]
    ordering_fields = ["name", "code", "tier", "created_at"]
    filterset_fields = ["status", "tier", "is_active"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return TenantListSerializer
        return TenantDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsPlatformAdmin()]
        return [IsPlatformAdmin()]


class TenantInvitationViewSet(viewsets.ModelViewSet):
    queryset = TenantInvitation.objects.select_related("tenant", "invited_by").all()
    serializer_class = TenantInvitationSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["email", "role"]
    ordering_fields = ["created_at", "status"]
    filterset_fields = ["status", "role"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        if invitation.is_expired:
            return Response({"error": "Invitation has expired."}, status=status.HTTP_400_BAD_REQUEST)
        invitation.accept()
        return Response({"status": "Invitation accepted."})

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        invitation = self.get_object()
        invitation.revoke()
        return Response({"status": "Invitation revoked."})
