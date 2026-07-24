from rest_framework import serializers
from apps.underwriting.models import UnderwritingRule, UnderwritingDecision, ReferralQueue


class UnderwritingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnderwritingRule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class UnderwritingDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnderwritingDecision
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ReferralQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralQueue
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
