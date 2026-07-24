from rest_framework import serializers
from apps.audit.models import AuditLog, DataChangeLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DataChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataChangeLog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
