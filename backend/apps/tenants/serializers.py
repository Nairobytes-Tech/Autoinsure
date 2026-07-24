from rest_framework import serializers
from apps.tenants.models import Tenant, TenantInvitation


class TenantListSerializer(serializers.ModelSerializer):
    active_users_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = [
            "id", "name", "code", "slug", "tier", "logo", "website", "email",
            "phone", "city", "state", "country", "is_active", "active_users_count",
            "max_users", "max_policies", "currency", "timezone", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TenantDetailSerializer(serializers.ModelSerializer):
    active_users_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tenant
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class TenantInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantInvitation
        fields = [
            "id", "tenant", "email", "role", "invited_by", "token",
            "status", "expires_at", "accepted_at", "message",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "token", "created_at", "updated_at"]
