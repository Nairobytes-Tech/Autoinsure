from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "first_name", "last_name", "role", "tenant", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "tenant")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login", "failed_login_attempts", "locked_until")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "avatar")}),
        ("Roles & Access", {"fields": ("role", "tenant", "branch", "is_active", "is_staff", "is_platform_admin")}),
        ("Security", {"fields": ("mfa_enabled", "mfa_secret", "force_password_change", "failed_login_attempts", "locked_until", "email_verified", "phone_verified")}),
        ("Metadata", {"fields": ("metadata",)}),
        ("Important dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "role", "tenant"),
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "is_active", "last_activity")
    list_filter = ("is_active",)
    search_fields = ("user__email", "ip_address")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "used", "expires_at", "created_at")
    list_filter = ("used",)
