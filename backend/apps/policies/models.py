import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel
from apps.core.utils import generate_policy_number


class Policy(TenantModel, StatusModel):
    class PolicyStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        QUOTED = "quoted", "Quoted"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        RENEWED = "renewed", "Renewed"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partial"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        REFUNDED = "refunded", "Refunded"

    class PolicyType(models.TextChoices):
        NEW = "new", "New Business"
        RENEWAL = "renewal", "Renewal"
        ENDORSEMENT = "endorsement", "Endorsement"
        REINSTATEMENT = "reinstatement", "Reinstatement"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="policies",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="policies",
    )
    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    policy_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_policy_number)
    policy_type = models.CharField(max_length=20, choices=PolicyType.choices, default=PolicyType.NEW)
    policy_status = models.CharField(max_length=20, choices=PolicyStatus.choices, default=PolicyStatus.DRAFT, db_index=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()
    effective_date = models.DateField(null=True, blank=True)
    premium_amount = MoneyField(default=0)
    sum_insured = MoneyField(default=0)
    excess_amount = MoneyField(default=0)
    tax_amount = MoneyField(default=0)
    discount_amount = MoneyField(default=0)
    net_premium = MoneyField(default=0)
    total_paid = MoneyField(default=0)
    balance_due = MoneyField(default=0)
    currency = models.CharField(max_length=3, default="NGN")
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    broker = models.ForeignKey(
        "brokers.Broker",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    dealer = models.ForeignKey(
        "dealers.Dealer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )
    underwriter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwritten_policies",
    )
    previous_policy = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewed_policies",
    )
    auto_renew = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    cancellation_date = models.DateField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    coverage_details = models.JSONField(default=dict, blank=True)
    endorsement_count = models.PositiveIntegerField(default=0)
    claim_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Policy"
        verbose_name_plural = "Policies"
        indexes = [
            models.Index(fields=["tenant", "policy_status"]),
            models.Index(fields=["tenant", "payment_status"]),
            models.Index(fields=["customer", "policy_status"]),
            models.Index(fields=["product", "policy_status"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["policy_number"]),
            models.Index(fields=["agent", "policy_status"]),
            models.Index(fields=["broker", "policy_status"]),
        ]

    def __str__(self):
        return f"Policy {self.policy_number} - {self.customer.full_name}"

    @property
    def is_active(self):
        return self.policy_status == self.PolicyStatus.ACTIVE

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        delta = self.end_date - timezone.now().date()
        return max(0, delta.days)

    @property
    def coverage_amount(self):
        return self.sum_insured

    def approve(self, user):
        self.policy_status = self.PolicyStatus.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=["policy_status", "approved_by", "approved_at", "updated_at"])

    def activate(self):
        self.policy_status = self.PolicyStatus.ACTIVE
        self.effective_date = timezone.now().date()
        self.save(update_fields=["policy_status", "effective_date", "updated_at"])

    def suspend(self, reason=""):
        self.policy_status = self.PolicyStatus.SUSPENDED
        self.notes = reason
        self.save(update_fields=["policy_status", "notes", "updated_at"])


class PolicyEndorsement(TenantModel, StatusModel):
    class EndorsementType(models.TextChoices):
        ADD_COVERAGE = "add_coverage", "Add Coverage"
        REMOVE_COVERAGE = "remove_coverage", "Remove Coverage"
        MODIFY_COVERAGE = "modify_coverage", "Modify Coverage"
        CHANGE_DETAILS = "change_details", "Change Details"
        CORRECTION = "correction", "Correction"
        OTHER = "other", "Other"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.CASCADE,
        related_name="endorsements",
    )
    endorsement_number = models.CharField(max_length=50, unique=True, db_index=True)
    endorsement_type = models.CharField(max_length=20, choices=EndorsementType.choices)
    effective_date = models.DateField()
    description = models.TextField()
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON representation of all changes made by this endorsement.",
    )
    previous_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of values before endorsement.",
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of values after endorsement.",
    )
    premium_adjustment = MoneyField(default=0)
    sum_insured_adjustment = MoneyField(default=0)
    new_premium_amount = MoneyField(default=0)
    new_sum_insured = MoneyField(default=0)
    reason = models.TextField(blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-effective_date", "-created_at"]
        verbose_name = "Policy Endorsement"
        verbose_name_plural = "Policy Endorsements"
        indexes = [
            models.Index(fields=["policy", "effective_date"]),
            models.Index(fields=["endorsement_number"]),
        ]

    def __str__(self):
        return f"Endorsement {self.endorsement_number} for {self.policy.policy_number}"

    def approve(self, user):
        self.is_approved = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=["is_approved", "approved_by", "approved_at", "updated_at"])


