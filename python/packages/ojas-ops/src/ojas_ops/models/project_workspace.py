"""Concrete ProjectWorkspace model."""

from django.db import models

from ojas_ops.abstract_models.project_workspace import AbstractProjectWorkspace


class ProjectWorkspace(AbstractProjectWorkspace):
    """Concrete model tracking a full-lifecycle operational project workspace."""

    class Meta(AbstractProjectWorkspace.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "-created_at"]),
            models.Index(fields=["tenant_id", "pipeline_type"]),
        ]

