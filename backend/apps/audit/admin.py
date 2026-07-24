from django.contrib import admin
from apps.audit.models import AuditLog, DataChangeLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action_type", "entity_type", "entity_name", "user", "ip_address", "is_success", "created_at"]
    list_filter = ["action_type", "entity_type", "is_success"]
    search_fields = ["entity_type", "entity_name", "description", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(DataChangeLog)
class DataChangeLogAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "entity_id", "field_name", "changed_by", "batch_id", "created_at"]
    list_filter = ["entity_type", "field_name"]
    search_fields = ["entity_type", "field_name", "changed_by__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
