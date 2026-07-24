from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.documents.views import DocumentCategoryViewSet, DocumentViewSet, DocumentVersionViewSet

router = DefaultRouter()
router.register(r"categories", DocumentCategoryViewSet, basename="document-category")
router.register(r"", DocumentViewSet, basename="document")
router.register(r"versions", DocumentVersionViewSet, basename="document-version")

urlpatterns = [
    path("", include(router.urls)),
]
