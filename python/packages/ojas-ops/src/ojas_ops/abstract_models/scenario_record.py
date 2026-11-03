"""AbstractScenarioRecord model definition."""

from django.db import models


class AbstractScenarioRecord(models.Model):
    """Abstract model storing declarative benchmark or operational scenarios."""

    tenant_id = models.CharField(max_length=64, default="default", db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    domain = models.CharField(max_length=64, db_index=True)
    scale = models.CharField(max_length=32, default="medium")
    definition_json = models.JSONField(default=dict)
    golden_expected_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
