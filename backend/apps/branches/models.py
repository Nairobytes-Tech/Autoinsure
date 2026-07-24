from django.conf import settings
from django.db import models

from apps.core.models import PhoneNumberField, StatusModel, TenantModel


class Branch(TenantModel, StatusModel):
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True)
    branch_type = models.CharField(
        max_length=30,
        choices=[
            ("head_office", "Head Office"),
            ("regional", "Regional Office"),
            ("branch", "Branch Office"),
            ("sub_branch", "Sub-Branch"),
            ("satellite", "Satellite Office"),
        ],
        default="branch",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_branches",
    )
    email = models.EmailField(blank=True)
    phone = PhoneNumberField()
    alternative_phone = PhoneNumberField()
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    working_days = models.JSONField(
        default=list,
        blank=True,
        help_text="List of working days: ['monday', 'tuesday', ...]",
    )
    max_users = models.PositiveIntegerField(default=50)
    max_policies = models.PositiveIntegerField(default=5000)
    target_premium = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    achieved_premium = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_policies = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    total_agents = models.PositiveIntegerField(default=0)
    total_brokers = models.PositiveIntegerField(default=0)
    total_dealers = models.PositiveIntegerField(default=0)
    settings = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        indexes = [
            models.Index(fields=["tenant", "code"]),
            models.Index(fields=["tenant", "name"]),
            models.Index(fields=["branch_type", "status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def achievement_percentage(self):
        if self.target_premium > 0:
            return (self.achieved_premium / self.target_premium) * 100
        return 0
