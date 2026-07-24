from django.conf import settings
from django.db import models

from apps.core.models import StatusModel, TenantModel


class Integration(TenantModel, StatusModel):
    class IntegrationType(models.TextChoices):
        PAYMENT_GATEWAY = "payment_gateway", "Payment Gateway"
        SMS_PROVIDER = "sms_provider", "SMS Provider"
        EMAIL_PROVIDER = "email_provider", "Email Provider"
        MAPS = "maps", "Maps/Geolocation"
        KYC = "kyc", "KYC Provider"
        REGULATORY = "regulatory", "Regulatory API"
        INSURANCE_BROKER = "insurance_broker", "Insurance Broker API"
        ACCOUNTING = "accounting", "Accounting System"
        CRM = "crm", "CRM"
        DOCUMENT_SIGN = "document_sign", "Document Signing"
        AI_SERVICE = "ai_service", "AI Service"
        CUSTOM = "custom", "Custom Integration"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    integration_type = models.CharField(max_length=30, choices=IntegrationType.choices, db_index=True)
    api_base_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=500, blank=True)
    additional_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration parameters for the integration",
    )
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    timeout_seconds = models.PositiveIntegerField(default=30)
    retry_count = models.PositiveIntegerField(default=3)
    rate_limit_per_minute = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    last_error_message = models.TextField(blank=True)
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    avg_response_time_ms = models.PositiveIntegerField(default=0)
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
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"
        indexes = [
            models.Index(fields=["tenant", "integration_type"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.integration_type})"

    @property
    def success_rate(self):
        if self.total_requests > 0:
            return (self.successful_requests / self.total_requests) * 100
        return 0


class IntegrationLog(TenantModel):
    class LogLevel(models.TextChoices):
        DEBUG = "debug", "Debug"
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        CRITICAL = "critical", "Critical"

    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    level = models.CharField(max_length=10, choices=LogLevel.choices, db_index=True)
    direction = models.CharField(
        max_length=10,
        choices=[("inbound", "Inbound"), ("outbound", "Outbound")],
        db_index=True,
    )
    request_method = models.CharField(max_length=10, blank=True)
    request_url = models.CharField(max_length=1000, blank=True)
    request_headers = models.JSONField(null=True, blank=True)
    request_body = models.JSONField(null=True, blank=True)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    reference_type = models.CharField(max_length=100, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Integration Log"
        verbose_name_plural = "Integration Logs"
        indexes = [
            models.Index(fields=["integration", "level"]),
            models.Index(fields=["integration", "created_at"]),
            models.Index(fields=["is_success", "created_at"]),
        ]

    def __str__(self):
        return f"{self.integration.name} - {self.level}"
