"""ModelViewSet managing operational project workspaces on /projects."""

from __future__ import annotations

import json
from typing import Any

from django_bolt import action

from ojas_ops.api.base import BaseOjasModelViewSet
from ojas_ops.models.project_workspace import ProjectWorkspace
from ojas_ops.pipelines.checkpoint import (
    get_completed_stages,
    init_project,
    read_checkpoint,
    write_checkpoint,
)
from ojas_ops.serializers.project_workspace import (
    ProjectWorkspaceCreateSerializer,
    ProjectWorkspaceSerializer,
)


class ProjectWorkspaceModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet managing project workspaces, stage execution, and HITL gate decisions."""

    queryset = ProjectWorkspace.objects.all().order_by("-created_at")
    serializer_class = ProjectWorkspaceSerializer
    create_serializer_class = ProjectWorkspaceCreateSerializer
    lookup_field = "project_id"

    @action(methods=["POST"], detail=False, path="init")
    async def initialize_project(self, request: Any, payload: dict[str, Any]) -> dict[str, Any]:
        """Initialize a project workspace on disk and database."""
        tenant_id = payload.get("tenant_id", "default")
        project_id = payload.get("project_id")
        title = payload.get("title", project_id)
        pipeline_type = payload.get("pipeline_type")
        ruleset = payload.get("ruleset")
        metadata = payload.get("metadata", {})

        if not project_id or not pipeline_type:
            return {"error": "project_id and pipeline_type are required", "status": "BAD_REQUEST"}

        proj_dir = init_project(
            project_id=project_id,
            title=title,
            pipeline_type=pipeline_type,
            tenant_id=tenant_id,
            ruleset=ruleset,
            metadata=metadata,
        )

        ws = await ProjectWorkspace.objects.filter(
            tenant_id=tenant_id, project_id=project_id
        ).afirst()

        return {
            "status": "INITIALIZED",
            "project_id": project_id,
            "tenant_id": tenant_id,
            "pipeline_type": pipeline_type,
            "path": str(proj_dir),
            "id": ws.id if ws else None,
        }

    @action(methods=["GET"], detail=False, path="{project_id}/stages/completed")
    async def list_completed_stages(self, request: Any, project_id: str) -> dict[str, Any]:
        """List stages completed for a given project."""
        tenant_id = "default"
        if hasattr(request, "query") and isinstance(request.query, dict):
            tenant_id = request.query.get("tenant_id", "default")
        completed = get_completed_stages(tenant_id, project_id)
        return {"project_id": project_id, "completed_stages": completed}

    @action(methods=["GET"], detail=False, path="{project_id}/checkpoints/{stage_name}")
    async def get_stage_checkpoint(
        self, request: Any, project_id: str, stage_name: str
    ) -> dict[str, Any]:
        """Retrieve the checkpoint payload for a specific stage."""
        tenant_id = "default"
        if hasattr(request, "query") and isinstance(request.query, dict):
            tenant_id = request.query.get("tenant_id", "default")
        cp = read_checkpoint(tenant_id, project_id, stage_name)
        if cp is None:
            return {"status": "NOT_FOUND", "project_id": project_id, "stage": stage_name}
        return cp

    @action(methods=["POST"], detail=False, path="{project_id}/gates/{stage_name}/approve")
    async def approve_stage_gate(
        self, request: Any, project_id: str, stage_name: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit Human-in-the-Loop approval for an awaiting stage gate."""
        tenant_id = payload.get("tenant_id", "default")
        notes = payload.get("notes", "")

        cp = read_checkpoint(tenant_id, project_id, stage_name)
        if not cp:
            return {"status": "NOT_FOUND", "error": f"No checkpoint found for stage {stage_name}"}

        # Update checkpoint to completed with human_approved=True
        write_checkpoint(
            tenant_id=tenant_id,
            project_id=project_id,
            stage=stage_name,
            status="completed",
            artifacts=cp.get("artifacts", {}),
            pipeline_type=cp.get("pipeline_type", "unknown"),
            ruleset=cp.get("ruleset"),
            checkpoint_policy=cp.get("checkpoint_policy", "guided"),
            human_approval_required=True,
            human_approved=True,
            review=cp.get("review"),
            metrics=cp.get("metrics"),
            metadata={**(cp.get("metadata") or {}), "approval_notes": notes},
        )

        return {
            "status": "APPROVED",
            "project_id": project_id,
            "stage": stage_name,
            "notes": notes,
        }

