from django.contrib import admin
from apps.policies.models import Policy, PolicyEndorsement, PolicyRenewal, PolicyCancellation, PolicyDocument


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ["policy_number", "customer", "product", "policy_status", "payment_status", "premium_amount", "start_date", "end_date"]
    list_filter = ["policy_status", "payment_status", "policy_type", "product"]
    search_fields = ["policy_number", "customer__first_name", "customer__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PolicyEndorsement)
class PolicyEndorsementAdmin(admin.ModelAdmin):
    list_display = ["endorsement_number", "policy", "endorsement_type", "effective_date", "is_approved"]
    list_filter = ["endorsement_type", "is_approved"]
    search_fields = ["endorsement_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PolicyRenewal)
class PolicyRenewalAdmin(admin.ModelAdmin):
    list_display = ["renewal_number", "policy", "renewal_status", "renewal_date", "new_premium"]
    list_filter = ["renewal_status"]
    search_fields = ["renewal_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PolicyCancellation)
class PolicyCancellationAdmin(admin.ModelAdmin):
    list_display = ["cancellation_number", "policy", "cancellation_date", "reason", "refund_status", "is_approved"]
    list_filter = ["reason", "refund_status", "is_approved"]
    search_fields = ["cancellation_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "policy", "version", "is_primary"]
    list_filter = ["document_type", "is_primary"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]
