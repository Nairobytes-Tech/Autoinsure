from django.contrib import admin
from apps.documents.models import DocumentCategory, Document, DocumentVersion


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "display_order", "status"]
    list_filter = ["status"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "original_filename", "file_size", "access_level", "is_template", "version", "created_at"]
    list_filter = ["access_level", "is_template", "category"]
    search_fields = ["title", "description", "original_filename"]
    readonly_fields = ["id", "download_count", "created_at", "updated_at"]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ["document", "version_number", "original_filename", "file_size", "uploaded_by", "created_at"]
    list_filter = []
    search_fields = ["document__title", "version_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
