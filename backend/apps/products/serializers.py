from rest_framework import serializers
from apps.products.models import ProductCategory, Product, ProductVariant, ProductPricing, ProductDocument


class ProductCategoryListSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductCategory
        fields = [
            "id", "name", "slug", "description", "icon", "display_order",
            "parent", "status", "products_count", "created_at",
        ]


class ProductCategoryDetailSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductCategory
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPricing
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDocument
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductListSerializer(serializers.ModelSerializer):
    active_variants_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            "id", "name", "code", "slug", "product_type", "billing_frequency",
            "category", "base_premium", "minimum_premium", "maximum_premium",
            "is_renewable", "is_featured", "status", "active_variants_count", "created_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    active_variants_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
