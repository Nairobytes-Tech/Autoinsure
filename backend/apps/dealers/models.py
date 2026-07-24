from django.conf import settings
from django.db import models

from apps.core.models import MoneyField, PhoneNumberField, StatusModel, TenantModel


class Dealer(TenantModel, StatusModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="dealer_profiles",
    )
    dealer_code = models.CharField(max_length=30, unique=True, db_index=True)
    company_name = models.CharField(max_length=255, db_index=True)
    trading_name = models.CharField(max_length=255, blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = PhoneNumberField()
    alternative_phone = PhoneNumberField()
    website = models.URLField(blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    dealer_type = models.CharField(
        max_length=30,
        choices=[
            ("new_car", "New Car Dealer"),
            ("used_car", "Used Car Dealer"),
            ("both", "New & Used Car Dealer"),
            ("commercial", "Commercial Vehicle Dealer"),
            ("motorcycle", "Motorcycle Dealer"),
        ],
        default="new_car",
    )
    showroom_address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dealers",
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_policies_sold = models.PositiveIntegerField(default=0)
    total_premium_generated = MoneyField(default=0)
    total_commission_earned = MoneyField(default=0)
    total_commission_paid = MoneyField(default=0)
    total_vehicles_insured = models.PositiveIntegerField(default=0)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    bank_sort_code = models.CharField(max_length=20, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    authorized_brands = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Dealer"
        verbose_name_plural = "Dealers"
        indexes = [
            models.Index(fields=["tenant", "dealer_code"]),
            models.Index(fields=["tenant", "company_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.company_name} ({self.dealer_code})"
