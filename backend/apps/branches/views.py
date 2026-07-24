from rest_framework import viewsets
from apps.branches.models import Branch
from apps.branches.serializers import BranchListSerializer, BranchDetailSerializer
from apps.core.permissions import IsTenantAdmin, IsBranchManager
from apps.core.pagination import StandardResultsPagination


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.select_related("manager", "parent").all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "email", "phone"]
    ordering_fields = ["name", "code", "branch_type", "created_at"]
    filterset_fields = ["status", "branch_type", "parent"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return BranchListSerializer
        return BranchDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsBranchManager()]
