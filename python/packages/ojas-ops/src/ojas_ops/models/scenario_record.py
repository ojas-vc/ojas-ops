"""Concrete ScenarioRecord model."""

from django.db import models

from ojas_ops.abstract_models.scenario_record import AbstractScenarioRecord


class ScenarioRecord(AbstractScenarioRecord):
    """Concrete model storing declarative benchmark or operational scenarios."""

    class Meta(AbstractScenarioRecord.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["tenant_id", "domain"]),
            models.Index(fields=["tenant_id", "-created_at"]),
        ]
