from rest_framework import serializers
from apps.commissions.models import CommissionStructure, Commission, CommissionPayment


class CommissionStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionStructure
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CommissionListSerializer(serializers.ModelSerializer):
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Commission
        fields = [
            "id", "policy", "structure", "earned_by_type", "commission_status",
            "premium_amount", "commission_rate", "commission_amount", "bonus_amount",
            "total_amount", "paid_amount", "outstanding_amount", "is_renewal",
            "calculation_date", "is_fully_paid", "created_at",
        ]


class CommissionDetailSerializer(serializers.ModelSerializer):
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Commission
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CommissionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionPayment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