class PolicyRenewal(TenantModel, StatusModel):
    class RenewalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        OFFER_SENT = "offer_sent", "Offer Sent"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.CASCADE,
        related_name="renewals",
    )
    new_policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewed_from",
    )
    renewal_number = models.CharField(max_length=50, unique=True, db_index=True)
    renewal_status = models.CharField(max_length=20, choices=RenewalStatus.choices, default=RenewalStatus.PENDING)
    renewal_date = models.DateField()
    renewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    previous_premium = MoneyField(default=0)
    new_premium = MoneyField(default=0)
    previous_sum_insured = MoneyField(default=0)
    new_sum_insured = MoneyField(default=0)
    premium_change_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    renewal_quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewals",
    )
    auto_renewed = models.BooleanField(default=False)
    offered_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-renewal_date"]
        verbose_name = "Policy Renewal"
        verbose_name_plural = "Policy Renewals"
        indexes = [
            models.Index(fields=["policy", "renewal_status"]),
            models.Index(fields=["renewal_date"]),
            models.Index(fields=["renewal_number"]),
        ]

    def __str__(self):
        return f"Renewal {self.renewal_number} for {self.policy.policy_number}"

    def accept_renewal(self, new_policy, user):
        self.renewal_status = self.RenewalStatus.ACCEPTED
        self.new_policy = new_policy
        self.renewed_by = user
        self.completed_at = timezone.now()
        self.save(update_fields=[
            "renewal_status", "new_policy", "renewed_by", "completed_at", "updated_at"
        ])


class PolicyCancellation(TenantModel, StatusModel):
    class CancellationReason(models.TextChoices):
        CUSTOMER_REQUEST = "customer_request", "Customer Request"
        NON_PAYMENT = "non_payment", "Non-Payment"
        FRAUD = "fraud", "Fraud"
        RISK = "risk", "Risk"
        DUPLICATE = "duplicate", "Duplicate"
        ERROR = "error", "Error"
        OTHER = "other", "Other"

    class RefundStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        PARTIAL = "partial", "Partial"
        DENIED = "denied", "Denied"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.CASCADE,
        related_name="cancellations",
    )
    cancellation_number = models.CharField(max_length=50, unique=True, db_index=True)
    cancellation_date = models.DateField()
    effective_date = models.DateField()
    reason = models.CharField(max_length=30, choices=CancellationReason.choices)
    reason_details = models.TextField(blank=True)
    refund_amount = MoneyField(default=0)
    refund_status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.PENDING,
    )
    refund_date = models.DateField(null=True, blank=True)
    refund_reference = models.CharField(max_length=100, blank=True)
    short_rate_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Short-rate percentage for pro-rata refund calculation.",
    )
    pro_rata_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Pro-rata percentage for refund calculation.",
    )
    cancellation_fee = MoneyField(default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_irrevocable = models.BooleanField(default=False)
    documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-cancellation_date"]
        verbose_name = "Policy Cancellation"
        verbose_name_plural = "Policy Cancellations"
        indexes = [
            models.Index(fields=["policy", "cancellation_date"]),
            models.Index(fields=["cancellation_number"]),
            models.Index(fields=["refund_status"]),
        ]

    def __str__(self):
        return f"Cancellation {self.cancellation_number} for {self.policy.policy_number}"

    def approve(self, user):
        self.is_approved = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=["is_approved", "approved_by", "approved_at", "updated_at"])


class PolicyDocument(TenantModel, StatusModel):
    class DocType(models.TextChoices):
        POLICY_SCHEDULE = "policy_schedule", "Policy Schedule"
        COVER_NOTE = "cover_note", "Cover Note"
        PROPOSAL_FORM = "proposal_form", "Proposal Form"
        CERTIFICATE = "certificate", "Certificate of Insurance"
        ENDORSEMENT = "endorsement", "Endorsement Document"
        RENEWAL_NOTICE = "renewal_notice", "Renewal Notice"
        CANCELLATION_LETTER = "cancellation_letter", "Cancellation Letter"
        RECEIPT = "receipt", "Receipt"
        INVOICE = "invoice", "Invoice"
        OTHER = "other", "Other"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=25, choices=DocType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="policy_documents/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=20, default="1.0")
    is_primary = models.BooleanField(default=False)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        ordering = ["-is_primary", "-created_at"]
        verbose_name = "Policy Document"
        verbose_name_plural = "Policy Documents"
        indexes = [
            models.Index(fields=["policy", "document_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.document_type}) - {self.policy.policy_number}"
