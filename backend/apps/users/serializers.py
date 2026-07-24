from rest_framework import serializers
from apps.users.models import User, UserSession


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name", "phone_number",
            "role", "tenant", "branch", "is_active", "is_platform_admin",
            "mfa_enabled", "date_joined", "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    is_locked = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name", "phone_number",
            "avatar", "role", "tenant", "branch", "is_active", "is_staff",
            "is_platform_admin", "date_joined", "last_login", "email_verified",
            "phone_verified", "mfa_enabled", "force_password_change",
            "failed_login_attempts", "locked_until", "is_locked", "metadata",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "date_joined", "last_login", "failed_login_attempts", "locked_until", "created_at", "updated_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone_number",
            "role", "tenant", "branch", "password",
        ]
        read_only_fields = ["id"]
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            "id", "user", "ip_address", "user_agent", "device_info",
            "created_at", "last_activity", "is_active",
        ]
        read_only_fields = ["id", "created_at", "last_activity"]
