"""ModelViewSet for OptimizationJob records and asynchronous Temporal workflow orchestration."""

from __future__ import annotations

from typing import Any

from django_bolt import action

from ojas_ops.api.base import BaseOjasModelViewSet
from ojas_ops.models.optimization_job import OptimizationJob
from ojas_ops.schemas.scheduling import OptimizeScheduleRequest
from ojas_ops.schemas.workflows import WorkflowSignalRequest, WorkflowSignalResponse
from ojas_ops.selectors.optimization_jobs import aget_job_by_workflow_id
from ojas_ops.serializers.optimization_job import (
    OptimizationJobCreateSerializer,
    OptimizationJobSerializer,
)
from ojas_ops.services.temporal_dispatcher import (
    dispatch_hitl_workflow_service,
    dispatch_temporal_solve_service,
    query_workflow_state_service,
    signal_workflow_service,
)


class OptimizationJobModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet managing optimization jobs and durable Temporal workflow dispatches."""

    queryset = OptimizationJob.objects.all().order_by("-created_at")
    serializer_class = OptimizationJobSerializer
    create_serializer_class = OptimizationJobCreateSerializer
    lookup_field = "id"

    @action(methods=["POST"], detail=False, path="dispatch")
    async def dispatch_solve_job(
        self,
        request: Any,
        payload: OptimizeScheduleRequest,
    ) -> dict[str, Any]:
        """Dispatch an asynchronous, durable Temporal workflow for heavy combinatorial optimization."""
        return await dispatch_temporal_solve_service(payload)

    @action(methods=["POST"], detail=False, path="hitl-dispatch")
    async def dispatch_hitl_job(
        self,
        request: Any,
        payload: OptimizeScheduleRequest,
    ) -> dict[str, Any]:
        """Dispatch a Human-in-the-Loop approval workflow requiring explicit supervisor sign-off."""
        return await dispatch_hitl_workflow_service(payload)

    @action(methods=["GET"], detail=False, path="{workflow_id}/workflow-status")
    async def get_workflow_status(self, request: Any, workflow_id: str) -> dict[str, Any]:
        """Query incumbent objective, best bound, and progress for a live Temporal workflow."""
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

    @action(methods=["POST"], detail=False, path="{workflow_id}/approvals")
    async def submit_workflow_approval(
        self,
        request: Any,
        workflow_id: str,
        payload: WorkflowSignalRequest,
    ) -> WorkflowSignalResponse:
        """Submit a Human-in-the-Loop review decision (APPROVED / REJECTED) with reviewer notes."""
        res = await signal_workflow_service(workflow_id, payload.decision, payload.notes)
        return WorkflowSignalResponse(
            workflow_id=res["workflow_id"],
            status=res["status"],
            signal_sent=res["signal_sent"],
            error=res.get("error"),
        )

    @action(methods=["GET"], detail=False, path="{workflow_id}/approval-state")
    async def get_workflow_approval_state(
        self,
        request: Any,
        workflow_id: str,
    ) -> dict[str, Any]:
        """Query current Human-in-the-Loop review and decision state."""
        return await query_workflow_state_service(workflow_id)
