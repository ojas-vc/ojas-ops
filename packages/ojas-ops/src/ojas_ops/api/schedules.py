"""Schedules API router."""

from django_bolt import Router

from ojas_ops.schemas.scheduling import (
    OptimizeScheduleRequest,
    OptimizeScheduleResponse,
    ValidateScheduleRequest,
    ValidateScheduleResponse,
)
from ojas_ops.services.optimizer import solve_schedule_service
from ojas_ops.services.validator import validate_schedule_service

router = Router()


@router.post("/optimize/sync")
async def optimize_sync(payload: OptimizeScheduleRequest) -> OptimizeScheduleResponse:
    """Synchronous CP-SAT optimization for fast operational solves (timeout <= 30s)."""
    return await solve_schedule_service(payload)


@router.post("/validate")
async def validate_schedule(payload: ValidateScheduleRequest) -> ValidateScheduleResponse:
    """Independent deterministic schedule validation without solver state."""
    return await validate_schedule_service(payload)
