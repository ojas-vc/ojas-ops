"""AbstractDisruptionLog model definition."""

from django.db import models


class AbstractDisruptionLog(models.Model):
    """Abstract model recording simulated or live operational disruptions."""

    tenant_id = models.CharField(max_length=64, default="default", db_index=True)
    schedule_run_id = models.CharField(max_length=64, db_index=True)
    disruption_type = models.CharField(max_length=64)
    magnitude_minutes = models.BigIntegerField(default=0)
    affected_tasks = models.JSONField(default=list)
    rescheduled_makespan = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
