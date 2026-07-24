from rest_framework import serializers
from apps.claims.models import Claim, ClaimActivity, ClaimDocument, ClaimAssessment, ClaimPayment, ClaimInvestigation


class ClaimListSerializer(serializers.ModelSerializer):
    outstanding_amount = serializers.ReadOnlyField()
    is_settled = serializers.ReadOnlyField()
    
    class Meta:
        model = Claim
        fields = [
            "id", "claim_number", "claim_status", "claim_type", "priority",
            "policy", "customer", "incident_date", "reported_date",
            "claim_amount", "approved_amount", "paid_amount", "currency",
            "third_party_involved", "fraud_flag", "assigned_to",
            "outstanding_amount", "is_settled", "created_at",
        ]


class ClaimDetailSerializer(serializers.ModelSerializer):
    outstanding_amount = serializers.ReadOnlyField()
    approval_percentage = serializers.ReadOnlyField()
    is_settled = serializers.ReadOnlyField()
    
    class Meta:
        model = Claim
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ClaimActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimActivity
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDocument
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ClaimAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimAssessment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ClaimPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimPayment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ClaimInvestigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimInvestigation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
