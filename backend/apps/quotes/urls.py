from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.quotes.views import QuoteViewSet, QuoteItemViewSet, QuoteVersionViewSet

router = DefaultRouter()
router.register(r"", QuoteViewSet, basename="quote")
router.register(r"items", QuoteItemViewSet, basename="quote-item")
router.register(r"versions", QuoteVersionViewSet, basename="quote-version")

urlpatterns = [
    path("", include(router.urls)),
]
