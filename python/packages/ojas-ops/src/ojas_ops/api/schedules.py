"""Class-Based ViewSet for Schedule optimization and validation operations."""

from __future__ import annotations

from typing import Any

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
    """Class-Based ViewSet managing combinatorial schedule optimization and validation on /schedules."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_schedule(
        self,
        request: Any,
        payload: OptimizeScheduleRequest,
    ) -> OptimizeScheduleResponse:
        """Synchronous CP-SAT optimization for operational solves."""
        return await solve_schedule_service(payload)

    @action(methods=["POST"], detail=False, path="validate")
    async def validate_schedule(
        self,
        request: Any,
        payload: ValidateScheduleRequest,
    ) -> ValidateScheduleResponse:
        """Independent deterministic schedule validation without solver state."""
        return await validate_schedule_service(payload)
