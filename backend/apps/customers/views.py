from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.customers.models import Customer, CustomerDocument, CustomerVehicle, CustomerContact
from apps.customers.serializers import (
    CustomerListSerializer, CustomerDetailSerializer,
    CustomerDocumentSerializer, CustomerVehicleSerializer, CustomerContactSerializer,
)
from apps.core.permissions import IsTenantAdmin
from apps.core.pagination import StandardResultsPagination


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related("tenant", "referred_by").all()
    pagination_class = StandardResultsPagination
    search_fields = ["first_name", "last_name", "email", "phone", "national_id_number"]
    ordering_fields = ["first_name", "last_name", "email", "created_at"]
    filterset_fields = ["status", "source", "gender", "city", "state"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        return CustomerDetailSerializer
    
    def get_permissions(self):
        return [IsTenantAdmin()]

    @action(detail=True, methods=["get"])
    def vehicles(self, request, pk=None):
        customer = self.get_object()
        vehicles = CustomerVehicle.objects.filter(customer=customer)
        serializer = CustomerVehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def documents(self, request, pk=None):
        customer = self.get_object()
        docs = CustomerDocument.objects.filter(customer=customer)
        serializer = CustomerDocumentSerializer(docs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        customer = self.get_object()
        contacts = CustomerContact.objects.filter(customer=customer)
        serializer = CustomerContactSerializer(contacts, many=True)
        return Response(serializer.data)


class CustomerDocumentViewSet(viewsets.ModelViewSet):
    queryset = CustomerDocument.objects.select_related("customer").all()
    serializer_class = CustomerDocumentSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["customer", "document_type", "is_verified"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class CustomerVehicleViewSet(viewsets.ModelViewSet):
    queryset = CustomerVehicle.objects.select_related("customer").all()
    serializer_class = CustomerVehicleSerializer
    pagination_class = StandardResultsPagination
    search_fields = ["make", "model", "registration_number", "chassis_number"]
    filterset_fields = ["customer", "status", "fuel_type", "vehicle_type"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]


class CustomerContactViewSet(viewsets.ModelViewSet):
    queryset = CustomerContact.objects.select_related("customer").all()
    serializer_class = CustomerContactSerializer
    pagination_class = StandardResultsPagination
    filterset_fields = ["customer", "contact_type"]
    
    def get_permissions(self):
        return [IsTenantAdmin()]
