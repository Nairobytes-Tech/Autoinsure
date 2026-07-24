import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(UUIDModel):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["deleted_at", "deleted_by", "updated_at"])

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["deleted_at", "deleted_by", "updated_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class TenantModel(UUIDModel):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.PROTECT,
        related_name="%(class)s_set",
        db_index=True,
    )

    class Meta:
        abstract = True

    class TenantManager(SoftDeleteManager):
        def get_queryset(self):
            return super().get_queryset()


class HistoricalModel(models.Model):
    class Meta:
        abstract = True

    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    history_date = models.DateTimeField(auto_now_add=True)
    history_type = models.CharField(
        max_length=1,
        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
    )
    history_user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.history_type:
            self.history_type = "~"
        super().save(*args, **kwargs)


class MoneyField(models.DecimalField):
    def __init__(self, *args, max_digits=15, decimal_places=2, **kwargs):
        kwargs.setdefault("max_digits", max_digits)
        kwargs.setdefault("decimal_places", decimal_places)
        super().__init__(*args, **kwargs)


class PhoneNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 20)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)


class StatusModel(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "Pending"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    class Meta:
        abstract = True
