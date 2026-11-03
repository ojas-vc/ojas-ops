"""Class-Based ViewSet for Schedule optimization and validation operations."""

from django_bolt import ViewSet, action

from ojas_ops.schemas.scheduling import (
    OptimizeScheduleRequest,
    OptimizeScheduleResponse,
    ValidateScheduleRequest,
    ValidateScheduleResponse,
)
from ojas_ops.services.optimizer import solve_schedule_service
from ojas_ops.services.validator import validate_schedule_service


class ScheduleViewSet(ViewSet):
    """Class-Based ViewSet managing combinatorial schedule optimization and validation."""

    @action(methods=["POST"], detail=False, path="optimize/sync")
    async def optimize_sync(
        self,
        request,
        payload: OptimizeScheduleRequest,
    ) -> OptimizeScheduleResponse:
        """Synchronous CP-SAT optimization for fast operational solves (timeout <= 30s)."""
        return await solve_schedule_service(payload)

    @action(methods=["POST"], detail=False, path="validate")
    async def validate_schedule(
        self,
        request,
        payload: ValidateScheduleRequest,
    ) -> ValidateScheduleResponse:
        """Independent deterministic schedule validation without solver state."""
        return await validate_schedule_service(payload)
