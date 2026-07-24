from rest_framework import viewsets
from apps.workflows.models import WorkflowTemplate, WorkflowInstance, WorkflowStep
from apps.workflows.serializers import (
    WorkflowTemplateSerializer, WorkflowInstanceSerializer, WorkflowStepSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "description", "entity_type"]
    ordering_fields = ["name", "entity_type", "trigger_type", "version", "created_at"]
    filterset_fields = ["entity_type", "trigger_type", "is_default"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.select_related("template", "initiated_by").all()
    serializer_class = WorkflowInstanceSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["entity_type", "entity_id"]
    filterset_fields = ["template", "entity_type", "instance_status", "initiated_by"]
    ordering_fields = ["instance_status", "started_at", "due_date", "completed_at"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]


class WorkflowStepViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStep.objects.select_related("instance", "assigned_to").all()
    serializer_class = WorkflowStepSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["instance", "step_type", "status", "assigned_to"]
    ordering_fields = ["step_number", "step_type", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
