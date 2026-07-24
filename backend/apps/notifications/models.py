from django.conf import settings
from django.db import models

from apps.core.models import StatusModel, TenantModel


class NotificationTemplate(TenantModel, StatusModel):
    class ChannelType(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App Notification"
        WEBHOOK = "webhook", "Webhook"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    channel = models.CharField(max_length=20, choices=ChannelType.choices, db_index=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    html_body = models.TextField(blank=True)
    description = models.TextField(blank=True)
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of template variables: ['first_name', 'policy_number', ...]",
    )
    is_default = models.BooleanField(default=False)
    from_email = models.EmailField(blank=True)
    from_name = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"
        indexes = [
            models.Index(fields=["tenant", "channel"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.channel})"


class Notification(TenantModel, StatusModel):
    class NotificationType(models.TextChoices):
        POLICY_ISSUED = "policy_issued", "Policy Issued"
        POLICY_RENEWAL = "policy_renewal", "Policy Renewal Due"
        POLICY_EXPIRED = "policy_expired", "Policy Expired"
        PAYMENT_RECEIVED = "payment_received", "Payment Received"
        PAYMENT_OVERDUE = "payment_overdue", "Payment Overdue"
        CLAIM_RECEIVED = "claim_received", "Claim Received"
        CLAIM_UPDATE = "claim_update", "Claim Status Update"
        CLAIM_SETTLED = "claim_settled", "Claim Settled"
        QUOTE_READY = "quote_ready", "Quote Ready"
        QUOTE_EXPIRING = "quote_expiring", "Quote Expiring"
        DOCUMENT_UPLOADED = "document_uploaded", "Document Uploaded"
        COMMISSION_EARNED = "commission_earned", "Commission Earned"
        SYSTEM = "system", "System Notification"
        REMINDER = "reminder", "Reminder"
        ALERT = "alert", "Alert"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, db_index=True)
    channel = models.CharField(max_length=20, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    subject = models.CharField(max_length=500, blank=True)
    message = models.TextField()
    html_message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    send_error = models.TextField(blank=True)
    reference_type = models.CharField(max_length=100, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["tenant", "notification_type"]),
            models.Index(fields=["channel", "is_sent"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.recipient.email}"

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])


class NotificationPreference(TenantModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    notification_type = models.CharField(max_length=30, db_index=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ["notification_type"]
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "notification_type"],
                name="unique_user_notification_type",
            ),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.user.email}"
