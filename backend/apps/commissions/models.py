from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel


class CommissionStructure(TenantModel, StatusModel):
    class ChannelType(models.TextChoices):
        AGENT = "agent", "Agent"
        BROKER = "broker", "Broker"
        DEALER = "dealer", "Dealer"
        DIRECT = "direct", "Direct"
        ONLINE = "online", "Online"
        PARTNERSHIP = "partnership", "Partnership"

    class CalculationType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FLAT = "flat", "Flat Amount"
        TIERED = "tiered", "Tiered"
        SLIDING = "sliding", "Sliding Scale"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.TextField(blank=True)
    channel_type = models.CharField(max_length=20, choices=ChannelType.choices, db_index=True)
    calculation_type = models.CharField(max_length=20, choices=CalculationType.choices)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commission_structures",
    )
    product_category = models.ForeignKey(
        "products.ProductCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commission_structures",
    )
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    flat_amount = MoneyField(default=0)
    tier_config = models.JSONField(
        default=list,
        blank=True,
        help_text="Tiered commission rules: [{min, max, rate}]",
    )
    sliding_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Sliding scale commission rules.",
    )
    base_commission = MoneyField(default=0)
    bonus_commission = MoneyField(default=0)
    max_commission = MoneyField(default=0)
    min_commission = MoneyField(default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_renewal_applicable = models.BooleanField(default=True)
    renewal_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payout_frequency = models.CharField(
        max_length=20,
        choices=[
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("bi_annual", "Bi-Annual"),
            ("annual", "Annual"),
            ("on_payment", "On Payment"),
        ],
        default="monthly",
    )
    requires_approval = models.BooleanField(default=False)
    approval_threshold = MoneyField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["channel_type", "name"]
        verbose_name = "Commission Structure"
        verbose_name_plural = "Commission Structures"
        indexes = [
            models.Index(fields=["tenant", "channel_type", "is_active"]),
            models.Index(fields=["product", "channel_type"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.channel_type})"

    def calculate_commission(self, premium_amount, is_renewal=False):
        if self.calculation_type == self.CalculationType.PERCENTAGE:
            rate = self.renewal_rate_percentage if is_renewal and self.is_renewal_applicable else self.rate_percentage
            commission = premium_amount * (rate / 100)
        elif self.calculation_type == self.CalculationType.FLAT:
            commission = self.flat_amount
        elif self.calculation_type == self.CalculationType.TIERED:
            commission = self._calculate_tiered(premium_amount)
        else:
            commission = premium_amount * (self.rate_percentage / 100)

        if self.max_commission > 0:
            commission = min(commission, self.max_commission)
        if self.min_commission > 0:
            commission = max(commission, self.min_commission)

        return commission

    def _calculate_tiered(self, premium_amount):
        total = MoneyField()(0)
        for tier in self.tier_config:
            tier_min = MoneyField()(tier.get("min", 0))
            tier_max = MoneyField()(tier.get("max", 0))
            tier_rate = models.DecimalField(max_digits=5, decimal_places=2)(tier.get("rate", 0))
            if premium_amount >= tier_min:
                applicable = min(premium_amount, tier_max) - tier_min if tier_max > 0 else premium_amount - tier_min
                total += applicable * (tier_rate / 100)
        return total


class Commission(TenantModel, StatusModel):
    class CommissionStatus(models.TextChoices):
        CALCULATED = "calculated", "Calculated"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        CANCELLED = "cancelled", "Cancelled"

    class EarnedBy(models.TextChoices):
        AGENT = "agent", "Agent"
        BROKER = "broker", "Broker"
        DEALER = "dealer", "Dealer"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.CASCADE,
        related_name="commissions",
    )
    structure = models.ForeignKey(
        "commissions.CommissionStructure",
        on_delete=models.PROTECT,
        related_name="commissions",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commissions",
    )
    broker = models.ForeignKey(
        "brokers.Broker",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commissions",
    )
    dealer = models.ForeignKey(
        "dealers.Dealer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commissions",
    )
    earned_by_type = models.CharField(max_length=10, choices=EarnedBy.choices)
    commission_status = models.CharField(max_length=20, choices=CommissionStatus.choices, default=CommissionStatus.CALCULATED, db_index=True)
    premium_amount = MoneyField()
    commission_rate = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    commission_amount = MoneyField()
    bonus_amount = MoneyField(default=0)
    total_amount = MoneyField(default=0)
    paid_amount = MoneyField(default=0)
    outstanding_amount = MoneyField(default=0)
    calculation_date = models.DateField(default=timezone.now)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    is_renewal = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-calculation_date"]
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"
        indexes = [
            models.Index(fields=["tenant", "commission_status"]),
            models.Index(fields=["agent", "commission_status"]),
            models.Index(fields=["broker", "commission_status"]),
            models.Index(fields=["dealer", "commission_status"]),
            models.Index(fields=["policy", "commission_status"]),
            models.Index(fields=["calculation_date"]),
        ]

    def __str__(self):
        return f"Commission {self.total_amount} - {self.earned_by_type}"

    @property
    def is_fully_paid(self):
        return self.paid_amount >= self.total_amount

    def approve(self, user):
        self.commission_status = self.CommissionStatus.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=[
            "commission_status", "approved_by", "approved_at", "updated_at"
        ])

    def reject(self, reason, user):
        self.commission_status = self.CommissionStatus.REJECTED
        self.rejection_reason = reason
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=[
            "commission_status", "rejection_reason", "approved_by", "approved_at", "updated_at"
        ])


class CommissionPayment(TenantModel, StatusModel):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commission_payments",
    )
    broker = models.ForeignKey(
        "brokers.Broker",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commission_payments",
    )
    dealer = models.ForeignKey(
        "dealers.Dealer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commission_payments",
    )
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)
    amount = MoneyField()
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("bank_transfer", "Bank Transfer"),
            ("cheque", "Cheque"),
            ("cash", "Cash"),
            ("mobile_money", "Mobile Money"),
        ],
        default="bank_transfer",
    )
    payment_date = models.DateField()
    transaction_reference = models.CharField(max_length=100, blank=True, db_index=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    commission_count = models.PositiveIntegerField(default=0)
    commissions = models.ManyToManyField(
        "commissions.Commission",
        related_name="payments",
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Commission Payment"
        verbose_name_plural = "Commission Payments"
        indexes = [
            models.Index(fields=["tenant", "payment_status"]),
            models.Index(fields=["agent", "payment_status"]),
            models.Index(fields=["broker", "payment_status"]),
            models.Index(fields=["dealer", "payment_status"]),
            models.Index(fields=["payment_date"]),
        ]

    def __str__(self):
        return f"Commission Payment {self.amount} - {self.payment_date}"

    def process(self, user):
        self.payment_status = self.PaymentStatus.COMPLETED
        self.processed_by = user
        self.processed_at = timezone.now()
        self.save(update_fields=[
            "payment_status", "processed_by", "processed_at", "updated_at"
        ])
