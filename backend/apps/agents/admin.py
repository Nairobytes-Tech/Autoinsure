from django.contrib import admin
from apps.agents.models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["agent_code", "first_name", "last_name", "email", "phone", "branch", "status", "commission_rate"]
    list_filter = ["status", "branch"]
    search_fields = ["agent_code", "first_name", "last_name", "email"]
    readonly_fields = ["id", "total_policies_sold", "total_claims_generated",
                       "total_commission_earned", "total_commission_paid", "created_at", "updated_at"]
