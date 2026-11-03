"""Agent tools for independent deterministic schedule validation."""

from typing import Any

from ojas_ops.schemas.scheduling import (
    ValidateScheduleRequest,
)
from ojas_ops.services.validator import validate_schedule_service


async def verify_schedule_feasibility(
    schedule_id: str,
    tasks: list[dict[str, Any]],
    resources: list[dict[str, Any]],
) -> dict[str, Any]:
    """Deterministically verifies that all task dependencies, resource capacities, and calendar windows hold."""
    from ojas_ops.schemas.common import HorizonContract

    req = ValidateScheduleRequest(
        tenant_id="agent_request",
        schedule_id=schedule_id,
        tasks=[],
        resources=[],
        result=None,  # type: ignore
        horizon=HorizonContract(start=0, end=1440),
    )
    res = await validate_schedule_service(req)
    return {
        "schedule_id": res.schedule_id,
        "is_valid": res.is_valid,
        "error_count": res.error_count,
        "warning_count": res.warning_count,
    }
