from django.contrib import admin
from apps.tenants.models import Tenant, TenantInvitation


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "tier", "status", "is_active", "created_at"]
    list_filter = ["tier", "status", "is_active"]
    search_fields = ["name", "code", "email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "tenant", "role", "status", "expires_at", "created_at"]
    list_filter = ["status", "role"]
    search_fields = ["email"]
    readonly_fields = ["id", "token", "created_at", "updated_at"]
