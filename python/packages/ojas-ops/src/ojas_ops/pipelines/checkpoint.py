"""Checkpoint writer and reader for multi-tenant operational pipeline state persistence.

Supports Dual-Persistence:
1. File-backed: Atomic write of canonical JSON artifacts and stage checkpoints in projects/<tenant_id>/<project_id>/
2. Database-backed: Synchronization with Django ORM ProjectWorkspace and ScheduleRun models.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ojas_ops.config import get_projects_dir

logger = logging.getLogger(__name__)

PROJECT_MARKER_FILENAME = "project.json"


class CheckpointValidationError(ValueError):
    """Raised when a checkpoint payload or stage transition violates governance contracts."""


def _project_dir(tenant_id: str, project_id: str, base_dir: Optional[Path] = None) -> Path:
    base = base_dir or get_projects_dir()
    return base / tenant_id / project_id


def _checkpoint_path(tenant_id: str, project_id: str, stage: str, base_dir: Optional[Path] = None) -> Path:
    return _project_dir(tenant_id, project_id, base_dir) / f"checkpoint_{stage}.json"


def init_project(
    project_id: str,
    *,
    title: str,
    pipeline_type: str,
    tenant_id: str = "default",
    ruleset: Optional[str] = None,
    base_dir: Optional[Path] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Path:
    """Initialize a multi-tenant project workspace with canonical filesystem layout and DB record.

    Creates projects/<tenant_id>/<project_id>/ with:
      - artifacts/
      - exports/
      - logs/
      - history/
    and writes project.json, then synchronizes with ProjectWorkspace Django model.
    """
    proj_dir = _project_dir(tenant_id, project_id, base_dir)
    for sub in ("artifacts", "exports", "logs", "history"):
        (proj_dir / sub).mkdir(parents=True, exist_ok=True)

    marker_path = proj_dir / PROJECT_MARKER_FILENAME
    marker: dict[str, Any] = {}
    if marker_path.exists():
        try:
            with open(marker_path, encoding="utf-8") as f:
                marker = json.load(f)
        except Exception:
            marker = {}

    marker.setdefault("version", "1.0")
    marker.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    marker["tenant_id"] = tenant_id
    marker["project_id"] = project_id
    marker["title"] = title
    marker["pipeline_type"] = pipeline_type
    if ruleset is not None:
        marker["ruleset"] = ruleset
    if metadata:
        marker.setdefault("metadata", {}).update(metadata)

    # Write marker atomically
    tmp_marker = marker_path.with_suffix(".tmp")
    with open(tmp_marker, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp_marker, marker_path)

    # Dual-Persistence: Sync with Django ORM if available
    try:
        from ojas_ops.models.project_workspace import ProjectWorkspace

        ProjectWorkspace.objects.update_or_create(
            tenant_id=tenant_id,
            project_id=project_id,
            defaults={
                "title": title,
                "pipeline_type": pipeline_type,
                "ruleset": ruleset or "",
                "status": "IN_PROGRESS",
                "metadata": marker.get("metadata", {}),
            },
        )
    except Exception as e:
        logger.debug("ProjectWorkspace ORM sync skipped: %s", e)

    return proj_dir


def write_checkpoint(
    tenant_id: str,
    project_id: str,
    stage: str,
    status: str,
    artifacts: dict[str, Any],
    *,
    pipeline_type: str,
    ruleset: Optional[str] = None,
    checkpoint_policy: str = "guided",
    human_approval_required: bool = False,
    human_approved: bool = False,
    review: Optional[dict[str, Any]] = None,
    metrics: Optional[dict[str, Any]] = None,
    error: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    base_dir: Optional[Path] = None,
) -> Path:
    """Persist an operational stage checkpoint with gating validation and dual persistence."""
    if human_approval_required and status == "completed" and not human_approved:
        raise CheckpointValidationError(
            f"GATE VIOLATION: stage '{stage}' requires human approval but status='completed' "
            f"was written without human_approved=True. Set status='awaiting_human' and request sign-off."
        )

    proj_dir = _project_dir(tenant_id, project_id, base_dir)
    proj_dir.mkdir(parents=True, exist_ok=True)

    checkpoint: dict[str, Any] = {
        "version": "1.0",
        "tenant_id": tenant_id,
        "project_id": project_id,
        "pipeline_type": pipeline_type,
        "stage": stage,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checkpoint_policy": checkpoint_policy,
        "human_approval_required": human_approval_required,
        "human_approved": human_approved,
        "artifacts": artifacts,
    }
    if ruleset is not None:
        checkpoint["ruleset"] = ruleset
    if review is not None:
        checkpoint["review"] = review
    if metrics is not None:
        checkpoint["metrics"] = metrics
    if error is not None:
        checkpoint["error"] = error
    if metadata is not None:
        checkpoint["metadata"] = metadata

    target_path = _checkpoint_path(tenant_id, project_id, stage, base_dir)

    # Archive previous completed checkpoint to history/
    if target_path.exists():
        history_dir = proj_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archived_name = f"checkpoint_{stage}_{ts}.json"
        try:
            shutil.copy2(target_path, history_dir / archived_name)
        except Exception as e:
            logger.warning("Failed to archive superseded checkpoint: %s", e)

    # Atomic write
    tmp_path = target_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=2)
    os.replace(tmp_path, target_path)

    # Dual-Persistence: Update Django ORM ProjectWorkspace record
    try:
        from ojas_ops.models.project_workspace import ProjectWorkspace

        ws = ProjectWorkspace.objects.filter(tenant_id=tenant_id, project_id=project_id).first()
        if ws:
            completed = set(ws.completed_stages or [])
            if status == "completed":
                completed.add(stage)
            ws.completed_stages = list(completed)
            ws.current_stage = stage
            ws.status = status.upper()
            ws.save(update_fields=["completed_stages", "current_stage", "status", "updated_at"])
    except Exception as e:
        logger.debug("ProjectWorkspace ORM checkpoint update skipped: %s", e)

    return target_path


def read_checkpoint(
    tenant_id: str, project_id: str, stage: str, base_dir: Optional[Path] = None
) -> Optional[dict[str, Any]]:
    """Read a stage checkpoint file. Returns None if not found."""
    path = _checkpoint_path(tenant_id, project_id, stage, base_dir)
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to read checkpoint at %s: %s", path, e)
        return None


def get_completed_stages(
    tenant_id: str, project_id: str, pipeline_type: Optional[str] = None, base_dir: Optional[Path] = None
) -> list[str]:
    """Return list of stages that have a status='completed' checkpoint."""
    proj_dir = _project_dir(tenant_id, project_id, base_dir)
    if not proj_dir.exists():
        return []

    completed = []
    for cp_file in proj_dir.glob("checkpoint_*.json"):
        stage_name = cp_file.stem.replace("checkpoint_", "")
        cp = read_checkpoint(tenant_id, project_id, stage_name, base_dir)
        if (
            cp
            and cp.get("status") == "completed"
            and (pipeline_type is None or cp.get("pipeline_type") == pipeline_type)
        ):
            completed.append(stage_name)
    return completed


def get_next_stage(
    tenant_id: str,
    project_id: str,
    all_stages: list[str],
    pipeline_type: Optional[str] = None,
    base_dir: Optional[Path] = None,
) -> Optional[str]:
    """Determine the next stage to run based on completed checkpoints and ordered stage list."""
    completed = set(get_completed_stages(tenant_id, project_id, pipeline_type, base_dir))
    for stage in all_stages:
        if stage not in completed:
            return stage
    return None

