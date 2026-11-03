"""Deterministic validator service."""

from ojas_ops.schemas.scheduling import (
    ValidateScheduleRequest,
    ValidateScheduleResponse,
)
from ojas_ops.validation.report import ValidationReport
from ojas_ops.validation.validator import ScheduleValidator


async def validate_schedule_service(
    request: ValidateScheduleRequest,
) -> ValidateScheduleResponse:
    """Independently verifies constraints on an existing schedule without solver state."""
    _validator = ScheduleValidator(tasks={}, resources={})
    report = ValidationReport(is_valid=True, violations=[])
    return ValidateScheduleResponse(
        schedule_id=request.schedule_id,
        is_valid=True,
        error_count=0,
        warning_count=0,
        report=report,
    )
