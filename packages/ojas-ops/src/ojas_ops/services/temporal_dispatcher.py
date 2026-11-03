"""Temporal dispatcher service for asynchronous long-running solves."""

import os
from typing import Any

from ojas_ops.schemas.scheduling import OptimizeScheduleRequest


async def dispatch_temporal_solve_service(request: OptimizeScheduleRequest) -> dict[str, Any]:
    """Dispatches a long-running schedule optimization request to a Temporal workflow."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    workflow_id = f"opt-{request.context.tenant_id}-{request.context.schedule_id}"

    try:
        from temporalio.client import Client

        client = await Client.connect(temporal_host)
        handle = await client.start_workflow(
            "ScheduleOptimizationWorkflow",
            request,
            id=workflow_id,
            task_queue="ojas-ops-workflows",
        )
        run_id = handle.result_run_id
    except Exception as e:
        # Fallback or record error
        return {
            "status": "DISPATCH_FAILED",
            "workflow_id": workflow_id,
            "error": str(e),
        }

    try:
        from ojas_ops.models.optimization_job import OptimizationJob

        await OptimizationJob.objects.acreate(
            tenant_id=request.context.tenant_id,
            temporal_workflow_id=workflow_id,
            task_queue="ojas-ops-workflows",
            status="RUNNING",
        )
    except Exception:
        pass

    return {
        "status": "DISPATCHED",
        "workflow_id": workflow_id,
        "run_id": run_id,
    }
