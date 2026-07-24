from django.conf import settings
from django.db import models

from apps.core.models import TenantModel, StatusModel


class AIModel(TenantModel, StatusModel):
    class ModelType(models.TextChoices):
        FRAUD_DETECTION = "fraud_detection", "Fraud Detection"
        RISK_SCORING = "risk_scoring", "Risk Scoring"
        PREMIUM_OPTIMIZATION = "premium_optimization", "Premium Optimization"
        CLAIMS_TRIAGE = "claims_triage", "Claims Triage"
        CUSTOMER_CHURN = "customer_churn", "Customer Churn Prediction"
        DOCUMENT_OCR = "document_ocr", "Document OCR"
        NATURAL_LANGUAGE = "natural_language", "Natural Language Processing"
        SENTIMENT = "sentiment", "Sentiment Analysis"
        RECOMMENDATION = "recommendation", "Recommendation Engine"
        CUSTOM = "custom", "Custom Model"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=30, choices=ModelType.choices, db_index=True)
    model_endpoint = models.URLField(blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    model_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Model configuration parameters",
    )
    input_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Expected input format",
    )
    output_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Expected output format",
    )
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_response_time_ms = models.PositiveIntegerField(default=0)
    total_predictions = models.PositiveIntegerField(default=0)
    successful_predictions = models.PositiveIntegerField(default=0)
    failed_predictions = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    configured_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        indexes = [
            models.Index(fields=["tenant", "model_type"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.model_type})"

    @property
    def success_rate(self):
        if self.total_predictions > 0:
            return (self.successful_predictions / self.total_predictions) * 100
        return 0


class AIPrediction(TenantModel):
    model = models.ForeignKey(
        AIModel,
        on_delete=models.PROTECT,
        related_name="predictions",
    )
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    input_data = models.JSONField(default=dict)
    prediction_result = models.JSONField(default=dict)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    prediction_label = models.CharField(max_length=255, blank=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_accepted = models.BooleanField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    feedback = models.TextField(blank=True)
    response_time_ms = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI Prediction"
        verbose_name_plural = "AI Predictions"
        indexes = [
            models.Index(fields=["model", "entity_type"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.model.name} - {self.entity_type}:{self.entity_id}"


class FraudAlert(TenantModel, StatusModel):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class AlertStatus(models.TextChoices):
        NEW = "new", "New"
        INVESTIGATING = "investigating", "Investigating"
        CONFIRMED = "confirmed", "Confirmed Fraud"
        FALSE_POSITIVE = "false_positive", "False Positive"
        RESOLVED = "resolved", "Resolved"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_alerts",
    )
    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_alerts",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_alerts",
    )
    prediction = models.ForeignKey(
        AIPrediction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_alerts",
    )
    alert_status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.NEW, db_index=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2)
    alert_type = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    evidence = models.JSONField(default=list, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_alert_assignments",
    )
    investigation_notes = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Fraud Alert"
        verbose_name_plural = "Fraud Alerts"
        indexes = [
            models.Index(fields=["tenant", "alert_status"]),
            models.Index(fields=["tenant", "severity"]),
            models.Index(fields=["assigned_to", "alert_status"]),
            models.Index(fields=["fraud_score"]),
        ]

    def __str__(self):
        return f"Fraud Alert - {self.title}"
