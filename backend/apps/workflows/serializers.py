from rest_framework import serializers
from apps.workflows.models import WorkflowTemplate, WorkflowInstance, WorkflowStep


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkflowInstance
        fields = "__all__"
        read_only_fields = ["id", "started_at", "created_at", "updated_at"]


class WorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStep
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
