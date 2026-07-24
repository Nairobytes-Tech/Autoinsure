from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.products.models import ProductCategory, Product, ProductVariant, ProductPricing, ProductDocument
from apps.products.serializers import (
    ProductCategoryListSerializer, ProductCategoryDetailSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ProductPricingSerializer, ProductDocumentSerializer,
)
from apps.core.permissions import IsTenantAdmin, IsPlatformAdmin
from apps.core.pagination import StandardResultsPagination


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "display_order", "created_at"]
    filterset_fields = ["status", "parent"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ProductCategoryListSerializer
        return ProductCategoryDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code", "slug", "description"]
    ordering_fields = ["name", "code", "product_type", "base_premium", "created_at"]
    filterset_fields = ["status", "product_type", "category", "billing_frequency", "is_renewable", "is_featured"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsTenantAdmin()]
        return [IsPlatformAdmin()]

    @action(detail=True, methods=["get"])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def pricing(self, request, pk=None):
        product = self.get_object()
        pricing = ProductPricing.objects.filter(product=product)
        serializer = ProductPricingSerializer(pricing, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        product = self.get_object()
        docs = ProductDocument.objects.filter(product=product)
        serializer = ProductDocumentSerializer(docs, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["name", "code"]
    filterset_fields = ["product", "status", "is_default"]
    ordering_fields = ["name", "display_order", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class ProductPricingViewSet(viewsets.ModelViewSet):
    queryset = ProductPricing.objects.select_related("product", "variant").all()
    serializer_class = ProductPricingSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["product", "variant", "tier_type", "is_active"]
    ordering_fields = ["tier_type", "tier_value_from", "effective_from"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]


class ProductDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProductDocument.objects.select_related("product").all()
    serializer_class = ProductDocumentSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["product", "document_type", "is_active"]
    ordering_fields = ["document_type", "version", "created_at"]
    
    def get_permissions(self):
        return [IsPlatformAdmin()]
