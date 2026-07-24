from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "autoinsure-connect"})


urlpatterns = [
    path("health/", health_check, name="health-check"),
]
