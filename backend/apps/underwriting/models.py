from django.conf import settings
from django.db import models

from apps.core.models import MoneyField, StatusModel, TenantModel


class UnderwritingRule(TenantModel, StatusModel):
    class RuleType(models.TextChoices):
        ELIGIBILITY = "eligibility", "Eligibility Rule"
        RATING = "rating", "Rating Rule"
        REFERRAL = "referral", "Referral Rule"
        REJECTION = "rejection", "Rejection Rule"
        DOCUMENT = "document", "Document Requirement"

    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RuleType.choices, db_index=True)
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_rules",
    )
    product_category = models.ForeignKey(
        "products.ProductCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_rules",
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON conditions: {field, operator, value, logic}",
    )
    actions = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON actions: {type, value, message}",
    )
    priority = models.PositiveIntegerField(default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_automated = models.BooleanField(default=True)
    requires_manual_review = models.BooleanField(default=False)
    max_sum_insured = MoneyField(null=True, blank=True)
    min_sum_insured = MoneyField(null=True, blank=True)
    max_premium = MoneyField(null=True, blank=True)
    min_premium = MoneyField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    warning_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority", "name"]
        verbose_name = "Underwriting Rule"
        verbose_name_plural = "Underwriting Rules"
        indexes = [
            models.Index(fields=["tenant", "rule_type", "is_active"]),
            models.Index(fields=["product", "rule_type"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class UnderwritingDecision(TenantModel, StatusModel):
    class DecisionType(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        REFERRED = "referred", "Referred"
        DECLINED = "declined", "Declined"
        REFERRED_TO_UNDERWRITER = "referred_to_underwriter", "Referred to Underwriter"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low Risk"
        MEDIUM = "medium", "Medium Risk"
        HIGH = "high", "High Risk"
        VERY_HIGH = "very_high", "Very High Risk"

    policy = models.ForeignKey(
        "policies.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_decisions",
    )
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_decisions",
    )
    decision_type = models.CharField(max_length=30, choices=DecisionType.choices, db_index=True)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.MEDIUM)
    underwriter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_decisions",
    )
    decision_date = models.DateField(auto_now_add=True)
    risk_assessment = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured risk assessment data",
    )
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    premium_loading = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    excess_loading = MoneyField(default=0)
    conditions_applied = models.JSONField(default=list, blank=True)
    exclusions_applied = models.JSONField(default=list, blank=True)
    referral_reason = models.TextField(blank=True)
    declined_reason = models.TextField(blank=True)
    documents_reviewed = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-decision_date", "-created_at"]
        verbose_name = "Underwriting Decision"
        verbose_name_plural = "Underwriting Decisions"
        indexes = [
            models.Index(fields=["tenant", "decision_type"]),
            models.Index(fields=["policy", "decision_type"]),
            models.Index(fields=["quote", "decision_type"]),
            models.Index(fields=["underwriter", "decision_type"]),
            models.Index(fields=["risk_level"]),
        ]

    def __str__(self):
        ref = self.policy.policy_number if self.policy else (self.quote.quote_number if self.quote else "N/A")
        return f"{self.decision_type} - {ref}"


class ReferralQueue(TenantModel, StatusModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    decision = models.ForeignKey(
        UnderwritingDecision,
        on_delete=models.CASCADE,
        related_name="referral_queue_entries",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="underwriting_referrals",
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    referral_reason = models.TextField()
    escalated = models.BooleanField(default=False)
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-priority", "created_at"]
        verbose_name = "Referral Queue"
        verbose_name_plural = "Referral Queues"
        indexes = [
            models.Index(fields=["tenant", "priority", "status"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return f"Referral for {self.decision}"
