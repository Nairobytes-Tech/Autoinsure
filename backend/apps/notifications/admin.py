from django.contrib import admin
from apps.notifications.models import NotificationTemplate, Notification, NotificationPreference


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "channel", "subject", "is_default", "status"]
    list_filter = ["channel", "is_default", "status"]
    search_fields = ["name", "code", "subject"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["notification_type", "channel", "priority", "recipient", "subject", "is_read", "is_sent", "created_at"]
    list_filter = ["notification_type", "channel", "priority", "is_read", "is_sent"]
    search_fields = ["subject", "message", "recipient__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "email_enabled", "sms_enabled", "push_enabled", "in_app_enabled"]
    list_filter = ["notification_type", "email_enabled", "sms_enabled"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
