from django.db import models

from apps.core.models import MoneyField, SoftDeleteModel, StatusModel, TenantModel


class ProductCategory(TenantModel, StatusModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "slug"], name="unique_category_slug_per_tenant"),
        ]
        indexes = [
            models.Index(fields=["tenant", "name"]),
        ]

    def __str__(self):
        return self.name

    @property
    def products_count(self):
        return self.products.filter(status="active").count()


class Product(TenantModel, StatusModel):
    class ProductType(models.TextChoices):
        MOTOR = "motor", "Motor Insurance"
        HEALTH = "health", "Health Insurance"
        LIFE = "life", "Life Insurance"
        PROPERTY = "property", "Property Insurance"
        TRAVEL = "travel", "Travel Insurance"
        LIABILITY = "liability", "Liability Insurance"
        MARINE = "marine", "Marine Insurance"
        AGRICULTURE = "agriculture", "Agriculture Insurance"
        ACCIDENT = "accident", "Accident Insurance"
        BONDS = "bonds", "Bonds"
        OTHER = "other", "Other"

    class BillingFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        ANNUAL = "annual", "Annual"
        ONE_TIME = "one_time", "One Time"

    category = models.ForeignKey(
        "products.ProductCategory",
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    code = models.CharField(max_length=30, unique=True, db_index=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices, db_index=True)
    billing_frequency = models.CharField(
        max_length=20,
        choices=BillingFrequency.choices,
        default=BillingFrequency.ANNUAL,
    )
    base_premium = MoneyField(default=0)
    minimum_premium = MoneyField(default=0)
    maximum_premium = MoneyField(default=0)
    default_sum_insured = MoneyField(default=0)
    minimum_sum_insured = MoneyField(default=0)
    maximum_sum_insured = MoneyField(default=0)
    premium_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible rating configuration: factors, multipliers, tiers, etc.",
    )
    coverage_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Default coverage items and limits for this product.",
    )
    underwriting_config = models.JSONField(default=dict, blank=True)
    document_config = models.JSONField(default=dict, blank=True)
    terms_and_conditions = models.TextField(blank=True)
    is_renewable = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    requires_vehicle = models.BooleanField(default=False)
    requires_medical = models.BooleanField(default=False)
    max_tenure_months = models.PositiveIntegerField(default=12)
    waiting_period_days = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to="products/images/", blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=["tenant", "product_type"]),
            models.Index(fields=["tenant", "category"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def active_variants_count(self):
        return self.variants.filter(status="active").count()


class ProductVariant(TenantModel, StatusModel):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="variants",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30, db_index=True)
    description = models.TextField(blank=True)
    premium_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    sum_insured_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    coverage_config = models.JSONField(default=dict, blank=True)
    premium_config = models.JSONField(default=dict, blank=True)
    base_premium = MoneyField(null=True, blank=True, help_text="Override product base premium")
    default_sum_insured = MoneyField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        constraints = [
            models.UniqueConstraint(fields=["product", "code"], name="unique_variant_code_per_product"),
        ]
        indexes = [
            models.Index(fields=["product", "is_default"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductPricing(TenantModel, StatusModel):
    class TierType(models.TextChoices):
        AGE = "age", "Age Based"
        VEHICLE_VALUE = "vehicle_value", "Vehicle Value"
        ZONE = "zone", "Geographic Zone"
        VEHICLE_TYPE = "vehicle_type", "Vehicle Type"
        CUSTOM = "custom", "Custom"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="pricing_rules",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pricing_rules",
    )
    tier_type = models.CharField(max_length=20, choices=TierType.choices)
    tier_name = models.CharField(max_length=255)
    tier_value_from = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tier_value_to = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    premium_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    premium_amount = MoneyField(null=True, blank=True)
    sum_insured = MoneyField(null=True, blank=True)
    min_premium = MoneyField(null=True, blank=True)
    max_premium = MoneyField(null=True, blank=True)
    conditions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["tier_type", "tier_value_from"]
        verbose_name = "Product Pricing"
        verbose_name_plural = "Product Pricings"
        indexes = [
            models.Index(fields=["product", "tier_type", "is_active"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.tier_name}"


class ProductDocument(TenantModel, StatusModel):
    class DocType(models.TextChoices):
        TERMS = "terms", "Terms & Conditions"
        PROSPECTUS = "prospectus", "Prospectus"
        CLAIM_FORM = "claim_form", "Claim Form"
        PROPOSAL_FORM = "proposal_form", "Proposal Form"
        PRODUCT_BRIEF = "product_brief", "Product Brief"
        FAQ = "faq", "FAQ"
        RATE_CARD = "rate_card", "Rate Card"
        GUIDELINE = "guideline", "Guidelines"
        OTHER = "other", "Other"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(max_length=20, choices=DocType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="product_documents/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=20, default="1.0")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["document_type", "-version"]
        verbose_name = "Product Document"
        verbose_name_plural = "Product Documents"
        indexes = [
            models.Index(fields=["product", "document_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.document_type}) - {self.product.name}"
