"""Temporal activity for deterministic independent schedule validation."""

from temporalio import activity

from ojas_ops.schemas.scheduling import (
    ValidateScheduleRequest,
    ValidateScheduleResponse,
)
from ojas_ops.services.validator import validate_schedule_service


@activity.defn(name="validate_schedule_activity")
async def validate_schedule_activity(
    request: ValidateScheduleRequest,
) -> ValidateScheduleResponse:
    """Independent deterministic schedule validation activity without solver dependencies."""
    return await validate_schedule_service(request)
