from rest_framework import viewsets
from apps.agents.models import Agent
from apps.agents.serializers import AgentListSerializer, AgentDetailSerializer
from apps.core.permissions import IsTenantAdmin, IsAgent
from apps.core.pagination import StandardResultsPagination


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.select_related("user", "branch", "supervisor").all()
    pagination_class = StandardResultsPagination
    search_fields = ["agent_code", "first_name", "last_name", "email", "phone"]
    ordering_fields = ["agent_code", "first_name", "last_name", "created_at"]
    filterset_fields = ["status", "branch", "supervisor"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return AgentListSerializer
        return AgentDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsAgent()]
