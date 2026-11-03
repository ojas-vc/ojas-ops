"""Concrete ScheduleRun model."""

from django.db import models

from ojas_ops.abstract_models.schedule_run import AbstractScheduleRun


class ScheduleRun(AbstractScheduleRun):
    """Concrete model storing discrete schedule optimization runs."""

    class Meta(AbstractScheduleRun.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "scenario_name"]),
            models.Index(fields=["tenant_id", "-created_at"]),
        ]
