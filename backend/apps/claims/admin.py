from django.contrib import admin
from apps.claims.models import (
    Claim, ClaimActivity, ClaimDocument, ClaimAssessment, ClaimPayment, ClaimInvestigation,
)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ["claim_number", "claim_status", "claim_type", "priority", "policy", "customer", "claim_amount", "incident_date"]
    list_filter = ["claim_status", "claim_type", "priority", "third_party_involved", "fraud_flag"]
    search_fields = ["claim_number", "policy__policy_number", "customer__first_name", "customer__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ClaimActivity)
class ClaimActivityAdmin(admin.ModelAdmin):
    list_display = ["claim", "action_type", "description", "performed_by", "created_at"]
    list_filter = ["action_type"]
    search_fields = ["claim__claim_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "claim", "is_verified", "created_at"]
    list_filter = ["document_type", "is_verified"]
    search_fields = ["title", "claim__claim_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ClaimAssessment)
class ClaimAssessmentAdmin(admin.ModelAdmin):
    list_display = ["assessment_type", "claim", "assessment_date", "assessed_amount", "is_accepted"]
    list_filter = ["assessment_type", "is_accepted"]
    search_fields = ["claim__claim_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ClaimPayment)
class ClaimPaymentAdmin(admin.ModelAdmin):
    list_display = ["claim", "payment_type", "payment_method", "amount", "payment_date", "payee_name"]
    list_filter = ["payment_type", "payment_method"]
    search_fields = ["transaction_reference", "payee_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ClaimInvestigation)
class ClaimInvestigationAdmin(admin.ModelAdmin):
    list_display = ["case_reference", "claim", "investigation_type", "investigation_status", "opened_date"]
    list_filter = ["investigation_type", "investigation_status"]
    search_fields = ["case_reference"]
    readonly_fields = ["id", "created_at", "updated_at"]
