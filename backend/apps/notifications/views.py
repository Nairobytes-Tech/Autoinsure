from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.notifications.models import NotificationTemplate, Notification, NotificationPreference
from apps.notifications.serializers import (
    NotificationTemplateSerializer, NotificationListSerializer,
    NotificationDetailSerializer, NotificationPreferenceSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "subject"]
    ordering_fields = ["name", "channel", "created_at"]
    filterset_fields = ["channel", "is_default"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("recipient", "template").all()
    pagination_class = StandardResultsPagination
    search_fields = ["subject", "message", "recipient__email"]
    ordering_fields = ["notification_type", "channel", "priority", "is_read", "created_at"]
    filterset_fields = ["recipient", "notification_type", "channel", "priority", "is_read", "is_sent"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        return NotificationDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_read()
        return Response({"status": "Notification marked as read."})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request, pk=None):
        from django.utils import timezone
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        count = notifications.update(is_read=True, read_at=timezone.now(), updated_at=timezone.now())
        return Response({"status": f"{count} notifications marked as read."})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.select_related("user").all()
    serializer_class = NotificationPreferenceSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["user", "notification_type"]
    ordering_fields = ["notification_type"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]
