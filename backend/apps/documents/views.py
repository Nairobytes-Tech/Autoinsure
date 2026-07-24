from rest_framework import viewsets
from apps.documents.models import DocumentCategory, Document, DocumentVersion
from apps.documents.serializers import (
    DocumentCategoryListSerializer, DocumentCategoryDetailSerializer,
    DocumentListSerializer, DocumentDetailSerializer, DocumentVersionSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "display_order"]
    filterset_fields = ["status", "parent"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return DocumentCategoryListSerializer
        return DocumentCategoryDetailSerializer
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("category", "uploaded_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["title", "description", "original_filename"]
    ordering_fields = ["title", "access_level", "version", "created_at"]
    filterset_fields = ["category", "access_level", "uploaded_by", "is_template"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        return DocumentDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.select_related("document", "uploaded_by").all()
    serializer_class = DocumentVersionSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["document", "version_number"]
    ordering_fields = ["version_number", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
