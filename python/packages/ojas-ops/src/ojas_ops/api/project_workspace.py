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

    @action(methods=["POST"], detail=False, path="{project_id}/stages/{stage_name}/run")
    async def run_stage(
        self, request: Any, project_id: str, stage_name: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Dispatch or execute a pipeline stage for the project."""
        from ojas_ops.pipelines.loader import load_pipeline_manifest
        from ojas_ops.temporal.activities.agent_activity import execute_agent_stage_activity

        tenant_id = payload.get("tenant_id", "default")
        inputs = payload.get("inputs", {})

        ws = await ProjectWorkspace.objects.filter(
            tenant_id=tenant_id, project_id=project_id
        ).afirst()
        pipeline_type = ws.pipeline_type if ws else "film-crossboarding"
        ruleset_name = ws.ruleset if ws else None

        manifest = load_pipeline_manifest(pipeline_type)
        stages = manifest.get("stages", [])
        stage_def = next((s for s in stages if s.get("name") == stage_name), None)
        if not stage_def:
            stage_def = {"name": stage_name, "tools_available": []}

        result = await execute_agent_stage_activity(
            {
                "tenant_id": tenant_id,
                "project_id": project_id,
                "pipeline_name": pipeline_type,
                "stage_name": stage_name,
                "stage_def": stage_def,
                "ruleset_name": ruleset_name,
                "context_data": inputs,
                "revision_notes": payload.get("revision_notes"),
            }
        )

        cp = read_checkpoint(tenant_id, project_id, stage_name)
        return {
            "status": result.get("status", "completed"),
            "project_id": project_id,
            "stage": stage_name,
            "checkpoint": cp,
            "artifacts": result.get("artifacts", {}),
        }

    @action(methods=["POST"], detail=False, path="{project_id}/gates/{stage_name}/revise")
    async def revise_stage_gate(
        self, request: Any, project_id: str, stage_name: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Request revision on an awaiting gate and trigger stage re-execution."""
        tenant_id = payload.get("tenant_id", "default")
        feedback = payload.get("feedback", "")
        return await self.run_stage(
            request,
            project_id=project_id,
            stage_name=stage_name,
            payload={
                "tenant_id": tenant_id,
                "inputs": payload.get("overrides", {}),
                "revision_notes": feedback,
            },
        )

    @action(methods=["GET"], detail=False, path="{project_id}/artifacts/{artifact_name}")
    async def get_project_artifact(
        self, request: Any, project_id: str, artifact_name: str
    ) -> dict[str, Any]:
        """Retrieve a specific artifact JSON by name for the project."""
        from ojas_ops.config import get_projects_dir

        tenant_id = "default"
        if hasattr(request, "query") and isinstance(request.query, dict):
            tenant_id = request.query.get("tenant_id", "default")

        # 1. Check file in projects/<tenant>/<id>/artifacts/<artifact_name>.json
        p_dir = get_projects_dir() / tenant_id / project_id / "artifacts"
        target_f = p_dir / artifact_name
        if not target_f.exists() and not artifact_name.endswith(".json"):
            target_f = p_dir / f"{artifact_name}.json"

        if target_f.exists():
            try:
                with open(target_f, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 2. Check within all checkpoints
        for cp_file in (get_projects_dir() / tenant_id / project_id).glob("checkpoint_*.json"):
            try:
                with open(cp_file, encoding="utf-8") as f:
                    cp_data = json.load(f)
                    artifacts = cp_data.get("artifacts", {})
                    if artifact_name in artifacts:
                        return {"artifact_name": artifact_name, "data": artifacts[artifact_name]}
            except Exception:
                pass

        return {"status": "NOT_FOUND", "artifact_name": artifact_name, "project_id": project_id}

    @action(methods=["GET"], detail=False, path="{project_id}/events")
    async def list_project_events(self, request: Any, project_id: str) -> list[dict[str, Any]]:
        """Retrieve recent events log for this project."""
        from ojas_ops.observability import get_project_events

        tenant_id = "default"
        if hasattr(request, "query") and isinstance(request.query, dict):
            tenant_id = request.query.get("tenant_id", "default")

        return get_project_events(tenant_id, project_id, limit=100)


