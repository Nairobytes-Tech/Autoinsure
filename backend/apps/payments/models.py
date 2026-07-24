import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel
from apps.core.utils import (
    generate_invoice_number,
    generate_payment_reference,
    generate_receipt_number,
)


class PaymentMethod(TenantModel, StatusModel):
    class MethodType(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CARD = "card", "Card Payment"
        CASH = "cash", "Cash"
        CHEQUE = "cheque", "Cheque"
        MOBILE_MONEY = "mobile_money", "Mobile Money"
        USSD = "ussd", "USSD"
        ONLINE = "online", "Online Payment"
        DIRECT_DEBIT = "direct_debit", "Direct Debit"
        STANDING_ORDER = "standing_order", "Standing Order"

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    method_type = models.CharField(max_length=20, choices=MethodType.choices)
    description = models.TextField(blank=True)
    gateway_provider = models.CharField(max_length=100, blank=True)
    gateway_config = models.JSONField(default=dict, blank=True)
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    processing_fee_fixed = MoneyField(default=0)
    min_amount = MoneyField(default=0)
    max_amount = MoneyField(default=0)
    is_online = models.BooleanField(default=False)
    requires_verification = models.BooleanField(default=False)
    settlement_days = models.PositiveIntegerField(default=0)
    display_order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=100, blank=True)
    instructions = models.TextField(blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Payment(TenantModel, StatusModel):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
        VERIFIED = "verified", "Verified"

    class PaymentFor(models.TextChoices):
        POLICY = "policy", "Policy Premium"
        CLAIM = "claim", "Claim Settlement"
        COMMISSION = "commission", "Commission"
        FEE = "fee", "Fee"
        OTHER = "other", "Other"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    invoice = models.ForeignKey(
        "payments.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    reference_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_payment_reference)
    payment_for = models.CharField(max_length=20, choices=PaymentFor.choices, default=PaymentFor.POLICY, db_index=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)
    amount = MoneyField()
    paid_amount = MoneyField(default=0)
    currency = models.CharField(max_length=3, default="NGN")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1)
    payment_method = models.ForeignKey(
        "payments.PaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    gateway_reference = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    payer_name = models.CharField(max_length=255, blank=True)
    payer_email = models.EmailField(blank=True)
    payer_phone = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    confirmed_date = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    is_confirmed = models.BooleanField(default=False)
    allocated_amount = MoneyField(default=0)
    unallocated_amount = MoneyField(default=0)
    allocation_details = models.JSONField(default=list, blank=True)
    reversal_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversals",
    )
    is_reversal = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["tenant", "payment_status"]),
            models.Index(fields=["tenant", "payment_for"]),
            models.Index(fields=["policy", "payment_status"]),
            models.Index(fields=["claim", "payment_status"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["reference_number"]),
        ]

    def __str__(self):
        return f"Payment {self.reference_number} - {self.amount}"

    @property
    def outstanding_amount(self):
        return self.amount - self.paid_amount

    @property
    def is_fully_paid(self):
        return self.paid_amount >= self.amount

    def confirm(self, user, amount=None):
        if amount is not None:
            self.paid_amount = amount
        self.payment_status = self.PaymentStatus.COMPLETED
        self.is_confirmed = True
        self.confirmed_date = timezone.now()
        self.confirmed_by = user
        self.save(update_fields=[
            "paid_amount", "payment_status", "is_confirmed",
            "confirmed_date", "confirmed_by", "updated_at",
        ])


class Invoice(TenantModel, StatusModel):
    class InvoiceStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"
        WRITTEN_OFF = "written_off", "Written Off"

    class InvoiceType(models.TextChoices):
        PREMIUM = "premium", "Premium Invoice"
        TOP_UP = "top_up", "Top-Up Invoice"
        RENEWAL = "renewal", "Renewal Invoice"
        ENDORSEMENT = "endorsement", "Endorsement Invoice"
        FEE = "fee", "Fee Invoice"
        OTHER = "other", "Other"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_invoice_number)
    invoice_type = models.CharField(max_length=20, choices=InvoiceType.choices, default=InvoiceType.PREMIUM)
    invoice_status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT, db_index=True)
    amount = MoneyField()
    tax_amount = MoneyField(default=0)
    discount_amount = MoneyField(default=0)
    total_amount = MoneyField(default=0)
    paid_amount = MoneyField(default=0)
    outstanding_amount = MoneyField(default=0)
    currency = models.CharField(max_length=3, default="NGN")
    due_date = models.DateField()
    issued_date = models.DateField(default=timezone.now)
    paid_date = models.DateField(null=True, blank=True)
    line_items = models.JSONField(default=list, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    last_reminder_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["-issued_date"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=["tenant", "invoice_status"]),
            models.Index(fields=["customer", "invoice_status"]),
            models.Index(fields=["policy", "invoice_status"]),
            models.Index(fields=["due_date", "invoice_status"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.total_amount}"

    @property
    def is_overdue(self):
        return (
            self.invoice_status not in [self.InvoiceStatus.PAID, self.InvoiceStatus.CANCELLED]
            and self.due_date < timezone.now().date()
        )

    @property
    def days_overdue(self):
        if self.is_overdue:
            delta = timezone.now().date() - self.due_date
            return delta.days
        return 0

    @property
    def payment_percentage(self):
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0

    def mark_paid(self):
        self.invoice_status = self.InvoiceStatus.PAID
        self.paid_date = timezone.now().date()
        self.outstanding_amount = 0
        self.save(update_fields=[
            "invoice_status", "paid_date", "outstanding_amount", "updated_at"
        ])


class Receipt(TenantModel, StatusModel):
    class ReceiptStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        SENT = "sent", "Sent"
        CANCELLED = "cancelled", "Cancelled"

    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.CASCADE,
        related_name="receipts",
    )
    invoice = models.ForeignKey(
        "payments.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
    )
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_receipt_number)
    receipt_status = models.CharField(max_length=20, choices=ReceiptStatus.choices, default=ReceiptStatus.DRAFT)
    amount = MoneyField()
    currency = models.CharField(max_length=3, default="NGN")
    receipt_date = models.DateField(default=timezone.now)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    receipt_for = models.CharField(max_length=100, blank=True)
    payment_description = models.TextField(blank=True)
    signature = models.ImageField(upload_to="receipt_signatures/", blank=True, null=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-receipt_date"]
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        indexes = [
            models.Index(fields=["tenant", "receipt_status"]),
            models.Index(fields=["payment", "receipt_status"]),
            models.Index(fields=["receipt_number"]),
        ]

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.amount}"

    def issue(self, user):
        self.receipt_status = self.ReceiptStatus.ISSUED
        self.issued_by = user
        self.issued_at = timezone.now()
        self.save(update_fields=["receipt_status", "issued_by", "issued_at", "updated_at"])

    def send(self):
        self.receipt_status = self.ReceiptStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["receipt_status", "sent_at", "updated_at"])
