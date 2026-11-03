"""Class-Based ViewSet for cultural and astrological calendar intervals."""

from __future__ import annotations

from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.calendars.cultural import CulturalCalendarProvider
from ojas_ops.schemas.calendars import (
    CulturalIntervalsRequest,
    CulturalIntervalsResponse,
)


class CulturalCalendarViewSet(ViewSet):
    """Class-Based ViewSet managing cultural blackout calculations and muhurats on /calendars/cultural."""

    @action(methods=["POST"], detail=False, path="intervals")
    async def cultural_intervals(
        self,
        request: Any,
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
