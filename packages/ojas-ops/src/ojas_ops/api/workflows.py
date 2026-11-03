"""Class-Based ViewSet for Temporal workflow execution and Human-in-the-Loop review."""

from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.schemas.scheduling import OptimizeScheduleRequest
from ojas_ops.schemas.workflows import (
    WorkflowSignalRequest,
    WorkflowSignalResponse,
)
from ojas_ops.selectors.optimization_jobs import aget_job_by_workflow_id
from ojas_ops.services.temporal_dispatcher import (
    dispatch_hitl_workflow_service,
    dispatch_temporal_solve_service,
    query_workflow_state_service,
    signal_workflow_service,
)


class WorkflowViewSet(ViewSet):
    """Class-Based ViewSet managing asynchronous Temporal workflows and approval signals."""

    @action(methods=["POST"], detail=False, path="solve")
    async def start_optimization_workflow(
        self,
        request,
        payload: OptimizeScheduleRequest,
    ) -> dict[str, Any]:
        """Start an asynchronous, durable Temporal workflow for heavy optimization runs."""
        return await dispatch_temporal_solve_service(payload)

    @action(methods=["POST"], detail=False, path="hitl/start")
    async def start_human_in_the_loop_workflow(
        self,
        request,
        payload: OptimizeScheduleRequest,
    ) -> dict[str, Any]:
        """Start a Human-in-the-Loop approval workflow requiring explicit sign-off."""
        return await dispatch_hitl_workflow_service(payload)

    @action(methods=["GET"], detail=False, path="{workflow_id}/status")
    async def get_workflow_status(self, request, workflow_id: str) -> dict[str, Any]:
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

    @action(methods=["POST"], detail=False, path="{workflow_id}/signal/approval")
    async def signal_workflow_approval(
        self,
        request,
        workflow_id: str,
        payload: WorkflowSignalRequest,
    ) -> WorkflowSignalResponse:
        """Send an approval or rejection signal to a running Human-in-the-Loop workflow."""
        res = await signal_workflow_service(
            workflow_id=workflow_id,
            decision=payload.decision,
            notes=payload.notes,
        )
        return WorkflowSignalResponse(
            workflow_id=workflow_id,
            status=res.get("status", "SIGNALED"),
            signal_sent=res.get("signal_sent", False),
            error=res.get("error"),
        )

    @action(methods=["GET"], detail=False, path="{workflow_id}/state")
    async def get_workflow_state(self, request, workflow_id: str) -> dict[str, Any]:
        """Query current review state of a Human-in-the-Loop workflow."""
        return await query_workflow_state_service(workflow_id)
