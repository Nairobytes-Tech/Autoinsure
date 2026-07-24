import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel
from apps.core.utils import generate_quote_number


class Quote(TenantModel, StatusModel):
    class QuoteStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        QUOTED = "quoted", "Quoted"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"
        CONVERTED = "converted", "Converted"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="quotes",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="quotes",
    )
    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    quote_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_quote_number)
    quote_status = models.CharField(max_length=20, choices=QuoteStatus.choices, default=QuoteStatus.DRAFT, db_index=True)
    valid_until = models.DateField()
    premium_amount = MoneyField(default=0)
    sum_insured = MoneyField(default=0)
    excess_amount = MoneyField(default=0)
    tax_amount = MoneyField(default=0)
    discount_amount = MoneyField(default=0)
    net_premium = MoneyField(default=0)
    currency = models.CharField(max_length=3, default="NGN")
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    broker = models.ForeignKey(
        "brokers.Broker",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    dealer = models.ForeignKey(
        "dealers.Dealer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    source = models.CharField(
        max_length=30,
        choices=[
            ("web", "Web Portal"),
            ("agent", "Agent"),
            ("broker", "Broker"),
            ("dealer", "Dealer"),
            ("api", "API"),
            ("manual", "Manual"),
        ],
        default="manual",
    )
    coverage_details = models.JSONField(default=dict, blank=True)
    risk_details = models.JSONField(default=dict, blank=True)
    rating_factors = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    declined_reason = models.TextField(blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    converted_policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="converted_from_quote",
    )
    version = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        indexes = [
            models.Index(fields=["tenant", "quote_status"]),
            models.Index(fields=["customer", "quote_status"]),
            models.Index(fields=["product", "quote_status"]),
            models.Index(fields=["valid_until"]),
            models.Index(fields=["quote_number"]),
        ]

    def __str__(self):
        return f"Quote {self.quote_number} - {self.customer.full_name}"

    @property
    def is_expired(self):
        return self.valid_until < timezone.now().date()

    @property
    def is_valid(self):
        return (
            not self.is_expired
            and self.quote_status in [self.QuoteStatus.QUOTED, self.QuoteStatus.SUBMITTED]
        )

    @property
    def items_total(self):
        from django.db.models import Sum
        result = self.items.aggregate(total=Sum("premium_amount"))
        return result["total"] or 0

    def decline(self, reason=""):
        self.quote_status = self.QuoteStatus.DECLINED
        self.declined_reason = reason
        self.declined_at = timezone.now()
        self.save(update_fields=["quote_status", "declined_reason", "declined_at", "updated_at"])

    def accept(self):
        self.quote_status = self.QuoteStatus.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=["quote_status", "accepted_at", "updated_at"])

    def convert_to_policy(self, policy):
        self.quote_status = self.QuoteStatus.CONVERTED
        self.converted_policy = policy
        self.converted_at = timezone.now()
        self.save(update_fields=["quote_status", "converted_policy", "converted_at", "updated_at"])


class QuoteItem(TenantModel, StatusModel):
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.CASCADE,
        related_name="items",
    )
    coverage_name = models.CharField(max_length=255)
    coverage_code = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    sum_insured = MoneyField(default=0)
    premium_amount = MoneyField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    rate_type = models.CharField(
        max_length=20,
        choices=[
            ("percentage", "Percentage"),
            ("flat", "Flat Rate"),
            ("per_unit", "Per Unit"),
        ],
        default="percentage",
    )
    quantity = models.PositiveIntegerField(default=1)
    is_included = models.BooleanField(default=True)
    is_optional = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    excess_amount = MoneyField(default=0)
    sub_items = models.JSONField(default=list, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    conditions = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_order", "coverage_name"]
        verbose_name = "Quote Item"
        verbose_name_plural = "Quote Items"
        indexes = [
            models.Index(fields=["quote", "is_included"]),
        ]

    def __str__(self):
        return f"{self.coverage_name} - {self.quote.quote_number}"

    @property
    def total_premium(self):
        return self.premium_amount * self.quantity


class QuoteVersion(TenantModel):
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    premium_amount = MoneyField(default=0)
    sum_insured = MoneyField(default=0)
    tax_amount = MoneyField(default=0)
    discount_amount = MoneyField(default=0)
    net_premium = MoneyField(default=0)
    coverage_details = models.JSONField(default=dict, blank=True)
    rating_factors = models.JSONField(default=dict, blank=True)
    items_snapshot = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    change_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-version_number"]
        verbose_name = "Quote Version"
        verbose_name_plural = "Quote Versions"
        constraints = [
            models.UniqueConstraint(
                fields=["quote", "version_number"],
                name="unique_quote_version",
            ),
        ]
        indexes = [
            models.Index(fields=["quote", "version_number"]),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} v{self.version_number}"
