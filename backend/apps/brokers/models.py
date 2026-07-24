from django.conf import settings
from django.db import models

from apps.core.models import MoneyField, PhoneNumberField, StatusModel, TenantModel


class Broker(TenantModel, StatusModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="broker_profiles",
    )
    broker_code = models.CharField(max_length=30, unique=True, db_index=True)
    company_name = models.CharField(max_length=255, db_index=True)
    trading_name = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = PhoneNumberField()
    alternative_phone = PhoneNumberField()
    website = models.URLField(blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    license_type = models.CharField(
        max_length=30,
        choices=[
            ("broker", "Insurance Broker"),
            ("sub_broker", "Sub-Broker"),
            ("corporate", "Corporate Agent"),
        ],
        default="broker",
    )
    license_expiry = models.DateField(null=True, blank=True)
    regulatory_body = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="brokers",
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_premium_placed = MoneyField(default=0)
    total_commission_earned = MoneyField(default=0)
    total_commission_paid = MoneyField(default=0)
    total_policies_sold = models.PositiveIntegerField(default=0)
    total_claims_generated = models.PositiveIntegerField(default=0)
    credit_limit = MoneyField(default=0)
    credit_balance = MoneyField(default=0)
    settlement_terms_days = models.PositiveIntegerField(default=30)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    bank_sort_code = models.CharField(max_length=20, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Broker"
        verbose_name_plural = "Brokers"
        indexes = [
            models.Index(fields=["tenant", "broker_code"]),
            models.Index(fields=["tenant", "company_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.company_name} ({self.broker_code})"

    @property
    def outstanding_balance(self):
        return self.credit_limit - self.credit_balance
