"""Django admin registration for OptimizationJob."""

from django.contrib import admin


class OptimizationJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant_id",
        "temporal_workflow_id",
        "status",
        "progress_basis_points",
        "created_at",
    )
    list_filter = ("tenant_id", "status")
    search_fields = ("temporal_workflow_id", "tenant_id")
    readonly_fields = ("created_at", "updated_at")
