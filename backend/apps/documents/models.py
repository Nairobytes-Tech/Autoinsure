from django.conf import settings
from django.db import models

from apps.core.models import StatusModel, SoftDeleteModel, TenantModel


class DocumentCategory(TenantModel, StatusModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Document Category"
        verbose_name_plural = "Document Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "slug"],
                name="unique_doc_category_slug_per_tenant",
            ),
        ]

    def __str__(self):
        return self.name


class Document(SoftDeleteModel):
    class AccessLevel(models.TextChoices):
        PRIVATE = "private", "Private"
        TENANT = "tenant", "Tenant Wide"
        PUBLIC = "public", "Public"

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.PRIVATE)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    version = models.CharField(max_length=20, default="1.0")
    tags = models.JSONField(default=list, blank=True)
    reference_type = models.CharField(max_length=100, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)
    is_template = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        indexes = [
            models.Index(fields=["tenant", "category"]),
            models.Index(fields=["tenant", "title"]),
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["access_level"]),
            models.Index(fields=["is_template"]),
        ]

    def __str__(self):
        return self.title


class DocumentVersion(TenantModel):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.CharField(max_length=20)
    file = models.FileField(upload_to="document_versions/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    change_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version_number"],
                name="unique_document_version",
            ),
        ]

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
