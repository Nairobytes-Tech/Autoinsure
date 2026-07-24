from django.contrib import admin
from apps.dealers.models import Dealer


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ["dealer_code", "company_name", "trading_name", "email", "phone", "branch", "status", "dealer_type"]
    list_filter = ["status", "branch", "dealer_type"]
    search_fields = ["dealer_code", "company_name", "trading_name", "email"]
    readonly_fields = ["id", "total_policies_sold", "total_premium_generated",
                       "total_commission_earned", "total_commission_paid",
                       "total_vehicles_insured", "created_at", "updated_at"]
