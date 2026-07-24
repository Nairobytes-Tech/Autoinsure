from rest_framework import serializers
from apps.agents.models import Agent


class AgentListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Agent
        fields = [
            "id", "agent_code", "first_name", "last_name", "full_name", "email",
            "phone", "branch", "status", "commission_rate", "target_premium",
            "achieved_premium", "total_policies_sold", "total_commission_earned",
            "achievement_percentage", "created_at",
        ]


class AgentDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Agent
        fields = "__all__"
        read_only_fields = ["id", "total_policies_sold", "total_claims_generated",
                            "total_commission_earned", "total_commission_paid", "created_at", "updated_at"]
