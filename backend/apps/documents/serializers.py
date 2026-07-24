from rest_framework import serializers
from apps.documents.models import DocumentCategory, Document, DocumentVersion


class DocumentCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = [
            "id", "name", "slug", "description", "icon", "display_order",
            "parent", "status", "created_at",
        ]


class DocumentCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id", "title", "description", "category", "original_filename",
            "file_size", "mime_type", "access_level", "uploaded_by",
            "version", "is_template", "download_count", "created_at",
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["id", "download_count", "created_at", "updated_at"]
