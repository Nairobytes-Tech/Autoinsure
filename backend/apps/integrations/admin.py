from django.contrib import admin
from apps.integrations.models import Integration, IntegrationLog


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "integration_type", "is_active", "total_requests",
                    "successful_requests", "failed_requests", "last_sync_at"]
    list_filter = ["integration_type", "is_active"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["id", "total_requests", "successful_requests", "failed_requests",
                       "avg_response_time_ms", "last_sync_at", "last_error_at",
                       "last_error_message", "created_at", "updated_at"]


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ["integration", "level", "direction", "request_method", "response_status",
                    "response_time_ms", "is_success", "created_at"]
    list_filter = ["level", "direction", "is_success"]
    search_fields = ["request_url", "error_message"]
    readonly_fields = ["id", "created_at", "updated_at"]
