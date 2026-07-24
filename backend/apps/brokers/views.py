from rest_framework import viewsets
from apps.brokers.models import Broker
from apps.brokers.serializers import BrokerListSerializer, BrokerDetailSerializer
from apps.core.permissions import IsTenantAdmin, IsBroker
from apps.core.pagination import StandardResultsPagination


class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.select_related("user", "branch").all()
    pagination_class = StandardResultsPagination
    search_fields = ["broker_code", "company_name", "trading_name", "contact_person", "email"]
    ordering_fields = ["broker_code", "company_name", "created_at"]
    filterset_fields = ["status", "branch", "license_type"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return BrokerListSerializer
        return BrokerDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsBroker()]
