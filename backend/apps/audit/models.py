from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class AuditLog(TenantModel):
    class ActionType(models.TextChoices):
        CREATE = "create", "Create"
        READ = "read", "Read"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        EXPORT = "export", "Export"
        IMPORT = "import", "Import"
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        ASSIGN = "assign", "Assign"
        STATUS_CHANGE = "status_change", "Status Change"
        PAYMENT = "payment", "Payment"
        DOWNLOAD = "download", "Download"
        UPLOAD = "upload", "Upload"
        EMAIL_SENT = "email_sent", "Email Sent"
        SMS_SENT = "sms_sent", "SMS Sent"
        SYSTEM = "system", "System Action"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action_type = models.CharField(max_length=20, choices=ActionType.choices, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(null=True, blank=True, db_index=True)
    entity_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_body = models.JSONField(null=True, blank=True)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=["tenant", "action_type"]),
            models.Index(fields=["tenant", "entity_type"]),
            models.Index(fields=["user", "action_type"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        entity = f"{self.entity_type}:{self.entity_name}" if self.entity_name else self.entity_type
        return f"{self.action_type} - {entity}"


class DataChangeLog(TenantModel):
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    field_name = models.CharField(max_length=255, db_index=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    old_value_json = models.JSONField(null=True, blank=True)
    new_value_json = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="data_changes",
    )
    change_reason = models.TextField(blank=True)
    batch_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Data Change Log"
        verbose_name_plural = "Data Change Logs"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["changed_by"]),
            models.Index(fields=["field_name"]),
            models.Index(fields=["batch_id"]),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} - {self.field_name}"
