from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.payments.models import PaymentMethod, Payment, Invoice, Receipt
from apps.payments.serializers import (
    PaymentMethodSerializer, PaymentListSerializer, PaymentDetailSerializer,
    InvoiceListSerializer, InvoiceDetailSerializer, ReceiptSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsFinanceOfficer
from apps.core.pagination import StandardResultsPagination


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code"]
    ordering_fields = ["name", "display_order"]
    filterset_fields = ["method_type", "is_online"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        "policy", "claim", "invoice", "payment_method", "confirmed_by",
    ).all()
    pagination_class = StandardResultsPagination
    search_fields = ["reference_number", "transaction_id", "payer_name", "payer_email"]
    ordering_fields = ["reference_number", "payment_status", "payment_for", "amount", "payment_date"]
    filterset_fields = ["payment_status", "payment_for", "policy", "claim", "invoice", "is_confirmed"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return PaymentDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsFinanceOfficer()]

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        payment = self.get_object()
        amount = request.data.get("amount")
        payment.confirm(request.user, amount)
        return Response({"status": "Payment confirmed."})


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("policy", "customer", "generated_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["invoice_number", "customer__first_name", "customer__last_name"]
    ordering_fields = ["invoice_number", "invoice_status", "amount", "due_date", "issued_date"]
    filterset_fields = ["invoice_status", "invoice_type", "customer", "policy"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        return InvoiceDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsFinanceOfficer()]

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.mark_paid()
        return Response({"status": "Invoice marked as paid."})


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.select_related("payment", "invoice", "issued_by").all()
    serializer_class = ReceiptSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["receipt_number", "receipt_for"]
    filterset_fields = ["receipt_status", "payment", "invoice"]
    ordering_fields = ["receipt_number", "receipt_date"]
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsFinanceOfficer()]

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        receipt = self.get_object()
        receipt.issue(request.user)
        return Response({"status": "Receipt issued."})

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        receipt = self.get_object()
        receipt.send()
        return Response({"status": "Receipt sent."})
