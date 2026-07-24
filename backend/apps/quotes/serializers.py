from rest_framework import serializers
from apps.quotes.models import Quote, QuoteItem, QuoteVersion


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class QuoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteVersion
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class QuoteListSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    items_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Quote
        fields = [
            "id", "quote_number", "quote_status", "customer", "product",
            "premium_amount", "sum_insured", "net_premium", "currency",
            "valid_until", "source", "agent", "broker", "dealer",
            "version", "is_expired", "is_valid", "items_total", "created_at",
        ]


class QuoteDetailSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    items_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Quote
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class QuoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            "id", "customer", "product", "product_variant", "agent", "broker",
            "dealer", "branch", "valid_until", "premium_amount", "sum_insured",
            "excess_amount", "tax_amount", "discount_amount", "net_premium",
            "currency", "source", "coverage_details", "risk_details",
            "rating_factors", "notes", "metadata",
        ]
        read_only_fields = ["id"]
