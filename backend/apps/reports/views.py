from rest_framework import viewsets
from apps.reports.models import Report, ReportSchedule
from apps.reports.serializers import ReportListSerializer, ReportDetailSerializer, ReportScheduleSerializer
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin, IsExecutiveManagement
from apps.core.pagination import StandardResultsPagination


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related("generated_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "description"]
    ordering_fields = ["name", "report_type", "format", "last_generated_at", "created_at"]
    filterset_fields = ["report_type", "format", "is_scheduled", "generated_by"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ReportListSerializer
        return ReportDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsExecutiveManagement()]


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.select_related("report").all()
    serializer_class = ReportScheduleSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["report", "frequency", "is_active"]
    ordering_fields = ["frequency", "next_run_at", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
