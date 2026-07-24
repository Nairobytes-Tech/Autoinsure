from rest_framework import serializers
from apps.policies.models import Policy, PolicyEndorsement, PolicyRenewal, PolicyCancellation, PolicyDocument


class PolicyListSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = Policy
        fields = [
            "id", "policy_number", "policy_type", "policy_status", "payment_status",
            "customer", "product", "start_date", "end_date", "premium_amount",
            "sum_insured", "net_premium", "currency", "agent", "broker", "dealer",
            "branch", "is_active", "is_expired", "days_until_expiry", "created_at",
        ]


class PolicyDetailSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    coverage_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Policy
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PolicyEndorsementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyEndorsement
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PolicyRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyRenewal
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PolicyCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCancellation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PolicyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocument
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
