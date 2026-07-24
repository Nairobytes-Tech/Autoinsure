from django.contrib import admin
from apps.underwriting.models import UnderwritingRule, UnderwritingDecision, ReferralQueue


@admin.register(UnderwritingRule)
class UnderwritingRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "rule_type", "product", "priority", "is_automated", "effective_from", "status"]
    list_filter = ["rule_type", "is_automated", "requires_manual_review", "status"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(UnderwritingDecision)
class UnderwritingDecisionAdmin(admin.ModelAdmin):
    list_display = ["decision_type", "risk_level", "risk_score", "policy", "quote", "underwriter", "decision_date"]
    list_filter = ["decision_type", "risk_level"]
    search_fields = ["policy__policy_number", "quote__quote_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ReferralQueue)
class ReferralQueueAdmin(admin.ModelAdmin):
    list_display = ["decision", "assigned_to", "priority", "escalated", "resolved_at"]
    list_filter = ["priority", "escalated"]
    search_fields = ["decision__policy__policy_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
