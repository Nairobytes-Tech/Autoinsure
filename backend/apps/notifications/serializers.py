from rest_framework import serializers
from apps.notifications.models import NotificationTemplate, Notification, NotificationPreference


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "recipient", "notification_type", "channel", "priority",
            "subject", "message", "is_read", "read_at", "is_sent",
            "sent_at", "reference_type", "reference_id", "created_at",
        ]


class NotificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
