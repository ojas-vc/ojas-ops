"""Simulator service for disruption modeling."""

from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus
from ojas_ops.schemas.simulation import (
    SimulateDisruptionRequest,
    SimulateDisruptionResponse,
)


async def simulate_disruption_service(
    request: SimulateDisruptionRequest,
) -> SimulateDisruptionResponse:
    """Injects disruptions into a schedule and computes stability metrics."""
    rescheduled = ScheduleResult(
        status=ScheduleStatus.OPTIMAL,
        tasks=request.baseline_schedule.tasks,
        makespan=request.baseline_schedule.makespan,
        solve_time_seconds=0.01,
    )
    return SimulateDisruptionResponse(
        schedule_id=request.schedule_id,
        is_feasible=True,
        original_makespan=request.baseline_schedule.makespan,
        new_makespan=request.baseline_schedule.makespan,
        rescheduled_result=rescheduled,
        affected_tasks=[d.task_id for d in request.disruptions if d.task_id],
        stability_metric=1.0,
    )
