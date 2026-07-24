from rest_framework import serializers
from apps.ai_features.models import AIModel, AIPrediction, FraudAlert


class AIModelListSerializer(serializers.ModelSerializer):
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = AIModel
        fields = [
            "id", "name", "code", "model_type", "description", "model_version",
            "accuracy_score", "avg_response_time_ms", "total_predictions",
            "successful_predictions", "failed_predictions", "is_active", "success_rate", "created_at",
        ]


class AIModelDetailSerializer(serializers.ModelSerializer):
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = AIModel
        fields = "__all__"
        read_only_fields = ["id", "total_predictions", "successful_predictions",
                            "failed_predictions", "avg_response_time_ms", "created_at", "updated_at"]


class AIPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class FraudAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudAlert
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
