from django.contrib import admin
from apps.brokers.models import Broker


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ["broker_code", "company_name", "trading_name", "email", "phone", "branch", "status", "license_type", "rating"]
    list_filter = ["status", "branch", "license_type"]
    search_fields = ["broker_code", "company_name", "trading_name", "email"]
    readonly_fields = ["id", "total_premium_placed", "total_commission_earned",
                       "total_commission_paid", "total_policies_sold", "total_claims_generated",
                       "credit_balance", "created_at", "updated_at"]
