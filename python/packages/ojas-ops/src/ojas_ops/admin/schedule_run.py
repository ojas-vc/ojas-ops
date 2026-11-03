"""Django admin registration for ScheduleRun."""

from django.contrib import admin


class ScheduleRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant_id",
        "scenario_name",
        "status",
        "makespan",
        "solve_time_seconds",
        "created_at",
    )
    list_filter = ("tenant_id", "status", "solver_status")
    search_fields = ("scenario_name", "tenant_id")
    readonly_fields = ("created_at", "updated_at")
