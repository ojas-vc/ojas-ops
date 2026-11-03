"""AbstractScheduleRun model definition."""

from django.db import models


class AbstractScheduleRun(models.Model):
    """Abstract model representing a discrete schedule optimization execution."""

    tenant_id = models.CharField(max_length=64, default="default", db_index=True)
    scenario_name = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=32, db_index=True)
    makespan = models.BigIntegerField(null=True, blank=True)
    objective_value = models.BigIntegerField(null=True, blank=True)
    solver_status = models.CharField(max_length=32, default="UNKNOWN")
    solve_time_seconds = models.FloatField(default=0.0)
    result_json = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
