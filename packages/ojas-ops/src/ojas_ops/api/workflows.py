"""Temporal workflow execution API router."""

from typing import Any

from django_bolt import Router

from ojas_ops.schemas.scheduling import OptimizeScheduleRequest
from ojas_ops.selectors.optimization_jobs import aget_job_by_workflow_id
from ojas_ops.services.temporal_dispatcher import dispatch_temporal_solve_service

router = Router()


@router.post("/solve")
async def start_optimization_workflow(payload: OptimizeScheduleRequest) -> dict[str, Any]:
    """Start an asynchronous, durable Temporal workflow for heavy optimization runs."""
    return await dispatch_temporal_solve_service(payload)


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    """Query current status, incumbent bound, and progress of a Temporal optimization workflow."""
    job = await aget_job_by_workflow_id(workflow_id)
    if not job:
        return {"status": "NOT_FOUND", "workflow_id": workflow_id}

    return {
        "status": job.status,
        "workflow_id": job.temporal_workflow_id,
        "incumbent_objective": job.incumbent_objective,
        "best_bound": job.best_bound,
        "progress_basis_points": job.progress_basis_points,
    }
