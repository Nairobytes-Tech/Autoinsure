import uuid

from django.conf import settings
from django.db import models

from apps.core.models import MoneyField, PhoneNumberField, SoftDeleteModel, StatusModel, TenantModel


class Customer(TenantModel, StatusModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    class Title(models.TextChoices):
        MR = "mr", "Mr"
        MRS = "mrs", "Mrs"
        MS = "ms", "Ms"
        DR = "dr", "Dr"
        PROF = "prof", "Prof"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="customer_profiles",
    )
    title = models.CharField(max_length=10, choices=Title.choices, blank=True)
    first_name = models.CharField(max_length=150, db_index=True)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(db_index=True)
    phone = PhoneNumberField()
    alternative_phone = PhoneNumberField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    national_id_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    tax_identification_number = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    employer_name = models.CharField(max_length=255, blank=True)
    annual_income = MoneyField(null=True, blank=True)
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("widowed", "Widowed"),
        ],
        blank=True,
    )
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    next_of_kin_name = models.CharField(max_length=255, blank=True)
    next_of_kin_phone = PhoneNumberField()
    next_of_kin_relationship = models.CharField(max_length=100, blank=True)
    next_of_kin_address = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    source = models.CharField(
        max_length=50,
        choices=[
            ("direct", "Direct"),
            ("agent", "Agent"),
            ("broker", "Broker"),
            ("dealer", "Dealer"),
            ("online", "Online"),
            ("referral", "Referral"),
        ],
        blank=True,
    )
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=["tenant", "first_name", "last_name"]),
            models.Index(fields=["tenant", "email"]),
            models.Index(fields=["tenant", "phone"]),
            models.Index(fields=["national_id_number"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(part for part in parts if part).strip()

    @property
    def age(self):
        if self.date_of_birth:
            from django.utils import timezone
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def active_policies_count(self):
        return self.policies.filter(status="active").count()

    @property
    def total_premium_paid(self):
        from django.db.models import Sum
        result = self.policies.filter(status="active").aggregate(total=Sum("premium_amount"))
        return result["total"] or 0


class CustomerDocument(SoftDeleteModel):
    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", "National ID"
        PASSPORT = "passport", "Passport"
        DRIVERS_LICENSE = "drivers_license", "Driver's License"
        UTILITY_BILL = "utility_bill", "Utility Bill"
        BANK_STATEMENT = "bank_statement", "Bank Statement"
        INCOME_PROOF = "income_proof", "Proof of Income"
        VEHICLE_REGISTRATION = "vehicle_registration", "Vehicle Registration"
        VEHICLE_PHOTO = "vehicle_photo", "Vehicle Photo"
        MEDICAL_REPORT = "medical_report", "Medical Report"
        OTHER = "other", "Other"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="customer_documents/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer Document"
        verbose_name_plural = "Customer Documents"
        indexes = [
            models.Index(fields=["customer", "document_type"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.full_name}"


class CustomerVehicle(TenantModel, StatusModel):
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="vehicles",
    )
    make = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50, blank=True)
    registration_number = models.CharField(max_length=50, unique=True, db_index=True)
    engine_number = models.CharField(max_length=100, blank=True)
    chassis_number = models.CharField(max_length=100, unique=True, db_index=True)
    engine_capacity = models.CharField(max_length=20, blank=True)
    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ("petrol", "Petrol"),
            ("diesel", "Diesel"),
            ("electric", "Electric"),
            ("hybrid", "Hybrid"),
        ],
        default="petrol",
    )
    vehicle_type = models.CharField(
        max_length=30,
        choices=[
            ("sedan", "Sedan"),
            ("suv", "SUV"),
            ("truck", "Truck"),
            ("motorcycle", "Motorcycle"),
            ("bus", "Bus"),
            ("van", "Van"),
            ("trailer", "Trailer"),
        ],
        default="sedan",
    )
    estimated_value = MoneyField(null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    driver_license_number = models.CharField(max_length=50, blank=True)
    is_financed = models.BooleanField(default=False)
    finance_company = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer Vehicle"
        verbose_name_plural = "Customer Vehicles"
        indexes = [
            models.Index(fields=["customer", "make", "model"]),
            models.Index(fields=["registration_number"]),
            models.Index(fields=["chassis_number"]),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.registration_number})"


class CustomerContact(TenantModel, StatusModel):
    class ContactType(models.TextChoices):
        PRIMARY = "primary", "Primary"
        EMERGENCY = "emergency", "Emergency"
        WORK = "work", "Work"
        HOME = "home", "Home"
        OTHER = "other", "Other"

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    contact_type = models.CharField(max_length=20, choices=ContactType.choices, default=ContactType.PRIMARY)
    contact_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField()
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=500, blank=True)
    is_primary = models.BooleanField(default=False)
    receive_notifications = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_primary", "-created_at"]
        verbose_name = "Customer Contact"
        verbose_name_plural = "Customer Contacts"
        indexes = [
            models.Index(fields=["customer", "contact_type"]),
        ]

    def __str__(self):
        return f"{self.contact_name} ({self.contact_type}) - {self.customer.full_name}"
