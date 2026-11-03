"""Class-Based ViewSet for standard operational shift calendar blackout windows."""

from __future__ import annotations

from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.calendars.standard import StandardCalendarProvider
from ojas_ops.schemas.calendars import (
    StandardBlackoutsRequest,
    StandardBlackoutsResponse,
)


class StandardCalendarViewSet(ViewSet):
    """Class-Based ViewSet managing operational blackout windows on /calendars/standard."""

    @action(methods=["POST"], detail=False, path="blackouts")
    async def standard_blackouts(
        self,
        request: Any,
        payload: StandardBlackoutsRequest,
    ) -> StandardBlackoutsResponse:
        """Generate operational non-working blackout windows across working shifts and weekends."""
        working_days = tuple(d for d in range(7) if d not in payload.weekend_days)
        cal = StandardCalendarProvider(
            horizon_days=payload.horizon_days,
            work_start_minute=payload.working_day_start_minute,
            work_end_minute=payload.working_day_end_minute,
            working_days=working_days,
        )
        blackouts = [
            {"start": w.start, "end": w.end, "label": w.label} for w in cal.get_blackout_windows()
        ]
        return StandardBlackoutsResponse(blackout_windows=blackouts)
