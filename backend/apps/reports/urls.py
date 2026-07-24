from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reports.views import ReportViewSet, ReportScheduleViewSet

router = DefaultRouter()
router.register(r"", ReportViewSet, basename="report")
router.register(r"schedules", ReportScheduleViewSet, basename="report-schedule")

urlpatterns = [
    path("", include(router.urls)),
]
