"""Serializers for ProjectWorkspace operational model."""

from __future__ import annotations

from typing import Any

from django_bolt.serializers import Serializer


class ProjectWorkspaceSerializer(Serializer):
    """Full serializer for ProjectWorkspace instances."""

    id: int
    tenant_id: str
    project_id: str
    title: str
    pipeline_type: str
    ruleset: str = ""
    status: str = "IN_PROGRESS"
    current_stage: str = ""
    temporal_workflow_id: str = ""
    completed_stages: list[str] = []
    metadata: dict[str, Any] = {}
    created_at: str = ""
    updated_at: str = ""


class ProjectWorkspaceCreateSerializer(Serializer):
    """Serializer for initializing a new ProjectWorkspace."""

    project_id: str
    title: str
    pipeline_type: str
    tenant_id: str = "default"
    ruleset: str = ""
    metadata: dict[str, Any] = {}

