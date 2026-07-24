from django.conf import settings
from django.db import models

from apps.core.models import StatusModel, TenantModel


class Report(TenantModel, StatusModel):
    class ReportType(models.TextChoices):
        PREMIUM_COLLECTION = "premium_collection", "Premium Collection Report"
        CLAIMS_SUMMARY = "claims_summary", "Claims Summary Report"
        POLICY_REGISTER = "policy_register", "Policy Register"
        REVENUE = "revenue", "Revenue Report"
        COMMISSION = "commission", "Commission Report"
        AGENT_PERFORMANCE = "agent_performance", "Agent Performance Report"
        BROKER_PERFORMANCE = "broker_performance", "Broker Performance Report"
        CUSTOMER = "customer", "Customer Report"
        PRODUCT_PERFORMANCE = "product_performance", "Product Performance"
        RENEWAL = "renewal", "Renewal Report"
        LAPSED = "lapsed", "Lapsed Policy Report"
        CANCELLATION = "cancellation", "Cancellation Report"
        FINANCIAL = "financial", "Financial Statement"
        REGULATORY = "regulatory", "Regulatory Report"
        FRAUD = "fraud", "Fraud Report"
        AGING = "aging", "Aging Report"
        CUSTOM = "custom", "Custom Report"

    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"
        CSV = "csv", "CSV"
        JSON = "json", "JSON"

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=ReportType.choices, db_index=True)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report parameters: date_from, date_to, filters, etc.",
    )
    file = models.FileField(upload_to="reports/%Y/%m/%d/", blank=True, null=True)
    file_size = models.PositiveIntegerField(default=0)
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    generation_time_ms = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        indexes = [
            models.Index(fields=["tenant", "report_type"]),
            models.Index(fields=["is_scheduled", "report_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportSchedule(TenantModel, StatusModel):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    frequency = models.CharField(max_length=20, choices=Frequency.choices, db_index=True)
    day_of_week = models.PositiveIntegerField(null=True, blank=True, help_text="0=Monday, 6=Sunday")
    day_of_month = models.PositiveIntegerField(null=True, blank=True)
    month_of_year = models.PositiveIntegerField(null=True, blank=True)
    time_of_day = models.TimeField()
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="report_schedules",
        blank=True,
    )
    recipient_emails = models.JSONField(default=list, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    run_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["next_run_at"]
        verbose_name = "Report Schedule"
        verbose_name_plural = "Report Schedules"
        indexes = [
            models.Index(fields=["tenant", "frequency", "is_active"]),
            models.Index(fields=["next_run_at"]),
        ]

    def __str__(self):
        return f"{self.report.name} - {self.frequency}"
