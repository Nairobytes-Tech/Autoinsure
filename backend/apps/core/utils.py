import uuid

from django.db import models
from django.utils.text import slugify


def generate_reference_number(prefix="REF", length=12):
    unique_id = uuid.uuid4().hex[:length].upper()
    return f"{prefix}-{unique_id}"


def generate_policy_number():
    return generate_reference_number("POL", 12)


def generate_claim_number():
    return generate_reference_number("CLM", 12)


def generate_quote_number():
    return generate_reference_number("QT", 10)


def generate_payment_reference():
    return generate_reference_number("PAY", 10)


def generate_receipt_number():
    return generate_reference_number("RCP", 10)


def generate_invoice_number():
    return generate_reference_number("INV", 10)


def generate_receipt_number_for_tenant(tenant_code, sequence):
    return f"{tenant_code}-RCP-{sequence:08d}"


def generate_policy_number_for_tenant(tenant_code, sequence):
    return f"{tenant_code}-POL-{sequence:08d}"


def generate_claim_number_for_tenant(tenant_code, sequence):
    return f"{tenant_code}-CLM-{sequence:08d}"


def generate_quote_number_for_tenant(tenant_code, sequence):
    return f"{tenant_code}-QT-{sequence:08d}"


def slugify_unique(value, model_class, max_length=255):
    slug = slugify(value)[:max_length]
    original_slug = slug
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{original_slug}-{counter}"[:max_length]
        counter += 1
    return slug
