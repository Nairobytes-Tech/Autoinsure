import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel
from apps.core.utils import generate_claim_number


class Claim(TenantModel, StatusModel):
    class ClaimStatus(models.TextChoices):
        NEW = "new", "New"
        UNDER_INVESTIGATION = "under_investigation", "Under Investigation"
        ASSESSED = "assessed", "Assessed"
        APPROVED = "approved", "Approved"
        PARTIALLY_APPROVED = "partially_approved", "Partially Approved"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        CLOSED = "closed", "Closed"
        REOPENED = "reopened", "Reopened"

    class ClaimType(models.TextChoices):
        ACCIDENT = "accident", "Accident"
        THEFT = "theft", "Theft"
        FIRE = "fire", "Fire"
        NATURAL_DISASTER = "natural_disaster", "Natural Disaster"
        VANDALISM = "vandalism", "Vandalism"
        MEDICAL = "medical", "Medical"
        HOSPITALIZATION = "hospitalization", "Hospitalization"
        DEATH = "death", "Death"
        DISABILITY = "disability", "Disability"
        PROPERTY_DAMAGE = "property_damage", "Property Damage"
        THIRD_PARTY = "third_party", "Third Party"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.PROTECT,
        related_name="claims",
    )
    claim_number = models.CharField(max_length=50, unique=True, db_index=True, default=generate_claim_number)
    claim_status = models.CharField(max_length=25, choices=ClaimStatus.choices, default=ClaimStatus.NEW, db_index=True)
    claim_type = models.CharField(max_length=25, choices=ClaimType.choices, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    incident_date = models.DateField()
    reported_date = models.DateTimeField(default=timezone.now)
    claim_amount = MoneyField(default=0)
    approved_amount = MoneyField(default=0)
    paid_amount = MoneyField(default=0)
    reserved_amount = MoneyField(default=0)
    deductible_amount = MoneyField(default=0)
    excess_amount = MoneyField(default=0)
    currency = models.CharField(max_length=3, default="NGN")
    incident_description = models.TextField()
    incident_location = models.CharField(max_length=500, blank=True)
    incident_reference = models.CharField(max_length=100, blank=True)
    police_report_number = models.CharField(max_length=100, blank=True)
    police_station = models.CharField(max_length=255, blank=True)
    third_party_involved = models.BooleanField(default=False)
    third_party_details = models.JSONField(default=dict, blank=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="claims",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_claims",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    investigation_required = models.BooleanField(default=False)
    fraud_flag = models.BooleanField(default=False)
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-reported_date"]
        verbose_name = "Claim"
        verbose_name_plural = "Claims"
        indexes = [
            models.Index(fields=["tenant", "claim_status"]),
            models.Index(fields=["tenant", "claim_type"]),
            models.Index(fields=["policy", "claim_status"]),
            models.Index(fields=["customer", "claim_status"]),
            models.Index(fields=["assigned_to", "claim_status"]),
            models.Index(fields=["incident_date"]),
            models.Index(fields=["claim_number"]),
            models.Index(fields=["fraud_flag", "claim_status"]),
        ]

    def __str__(self):
        return f"Claim {self.claim_number} - {self.policy.policy_number}"

    @property
    def outstanding_amount(self):
        return self.claim_amount - self.paid_amount

    @property
    def approval_percentage(self):
        if self.claim_amount > 0:
            return (self.approved_amount / self.claim_amount) * 100
        return 0

    @property
    def is_settled(self):
        return self.claim_status in [
            self.ClaimStatus.PAID,
            self.ClaimStatus.CLOSED,
        ]

    def assign(self, user, assigned_by=None):
        self.assigned_to = user
        self.assigned_by = assigned_by
        self.assigned_at = timezone.now()
        self.claim_status = self.ClaimStatus.UNDER_INVESTIGATION
        self.save(update_fields=[
            "assigned_to", "assigned_by", "assigned_at", "claim_status", "updated_at"
        ])

    def approve(self, amount, user):
        self.approved_amount = amount
        self.claim_status = self.ClaimStatus.APPROVED
        self.save(update_fields=["approved_amount", "claim_status", "updated_at"])

    def reject(self, reason, user):
        self.rejection_reason = reason
        self.claim_status = self.ClaimStatus.REJECTED
        self.save(update_fields=["rejection_reason", "claim_status", "updated_at"])

    def close(self, user):
        self.claim_status = self.ClaimStatus.CLOSED
        self.closed_at = timezone.now()
        self.closed_by = user
        self.save(update_fields=["claim_status", "closed_at", "closed_by", "updated_at"])


class ClaimActivity(TenantModel):
    class ActionType(models.TextChoices):
        CREATED = "created", "Created"
        ASSIGNED = "assigned", "Assigned"
        STATUS_CHANGED = "status_changed", "Status Changed"
        DOCUMENT_UPLOADED = "document_uploaded", "Document Uploaded"
        NOTE_ADDED = "note_added", "Note Added"
        ASSESSMENT_COMPLETED = "assessment_completed", "Assessment Completed"
        INVESTIGATION_STARTED = "investigation_started", "Investigation Started"
        INVESTIGATION_COMPLETED = "investigation_completed", "Investigation Completed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"
        CLOSED = "closed", "Closed"
        REOPENED = "reopened", "Reopened"
        ESCALATED = "escalated", "Escalated"
        OTHER = "other", "Other"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="activities",
    )
    action_type = models.CharField(max_length=30, choices=ActionType.choices, db_index=True)
    description = models.TextField()
    old_value = models.CharField(max_length=500, blank=True)
    new_value = models.CharField(max_length=500, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    metadata = models.JSONField(default=dict, blank=True)
    attachment = models.FileField(upload_to="claim_activities/%Y/%m/%d/", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Claim Activity"
        verbose_name_plural = "Claim Activities"
        indexes = [
            models.Index(fields=["claim", "action_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.action_type} - Claim {self.claim.claim_number}"


class ClaimDocument(TenantModel, StatusModel):
    class DocType(models.TextChoices):
        CLAIM_FORM = "claim_form", "Claim Form"
        POLICE_REPORT = "police_report", "Police Report"
        MEDICAL_REPORT = "medical_report", "Medical Report"
        PHOTO_EVIDENCE = "photo_evidence", "Photo Evidence"
        INVOICE = "invoice", "Invoice/Receipt"
        ESTIMATE = "estimate", "Repair Estimate"
        SURVEY_REPORT = "survey_report", "Survey Report"
        WITNESS_STATEMENT = "Witness Statement", "Witness Statement"
        COURT_DOCUMENT = "court_document", "Court Document"
        OTHER = "other", "Other"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=25, choices=DocType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="claim_documents/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Claim Document"
        verbose_name_plural = "Claim Documents"
        indexes = [
            models.Index(fields=["claim", "document_type"]),
        ]

    def __str__(self):
        return f"{self.title} - Claim {self.claim.claim_number}"


class ClaimAssessment(TenantModel, StatusModel):
    class AssessmentType(models.TextChoices):
        INITIAL = "initial", "Initial Assessment"
        SURVEY = "survey", "Survey"
        REPAIR_ESTIMATE = "repair_estimate", "Repair Estimate"
        MEDICAL = "medical", "Medical Assessment"
        FINAL = "final", "Final Assessment"
        REASSESSMENT = "reassessment", "Reassessment"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    assessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claim_assessments",
    )
    assessment_date = models.DateField()
    findings = models.TextField()
    recommended_amount = MoneyField(default=0)
    assessed_amount = MoneyField(default=0)
    depreciation_amount = MoneyField(default=0)
    salvage_value = MoneyField(default=0)
    repair_replacement = models.CharField(
        max_length=20,
        choices=[
            ("repair", "Repair"),
            ("replace", "Replace"),
            ("total_loss", "Total Loss"),
            ("partial", "Partial"),
        ],
        blank=True,
    )
    condition_notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    photographs = models.JSONField(default=list, blank=True)
    measurements = models.JSONField(default=dict, blank=True)
    is_accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    report_file = models.FileField(upload_to="claim_assessments/%Y/%m/%d/", blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-assessment_date"]
        verbose_name = "Claim Assessment"
        verbose_name_plural = "Claim Assessments"
        indexes = [
            models.Index(fields=["claim", "assessment_type"]),
            models.Index(fields=["assessment_date"]),
        ]

    def __str__(self):
        return f"{self.assessment_type} - Claim {self.claim.claim_number}"


class ClaimPayment(TenantModel, StatusModel):
    class PaymentType(models.TextChoices):
        SETTLEMENT = "settlement", "Settlement"
        PARTIAL = "partial", "Partial Payment"
        ADVANCE = "advance", "Advance Payment"
        EXGRATIA = "ex_gratia", "Ex-Gratia"
        THIRD_PARTY = "third_party", "Third Party Recovery"
        OTHER = "other", "Other"

    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CHEQUE = "cheque", "Cheque"
        CASH = "cash", "Cash"
        MOBILE_MONEY = "mobile_money", "Mobile Money"
        ONLINE = "online", "Online Payment"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount = MoneyField()
    payment_date = models.DateField()
    transaction_reference = models.CharField(max_length=100, blank=True, db_index=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=255, blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    payee_name = models.CharField(max_length=255)
    payee_address = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
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
    receipt_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Claim Payment"
        verbose_name_plural = "Claim Payments"
        indexes = [
            models.Index(fields=["claim", "payment_type"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["transaction_reference"]),
        ]

    def __str__(self):
        return f"Payment {self.amount} for Claim {self.claim.claim_number}"


class ClaimInvestigation(TenantModel, StatusModel):
    class InvestigationType(models.TextChoices):
        FRAUD = "fraud", "Fraud Investigation"
        LIABILITY = "liability", "Liability Investigation"
        SUBROGATION = "subrogation", "Subrogation"
        GENERAL = "general", "General Investigation"

    class InvestigationStatus(models.TextChoices):
        OPENED = "opened", "Opened"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"

    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="investigations",
    )
    investigation_type = models.CharField(max_length=20, choices=InvestigationType.choices)
    investigation_status = models.CharField(max_length=20, choices=InvestigationStatus.choices, default=InvestigationStatus.OPENED)
    case_reference = models.CharField(max_length=100, unique=True, db_index=True)
    investigator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claim_investigations",
    )
    external_agency = models.CharField(max_length=255, blank=True)
    opened_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    evidence_collected = models.JSONField(default=list, blank=True)
    witnesses_interviewed = models.JSONField(default=list, blank=True)
    estimated_fraud_amount = MoneyField(null=True, blank=True)
    is_fraud_confirmed = models.BooleanField(default=False)
    legal_action_required = models.BooleanField(default=False)
    legal_action_taken = models.BooleanField(default=False)
    report_file = models.FileField(upload_to="claim_investigations/%Y/%m/%d/", blank=True, null=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-opened_date"]
        verbose_name = "Claim Investigation"
        verbose_name_plural = "Claim Investigations"
        indexes = [
            models.Index(fields=["claim", "investigation_type"]),
            models.Index(fields=["investigation_status"]),
            models.Index(fields=["case_reference"]),
        ]

    def __str__(self):
        return f"Investigation {self.case_reference} - Claim {self.claim.claim_number}"

    def complete(self, findings, conclusion, recommendation=""):
        self.investigation_status = self.InvestigationStatus.COMPLETED
        self.findings = findings
        self.conclusion = conclusion
        self.recommendation = recommendation
        self.completed_date = timezone.now().date()
        self.save(update_fields=[
            "investigation_status", "findings", "conclusion",
            "recommendation", "completed_date", "updated_at",
        ])
