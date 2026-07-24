from rest_framework import viewsets
from apps.dealers.models import Dealer
from apps.dealers.serializers import DealerListSerializer, DealerDetailSerializer
from apps.core.permissions import IsTenantAdmin, IsDealer
from apps.core.pagination import StandardResultsPagination


class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.select_related("user", "branch").all()
    pagination_class = StandardResultsPagination
    search_fields = ["dealer_code", "company_name", "trading_name", "contact_person", "email"]
    ordering_fields = ["dealer_code", "company_name", "created_at"]
    filterset_fields = ["status", "branch", "dealer_type"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return DealerListSerializer
        return DealerDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsDealer()]
