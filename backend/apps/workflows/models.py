from django.conf import settings
from django.db import models

from apps.core.models import StatusModel, TenantModel


class WorkflowTemplate(TenantModel, StatusModel):
    class TriggerType(models.TextChoices):
        MANUAL = "manual", "Manual"
        ON_CREATE = "on_create", "On Create"
        ON_UPDATE = "on_update", "On Update"
        ON_STATUS_CHANGE = "on_status_change", "On Status Change"
        ON_DATE = "on_date", "On Date"
        ON_EVENT = "on_event", "On Event"
        SCHEDULED = "scheduled", "Scheduled"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    trigger_type = models.CharField(max_length=20, choices=TriggerType.choices, db_index=True)
    trigger_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Trigger configuration: entity, conditions, schedule",
    )
    steps = models.JSONField(
        default=list,
        blank=True,
        help_text="Ordered list of workflow steps: [{type, config, assignees}]",
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Entry conditions for the workflow",
    )
    variables = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template variables",
    )
    is_default = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Workflow Template"
        verbose_name_plural = "Workflow Templates"
        indexes = [
            models.Index(fields=["tenant", "entity_type"]),
            models.Index(fields=["tenant", "trigger_type"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class WorkflowInstance(TenantModel, StatusModel):
    class InstanceStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING = "waiting", "Waiting"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    instance_status = models.CharField(
        max_length=20, choices=InstanceStatus.choices,
        default=InstanceStatus.PENDING, db_index=True,
    )
    current_step = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_workflows",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data collected during workflow execution",
    )
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Workflow Instance"
        verbose_name_plural = "Workflow Instances"
        indexes = [
            models.Index(fields=["tenant", "instance_status"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["template", "instance_status"]),
            models.Index(fields=["due_date", "instance_status"]),
        ]

    def __str__(self):
        return f"{self.template.name} - {self.entity_type}:{self.entity_id}"

    @property
    def progress_percentage(self):
        if self.total_steps > 0:
            return (self.current_step / self.total_steps) * 100
        return 0


class WorkflowStep(TenantModel):
    class StepType(models.TextChoices):
        APPROVAL = "approval", "Approval"
        REVIEW = "review", "Review"
        NOTIFICATION = "notification", "Notification"
        TASK = "task", "Task"
        WAIT = "wait", "Wait"
        CONDITION = "condition", "Condition"
        AUTOMATION = "automation", "Automation"
        ESCALATION = "escalation", "Escalation"

    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name="step_instances",
    )
    step_number = models.PositiveIntegerField()
    step_type = models.CharField(max_length=20, choices=StepType.choices)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("skipped", "Skipped"),
            ("failed", "Failed"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        db_index=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_step_assignments",
    )
    assigned_role = models.CharField(max_length=50, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    action_taken = models.CharField(max_length=100, blank=True)
    action_notes = models.TextField(blank=True)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["step_number"]
        verbose_name = "Workflow Step"
        verbose_name_plural = "Workflow Steps"
        constraints = [
            models.UniqueConstraint(
                fields=["instance", "step_number"],
                name="unique_workflow_step_number",
            ),
        ]
        indexes = [
            models.Index(fields=["instance", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date", "status"]),
        ]

    def __str__(self):
        return f"Step {self.step_number}: {self.name}"
