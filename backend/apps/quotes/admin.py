from django.contrib import admin
from apps.quotes.models import Quote, QuoteItem, QuoteVersion


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ["quote_number", "quote_status", "customer", "product", "premium_amount", "valid_until", "source"]
    list_filter = ["quote_status", "source", "product"]
    search_fields = ["quote_number", "customer__first_name", "customer__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ["coverage_name", "coverage_code", "quote", "sum_insured", "premium_amount", "is_included"]
    list_filter = ["is_included", "is_optional", "is_mandatory"]
    search_fields = ["coverage_name", "coverage_code"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(QuoteVersion)
class QuoteVersionAdmin(admin.ModelAdmin):
    list_display = ["quote", "version_number", "premium_amount", "net_premium", "changed_by"]
    list_filter = []
    search_fields = ["quote__quote_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
