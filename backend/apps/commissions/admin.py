from django.contrib import admin
from apps.commissions.models import CommissionStructure, Commission, CommissionPayment


@admin.register(CommissionStructure)
class CommissionStructureAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "channel_type", "calculation_type", "rate_percentage", "effective_from", "status"]
    list_filter = ["channel_type", "calculation_type", "status"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ["policy", "earned_by_type", "commission_status", "commission_amount", "total_amount", "paid_amount", "calculation_date"]
    list_filter = ["commission_status", "earned_by_type", "is_renewal"]
    search_fields = ["policy__policy_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(CommissionPayment)
class CommissionPaymentAdmin(admin.ModelAdmin):
    list_display = ["amount", "payment_status", "payment_method", "payment_date", "transaction_reference", "period_start", "period_end"]
    list_filter = ["payment_status", "payment_method"]
    search_fields = ["transaction_reference"]
    readonly_fields = ["id", "created_at", "updated_at"]
