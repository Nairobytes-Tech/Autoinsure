from django.contrib import admin
from apps.reports.models import Report, ReportSchedule


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "format", "generated_by", "is_scheduled", "last_generated_at", "row_count"]
    list_filter = ["report_type", "format", "is_scheduled"]
    search_fields = ["name", "description"]
    readonly_fields = ["id", "row_count", "generation_time_ms", "created_at", "updated_at"]


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ["report", "frequency", "time_of_day", "next_run_at", "run_count"]
    list_filter = ["frequency", "is_active"]
    search_fields = ["report__name"]
    readonly_fields = ["id", "last_run_at", "run_count", "created_at", "updated_at"]
