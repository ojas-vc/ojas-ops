"""AbstractOptimizationJob model definition."""

from django.db import models


class AbstractOptimizationJob(models.Model):
    """Abstract model tracking an asynchronous or Temporal-managed optimization job."""

    tenant_id = models.CharField(max_length=64, default="default", db_index=True)
    temporal_workflow_id = models.CharField(max_length=128, unique=True, db_index=True)
    task_queue = models.CharField(max_length=64, default="ojas-ops-workflows")
    status = models.CharField(max_length=32, default="PENDING", db_index=True)
    incumbent_objective = models.BigIntegerField(null=True, blank=True)
    best_bound = models.BigIntegerField(null=True, blank=True)
    progress_basis_points = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
