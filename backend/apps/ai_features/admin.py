from django.contrib import admin
from apps.ai_features.models import AIModel, AIPrediction, FraudAlert


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "model_type", "model_version", "accuracy_score", "is_active", "total_predictions"]
    list_filter = ["model_type", "is_active"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["id", "total_predictions", "successful_predictions", "failed_predictions",
                       "avg_response_time_ms", "created_at", "updated_at"]


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ["model", "entity_type", "entity_id", "prediction_label", "confidence_score", "risk_score", "is_accepted", "created_at"]
    list_filter = ["is_accepted"]
    search_fields = ["entity_type", "prediction_label"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ["title", "alert_type", "alert_status", "severity", "fraud_score", "claim", "assigned_to", "created_at"]
    list_filter = ["alert_status", "severity"]
    search_fields = ["title", "alert_type", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
