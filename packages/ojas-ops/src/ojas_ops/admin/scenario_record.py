"""Django admin registration for ScenarioRecord."""

from django.contrib import admin


class ScenarioRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant_id", "name", "domain", "scale", "created_at")
    list_filter = ("tenant_id", "domain", "scale")
    search_fields = ("name", "tenant_id")
    readonly_fields = ("created_at", "updated_at")
