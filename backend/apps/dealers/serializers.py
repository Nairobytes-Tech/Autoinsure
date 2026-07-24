from rest_framework import serializers
from apps.dealers.models import Dealer


class DealerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = [
            "id", "dealer_code", "company_name", "trading_name", "contact_person",
            "email", "phone", "dealer_type", "branch", "status",
            "commission_rate", "total_policies_sold", "total_premium_generated",
            "total_commission_earned", "total_vehicles_insured", "created_at",
        ]


class DealerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = "__all__"
        read_only_fields = ["id", "total_policies_sold", "total_premium_generated",
                            "total_commission_earned", "total_commission_paid",
                            "total_vehicles_insured", "created_at", "updated_at"]
