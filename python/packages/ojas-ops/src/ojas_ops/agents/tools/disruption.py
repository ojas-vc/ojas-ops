"""Agent tools for disruption injection and reactive rescheduling."""

from typing import Any

from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus
from ojas_ops.schemas.simulation import (
    DisruptionContract,
    DisruptionType,
    SimulateDisruptionRequest,
)
from ojas_ops.services.simulator import simulate_disruption_service


async def simulate_schedule_delay(
    schedule_id: str,
    disruption_type: str,
    magnitude_minutes: int,
    affected_tasks: list[str],
) -> dict[str, Any]:
    """Simulates an operational disruption and computes rescheduling impact."""
    dtype = getattr(DisruptionType, disruption_type.upper(), DisruptionType.TASK_DELAY)
    disruptions = [
        DisruptionContract(
            disruption_type=dtype,
            task_id=tid,
            delay_minutes=magnitude_minutes,
        )
        for tid in affected_tasks
    ] or [
        DisruptionContract(
            disruption_type=dtype,
            delay_minutes=magnitude_minutes,
        )
    ]
    req = SimulateDisruptionRequest(
        tenant_id="default",
        schedule_id=schedule_id,
        baseline_schedule=ScheduleResult(status=ScheduleStatus.OPTIMAL),
        disruptions=disruptions,
    )
    res = await simulate_disruption_service(req)
    return {
        "schedule_id": res.schedule_id,
        "is_rescheduled": res.rescheduled_result is not None,
        "new_makespan": res.new_makespan,
        "impact_delta": res.new_makespan - res.original_makespan,
    }
