"""Concrete OptimizationJob model."""

from django.db import models

from ojas_ops.abstract_models.optimization_job import AbstractOptimizationJob


class OptimizationJob(AbstractOptimizationJob):
    """Concrete model tracking an asynchronous or Temporal optimization workflow."""

    class Meta(AbstractOptimizationJob.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "-created_at"]),
        ]
