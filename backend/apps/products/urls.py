from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductCategoryViewSet, ProductViewSet,
    ProductVariantViewSet, ProductPricingViewSet, ProductDocumentViewSet,
)

router = DefaultRouter()
router.register(r"categories", ProductCategoryViewSet, basename="product-category")
router.register(r"", ProductViewSet, basename="product")
router.register(r"variants", ProductVariantViewSet, basename="product-variant")
router.register(r"pricing", ProductPricingViewSet, basename="product-pricing")
router.register(r"documents", ProductDocumentViewSet, basename="product-document")

urlpatterns = [
    path("", include(router.urls)),
]
