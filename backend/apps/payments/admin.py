from django.contrib import admin
from apps.payments.models import PaymentMethod, Payment, Invoice, Receipt


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "method_type", "is_online", "processing_fee_percentage", "display_order"]
    list_filter = ["method_type", "is_online"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["reference_number", "payment_for", "payment_status", "amount", "paid_amount", "payment_date", "is_confirmed"]
    list_filter = ["payment_status", "payment_for", "is_confirmed"]
    search_fields = ["reference_number", "transaction_id", "payer_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "invoice_type", "invoice_status", "customer", "total_amount", "paid_amount", "due_date"]
    list_filter = ["invoice_status", "invoice_type"]
    search_fields = ["invoice_number", "customer__first_name", "customer__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "receipt_status", "amount", "payment", "receipt_date", "issued_by"]
    list_filter = ["receipt_status"]
    search_fields = ["receipt_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
