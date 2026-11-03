"""Agent tools for disruption injection and reactive rescheduling."""

from typing import Any

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
    req = SimulateDisruptionRequest(
        schedule_id=schedule_id,
        disruption=DisruptionContract(
            disruption_type=dtype,
            affected_task_ids=affected_tasks,
            delay_minutes=magnitude_minutes,
        ),
    )
    res = await simulate_disruption_service(req)
    return {
        "schedule_id": res.schedule_id,
        "is_rescheduled": res.rescheduled_schedule is not None,
        "new_makespan": res.new_makespan,
        "impact_delta": res.new_makespan - res.original_makespan,
    }
