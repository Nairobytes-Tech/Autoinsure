from rest_framework import serializers
from apps.integrations.models import Integration, IntegrationLog


class IntegrationListSerializer(serializers.ModelSerializer):
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Integration
        fields = [
            "id", "name", "code", "integration_type", "description",
            "api_base_url", "is_active", "last_sync_at", "last_error_at",
            "total_requests", "successful_requests", "failed_requests",
            "avg_response_time_ms", "success_rate", "created_at",
        ]


class IntegrationDetailSerializer(serializers.ModelSerializer):
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Integration
        fields = "__all__"
        read_only_fields = ["id", "total_requests", "successful_requests",
                            "failed_requests", "avg_response_time_ms", "last_sync_at",
                            "last_error_at", "last_error_message", "created_at", "updated_at"]


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
