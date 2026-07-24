from rest_framework import serializers
from apps.reports.models import Report, ReportSchedule


class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id", "name", "description", "report_type", "format", "generated_by",
            "is_scheduled", "last_generated_at", "row_count", "error_message", "created_at",
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["id", "row_count", "generation_time_ms", "created_at", "updated_at"]


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = "__all__"
        read_only_fields = ["id", "last_run_at", "run_count", "created_at", "updated_at"]
