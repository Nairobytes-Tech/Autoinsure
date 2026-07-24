from rest_framework import serializers
from apps.branches.models import Branch


class BranchListSerializer(serializers.ModelSerializer):
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Branch
        fields = [
            "id", "name", "code", "branch_type", "manager", "parent",
            "email", "phone", "city", "state", "country", "status",
            "target_premium", "achieved_premium", "total_policies",
            "total_customers", "total_agents", "achievement_percentage", "created_at",
        ]


class BranchDetailSerializer(serializers.ModelSerializer):
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Branch
        fields = "__all__"
        read_only_fields = ["id", "total_policies", "total_customers", "total_agents",
                            "total_brokers", "total_dealers", "achieved_premium", "created_at", "updated_at"]
