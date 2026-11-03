"""Django admin for DisruptionLog."""

from django.contrib import admin


class DisruptionLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant_id",
        "schedule_run_id",
        "disruption_type",
        "magnitude_minutes",
        "rescheduled_makespan",
        "created_at",
    )
    list_filter = ("disruption_type", "created_at")
    search_fields = ("tenant_id", "schedule_run_id")
    readonly_fields = ("created_at",)
