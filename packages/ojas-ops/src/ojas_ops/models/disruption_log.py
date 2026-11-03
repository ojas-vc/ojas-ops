"""Concrete DisruptionLog model."""

from django.db import models

from ojas_ops.abstract_models.disruption_log import AbstractDisruptionLog


class DisruptionLog(AbstractDisruptionLog):
    """Concrete model recording operational disruptions and rescheduling impacts."""

    class Meta(AbstractDisruptionLog.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["tenant_id", "schedule_run_id"]),
            models.Index(fields=["tenant_id", "-created_at"]),
        ]
