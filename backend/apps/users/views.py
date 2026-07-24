from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.models import User, UserSession
from apps.users.serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer, UserSessionSerializer
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("tenant", "branch").all()
    pagination_class = StandardResultsPagination
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering_fields = ["email", "first_name", "last_name", "role", "date_joined"]
    filterset_fields = ["role", "tenant", "branch", "is_active", "is_platform_admin"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserCreateSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]

    @action(detail=True, methods=["post"])
    def lock(self, request, pk=None):
        user = self.get_object()
        minutes = int(request.data.get("minutes", 30))
        user.lock_account(minutes=minutes)
        return Response({"status": "Account locked."})

    @action(detail=True, methods=["post"])
    def unlock(self, request, pk=None):
        user = self.get_object()
        user.unlock_account()
        return Response({"status": "Account unlocked."})


class UserSessionViewSet(viewsets.ModelViewSet):
    queryset = UserSession.objects.select_related("user").all()
    serializer_class = UserSessionSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["user", "is_active"]
    ordering_fields = ["last_activity", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
