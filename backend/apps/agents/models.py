from django.conf import settings
from django.db import models

from apps.core.models import MoneyField, PhoneNumberField, StatusModel, TenantModel


class Agent(TenantModel, StatusModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="agent_profiles",
    )
    agent_code = models.CharField(max_length=30, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, db_index=True)
    last_name = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = PhoneNumberField()
    alternative_phone = PhoneNumberField()
    date_of_birth = models.DateField(null=True, blank=True)
    national_id_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    tax_identification_number = models.CharField(max_length=50, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
    )
    supervisor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    target_premium = MoneyField(default=0)
    achieved_premium = MoneyField(default=0)
    total_policies_sold = models.PositiveIntegerField(default=0)
    total_claims_generated = models.PositiveIntegerField(default=0)
    total_commission_earned = MoneyField(default=0)
    total_commission_paid = MoneyField(default=0)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    bank_sort_code = models.CharField(max_length=20, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    performance_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        indexes = [
            models.Index(fields=["tenant", "agent_code"]),
            models.Index(fields=["tenant", "first_name", "last_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.agent_code})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def achievement_percentage(self):
        if self.target_premium > 0:
            return (self.achieved_premium / self.target_premium) * 100
        return 0
