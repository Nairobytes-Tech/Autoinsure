from django.contrib import admin
from apps.workflows.models import WorkflowTemplate, WorkflowInstance, WorkflowStep


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "entity_type", "trigger_type", "is_default", "version", "status"]
    list_filter = ["trigger_type", "is_default", "status"]
    search_fields = ["name", "code", "entity_type"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ["template", "entity_type", "entity_id", "instance_status",
                    "current_step", "total_steps", "initiated_by", "started_at", "completed_at"]
    list_filter = ["instance_status"]
    search_fields = ["entity_type", "entity_id"]
    readonly_fields = ["id", "started_at", "created_at", "updated_at"]


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ["instance", "step_number", "step_type", "name", "status", "assigned_to", "completed_at"]
    list_filter = ["step_type", "status"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
