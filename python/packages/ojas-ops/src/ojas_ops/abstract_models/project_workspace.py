"""AbstractProjectWorkspace model definition."""

from django.db import models


class AbstractProjectWorkspace(models.Model):
    """Abstract model tracking a full-lifecycle operational project workspace."""

    tenant_id = models.CharField(max_length=64, default="default", db_index=True)
    project_id = models.CharField(max_length=128, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    pipeline_type = models.CharField(max_length=64, db_index=True)
    ruleset = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(max_length=32, default="IN_PROGRESS", db_index=True)
    current_stage = models.CharField(max_length=64, blank=True, default="")
    temporal_workflow_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    completed_stages = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

