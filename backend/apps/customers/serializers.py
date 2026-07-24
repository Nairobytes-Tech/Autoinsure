from rest_framework import serializers
from apps.customers.models import Customer, CustomerDocument, CustomerVehicle, CustomerContact


class CustomerListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    active_policies_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            "id", "title", "first_name", "middle_name", "last_name", "full_name",
            "email", "phone", "date_of_birth", "gender", "city", "state", "country",
            "status", "source", "active_policies_count", "created_at",
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    active_policies_count = serializers.ReadOnlyField()
    total_premium_paid = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDocument
        fields = [
            "id", "customer", "document_type", "title", "description", "file",
            "original_filename", "file_size", "mime_type", "is_verified",
            "verified_by", "verified_at", "expiry_date", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerVehicle
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContact
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
