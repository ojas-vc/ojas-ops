"""Temporal dispatcher service for asynchronous long-running solves and HITL workflows."""

import os
from typing import Any

from ojas_ops.schemas.scheduling import OptimizeScheduleRequest


async def dispatch_temporal_solve_service(request: OptimizeScheduleRequest) -> dict[str, Any]:
    """Dispatches a long-running schedule optimization request to a Temporal workflow."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    sched_id = request.schedule_id or request.project_id
    workflow_id = f"opt-{request.tenant_id}-{sched_id}"

    error_msg: str | None = None
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
        # Fallback in local/disconnected environment
        run_id = None
        error_msg = str(e)

    try:
        from ojas_ops.models.optimization_job import OptimizationJob

        await OptimizationJob.objects.acreate(
            tenant_id=request.tenant_id,
            temporal_workflow_id=workflow_id,
            task_queue="ojas-ops-workflows",
            status="RUNNING" if error_msg is None else "DISPATCH_FAILED",
        )
    except Exception:
        pass

    if error_msg:
        return {
            "status": "DISPATCH_FAILED",
            "workflow_id": workflow_id,
            "error": error_msg,
        }

    return {
        "status": "DISPATCHED",
        "workflow_id": workflow_id,
        "run_id": run_id,
    }


async def dispatch_hitl_workflow_service(request: OptimizeScheduleRequest) -> dict[str, Any]:
    """Dispatches a Human-in-the-Loop approval workflow to Temporal."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    sched_id = request.schedule_id or request.project_id
    workflow_id = f"hitl-{request.tenant_id}-{sched_id}"

    error_msg: str | None = None
    try:
        from temporalio.client import Client

        client = await Client.connect(temporal_host)
        handle = await client.start_workflow(
            "FilmScheduleApprovalWorkflow",
            request,
            id=workflow_id,
            task_queue="ojas-ops-workflows",
        )
        run_id = handle.result_run_id
    except Exception as e:
        run_id = None
        error_msg = str(e)

    try:
        from ojas_ops.models.optimization_job import OptimizationJob

        await OptimizationJob.objects.acreate(
            tenant_id=request.tenant_id,
            temporal_workflow_id=workflow_id,
            task_queue="ojas-ops-workflows",
            status="AWAITING_APPROVAL" if error_msg is None else "DISPATCH_FAILED",
        )
    except Exception:
        pass

    if error_msg:
        return {
            "status": "DISPATCH_FAILED",
            "workflow_id": workflow_id,
            "error": error_msg,
        }

    return {
        "status": "DISPATCHED",
        "workflow_id": workflow_id,
        "run_id": run_id,
    }


async def signal_workflow_service(
    workflow_id: str,
    decision: str,
    notes: str | None = None,
) -> dict[str, Any]:
    """Sends a review decision signal to an active Human-in-the-Loop workflow."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")

    try:
        from temporalio.client import Client

        client = await Client.connect(temporal_host)
        handle = client.get_workflow_handle(workflow_id)
        if notes is not None:
            await handle.signal("submit_review_decision", args=[decision, notes])
        else:
            await handle.signal("submit_review_decision", decision)
        signal_sent = True
        error_msg = None
    except Exception as e:
        signal_sent = False
        error_msg = str(e)

    # Update DB job status if present
    try:
        from ojas_ops.models.optimization_job import OptimizationJob

        job = await OptimizationJob.objects.filter(temporal_workflow_id=workflow_id).afirst()
        if job:
            job.status = f"SIGNALED_{decision.upper()}"
            await job.asave()
    except Exception:
        pass

    return {
        "workflow_id": workflow_id,
        "status": f"SIGNALED_{decision.upper()}" if signal_sent else "SIGNAL_FAILED",
        "signal_sent": signal_sent,
        "error": error_msg,
    }


async def query_workflow_state_service(workflow_id: str) -> dict[str, Any]:
    """Queries current state and decision of a Human-in-the-Loop workflow."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")

    try:
        from temporalio.client import Client

        client = await Client.connect(temporal_host)
        handle = client.get_workflow_handle(workflow_id)
        state = await handle.query("get_review_state")
        return {"workflow_id": workflow_id, "state": state}
    except Exception as e:
        # Fallback to DB
        from ojas_ops.models.optimization_job import OptimizationJob

        job = await OptimizationJob.objects.filter(temporal_workflow_id=workflow_id).afirst()
        if job:
            return {
                "workflow_id": workflow_id,
                "state": {
                    "status": job.status,
                    "progress_basis_points": job.progress_basis_points,
                    "incumbent_objective": job.incumbent_objective,
                },
            }
        return {"workflow_id": workflow_id, "error": str(e), "status": "UNKNOWN"}
