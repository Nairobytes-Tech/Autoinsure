from rest_framework import serializers
from apps.payments.models import PaymentMethod, Payment, Invoice, Receipt


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentListSerializer(serializers.ModelSerializer):
    outstanding_amount = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            "id", "reference_number", "payment_for", "payment_status", "amount",
            "paid_amount", "currency", "payment_method", "policy", "claim",
            "invoice", "payer_name", "payer_email", "is_confirmed",
            "outstanding_amount", "is_fully_paid", "payment_date", "created_at",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    outstanding_amount = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceListSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    payment_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "invoice_type", "invoice_status",
            "customer", "policy", "amount", "total_amount", "paid_amount",
            "outstanding_amount", "currency", "due_date", "issued_date",
            "is_overdue", "days_overdue", "payment_percentage", "created_at",
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    payment_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
