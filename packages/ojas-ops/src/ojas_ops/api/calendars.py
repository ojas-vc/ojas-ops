"""Class-Based ViewSet for calendar intervals and blackout calculations."""

from django_bolt import ViewSet, action

from ojas_ops.calendars.cultural import CulturalCalendarProvider
from ojas_ops.calendars.standard import StandardCalendarProvider
from ojas_ops.schemas.calendars import (
    CulturalIntervalsRequest,
    CulturalIntervalsResponse,
    StandardBlackoutsRequest,
    StandardBlackoutsResponse,
)


class CalendarViewSet(ViewSet):
    """Class-Based ViewSet managing calendar blackout calculations and cultural muhurats."""

    @action(methods=["POST"], detail=False, path="cultural/intervals")
    async def cultural_intervals(
        self,
        request,
        payload: CulturalIntervalsRequest,
    ) -> CulturalIntervalsResponse:
        """Compute astrological/cultural inauspicious blackout intervals (Rahu Kalam, Yamagandam) and auspicious muhurats."""
        cal = CulturalCalendarProvider(
            horizon_days=payload.horizon_days,
            day_minutes=payload.day_minutes,
            enable_rahu_kalam=payload.enable_rahu_kalam,
            enable_yamagandam=payload.enable_yamagandam,
        )
        blackouts = [
            {"start": w.start, "end": w.end, "label": w.label} for w in cal.get_blackout_windows()
        ]
        auspicious = [
            {"start": w.start, "end": w.end, "label": w.label} for w in cal.get_target_windows()
        ]
        return CulturalIntervalsResponse(
            horizon_days=payload.horizon_days,
            blackout_windows=blackouts,
            auspicious_windows=auspicious,
        )

    @action(methods=["POST"], detail=False, path="standard/blackouts")
    async def standard_blackouts(
        self,
        request,
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
