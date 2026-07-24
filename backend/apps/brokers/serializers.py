from rest_framework import serializers
from apps.brokers.models import Broker


class BrokerListSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.ReadOnlyField()
    
    class Meta:
        model = Broker
        fields = [
            "id", "broker_code", "company_name", "trading_name", "contact_person",
            "email", "phone", "license_number", "license_type", "branch", "status",
            "commission_rate", "total_premium_placed", "total_commission_earned",
            "total_policies_sold", "credit_limit", "credit_balance",
            "outstanding_balance", "rating", "created_at",
        ]


class BrokerDetailSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.ReadOnlyField()
    
    class Meta:
        model = Broker
        fields = "__all__"
        read_only_fields = ["id", "total_premium_placed", "total_commission_earned",
                            "total_commission_paid", "total_policies_sold", "total_claims_generated",
                            "credit_balance", "created_at", "updated_at"]
