from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.workflows.views import WorkflowTemplateViewSet, WorkflowInstanceViewSet, WorkflowStepViewSet

router = DefaultRouter()
router.register(r"templates", WorkflowTemplateViewSet, basename="workflow-template")
router.register(r"instances", WorkflowInstanceViewSet, basename="workflow-instance")
router.register(r"steps", WorkflowStepViewSet, basename="workflow-step")

urlpatterns = [
    path("", include(router.urls)),
]
