from django.contrib import admin
from apps.customers.models import Customer, CustomerDocument, CustomerVehicle, CustomerContact


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "phone", "status", "source", "created_at"]
    list_filter = ["status", "source", "gender"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "document_type", "customer", "is_verified", "created_at"]
    list_filter = ["document_type", "is_verified"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(CustomerVehicle)
class CustomerVehicleAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "make", "model", "year", "customer", "status"]
    list_filter = ["status", "fuel_type", "vehicle_type"]
    search_fields = ["registration_number", "chassis_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ["contact_name", "contact_type", "phone", "customer", "is_primary"]
    list_filter = ["contact_type", "is_primary"]
    readonly_fields = ["id", "created_at", "updated_at"]
