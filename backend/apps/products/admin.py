from django.contrib import admin
from apps.products.models import ProductCategory, Product, ProductVariant, ProductPricing, ProductDocument


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "status", "display_order", "parent", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "product_type", "billing_frequency", "category", "base_premium", "status", "is_featured"]
    list_filter = ["product_type", "billing_frequency", "status", "is_renewable", "is_featured"]
    search_fields = ["name", "code", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "product", "premium_multiplier", "is_default", "status"]
    list_filter = ["status", "is_default"]
    search_fields = ["name", "code"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ProductPricing)
class ProductPricingAdmin(admin.ModelAdmin):
    list_display = ["tier_name", "tier_type", "product", "premium_rate", "is_active", "effective_from"]
    list_filter = ["tier_type", "is_active"]
    search_fields = ["tier_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ProductDocument)
class ProductDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "product", "version", "is_active"]
    list_filter = ["document_type", "is_active"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at", "updated_at"]
