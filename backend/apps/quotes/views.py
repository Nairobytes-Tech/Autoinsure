from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.quotes.models import Quote, QuoteItem, QuoteVersion
from apps.quotes.serializers import (
    QuoteListSerializer, QuoteDetailSerializer, QuoteCreateSerializer,
    QuoteItemSerializer, QuoteVersionSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsUnderwriter
from apps.core.pagination import StandardResultsPagination


class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.select_related(
        "customer", "product", "product_variant", "agent", "broker", "dealer", "branch",
    ).all()
    pagination_class = StandardResultsPagination
    search_fields = ["quote_number", "customer__first_name", "customer__last_name", "customer__email"]
    ordering_fields = ["quote_number", "quote_status", "valid_until", "premium_amount", "created_at"]
    filterset_fields = ["quote_status", "product", "customer", "agent", "broker", "source"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return QuoteListSerializer
        if self.action == "create":
            return QuoteCreateSerializer
        return QuoteDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsUnderwriter()]

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        quote = self.get_object()
        reason = request.data.get("reason", "")
        quote.decline(reason)
        return Response({"status": "Quote declined."})

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        quote = self.get_object()
        quote.accept()
        return Response({"status": "Quote accepted."})

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        quote = self.get_object()
        items = QuoteItem.objects.filter(quote=quote)
        serializer = QuoteItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        quote = self.get_object()
        versions = QuoteVersion.objects.filter(quote=quote)
        serializer = QuoteVersionSerializer(versions, many=True)
        return Response(serializer.data)


class QuoteItemViewSet(viewsets.ModelViewSet):
    queryset = QuoteItem.objects.select_related("quote").all()
    serializer_class = QuoteItemSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["coverage_name", "coverage_code"]
    filterset_fields = ["quote", "is_included", "is_optional", "is_mandatory"]
    ordering_fields = ["display_order", "premium_amount", "created_at"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class QuoteVersionViewSet(viewsets.ModelViewSet):
    queryset = QuoteVersion.objects.select_related("quote", "changed_by").all()
    serializer_class = QuoteVersionSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["quote", "version_number"]
    ordering_fields = ["version_number", "created_at"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]
