import uuid

from django.db import models
from django.utils import timezone

from apps.core.models import UUIDModel, StatusModel, SoftDeleteModel


class Tenant(UUIDModel, StatusModel):
    class Tier(models.TextChoices):
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"
        UNLIMITED = "unlimited", "Unlimited"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.PROFESSIONAL)
    logo = models.ImageField(upload_to="tenants/logos/", blank=True, null=True)
    website = models.URLField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_identification_number = models.CharField(max_length=100, blank=True)
    insurance_license_number = models.CharField(max_length=100, blank=True)
    max_users = models.PositiveIntegerField(default=50)
    max_policies = models.PositiveIntegerField(default=10000)
    settings = models.JSONField(default=dict, blank=True)
    branding = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=50, default="Africa/Lagos")
    currency = models.CharField(max_length=3, default="NGN")
    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_trial_expired(self):
        if self.trial_ends_at:
            return timezone.now() > self.trial_ends_at
        return False

    @property
    def active_users_count(self):
        return self.users.filter(is_active=True).count()


class TenantInvitation(UUIDModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=50)
    invited_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation to {self.email} for {self.tenant.name}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def accept(self):
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["status", "accepted_at", "updated_at"])

    def revoke(self):
        self.status = self.Status.REVOKED
        self.save(update_fields=["status", "updated_at"])
