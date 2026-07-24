from rest_framework import viewsets
from apps.audit.models import AuditLog, DataChangeLog
from apps.audit.serializers import AuditLogSerializer, DataChangeLogSerializer
from apps.core.permissions import IsAuditor, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["entity_type", "entity_name", "description", "user__email"]
    ordering_fields = ["action_type", "entity_type", "ip_address", "created_at"]
    filterset_fields = ["user", "action_type", "entity_type", "is_success"]
    
    def get_permissions(self):
        return [IsAuditor()]


class DataChangeLogViewSet(viewsets.ModelViewSet):
    queryset = DataChangeLog.objects.select_related("changed_by").all()
    serializer_class = DataChangeLogSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["entity_type", "field_name", "changed_by__email"]
    ordering_fields = ["entity_type", "field_name", "created_at"]
    filterset_fields = ["entity_type", "changed_by", "field_name"]
    
    def get_permissions(self):
        return [IsAuditor()]
