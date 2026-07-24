from django.contrib import admin
from apps.branches.models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "branch_type", "manager", "email", "phone", "city", "status"]
    list_filter = ["status", "branch_type"]
    search_fields = ["name", "code", "email"]
    readonly_fields = ["id", "total_policies", "total_customers", "total_agents",
                       "total_brokers", "total_dealers", "achieved_premium", "created_at", "updated_at"]
