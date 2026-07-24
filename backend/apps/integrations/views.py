from rest_framework import viewsets
from apps.integrations.models import Integration, IntegrationLog
from apps.integrations.serializers import (
    IntegrationListSerializer, IntegrationDetailSerializer, IntegrationLogSerializer,
)
from apps.core.permissions import IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.select_related("configured_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "integration_type", "is_active", "created_at"]
    filterset_fields = ["integration_type", "is_active"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return IntegrationListSerializer
        return IntegrationDetailSerializer
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class IntegrationLogViewSet(viewsets.ModelViewSet):
    queryset = IntegrationLog.objects.select_related("integration").all()
    serializer_class = IntegrationLogSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["request_url", "error_message"]
    filterset_fields = ["integration", "level", "direction", "is_success"]
    ordering_fields = ["level", "direction", "response_time_ms", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
