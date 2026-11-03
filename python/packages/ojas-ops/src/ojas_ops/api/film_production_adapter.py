"""Class-Based ViewSet for film production shooting schedule optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.film_production import (
    CalendarDay,
    DailyCallSheet,
    FilmCallSheetRequest,
    FilmIntradayRequest,
    FilmRescheduleRequest,
    FilmScheduleResult,
    ProductionDataset,
    generate_daily_call_sheet,
    optimize_intraday_schedule,
    optimize_production_schedule,
    reschedule_production,
)


class FilmProductionAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing film shooting schedule optimization on /adapters/film-production."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_film(
        self,
        request: Any,
        payload: ProductionDataset,
    ) -> FilmScheduleResult:
        """Optimize film production shooting schedule with Day Out of Days (DOOD) cast minimization."""
        return await asyncio.to_thread(
            optimize_production_schedule,
            payload,
            max_time_in_seconds=payload.max_time_in_seconds,
            move_penalty=payload.move_penalty,
            enable_drop_pickup=payload.enable_drop_pickup,
            enable_soundstage_lease_tracking=payload.enable_soundstage_lease_tracking,
            enable_hazard_deferral=payload.enable_hazard_deferral,
            enable_intraday_micro_optimization=payload.enable_intraday_micro_optimization,
            fixed_assignments=payload.fixed_assignments,
        )

    @action(methods=["POST"], detail=False, path="reschedule")
    async def reschedule_film(
        self,
        request: Any,
        payload: FilmRescheduleRequest,
    ) -> FilmScheduleResult:
        """Perform rolling-horizon rescheduling preserving completed days while resolving weather/cast disruptions."""
        return await asyncio.to_thread(
            reschedule_production,
            payload.dataset,
            completed_days=payload.completed_days,
            weather_disruptions=payload.weather_disruptions,
            talent_blackouts=payload.talent_blackouts,
            activate_cover_sets=payload.activate_cover_sets,
            max_time_in_seconds=payload.max_time_in_seconds,
            fixed_assignments=payload.fixed_assignments,
        )

    @action(methods=["POST"], detail=False, path="intraday")
    async def intraday_shots(
        self,
        request: Any,
        payload: FilmIntradayRequest,
    ) -> list[dict[str, Any]]:
        """Compute micro intra-day minute-level shot schedule optimizing setups and golden hour windows."""
        loc_map = {loc.id: loc for loc in payload.locations}
        tal_map = {t.id: t for t in payload.talents}
        shots = await asyncio.to_thread(
            optimize_intraday_schedule,
            payload.scenes,
            payload.calendar_day,
            loc_map,
            tal_map,
            shooting_call_minute=payload.shooting_call_minute,
            max_day_minutes=payload.max_day_minutes,
        )
        return [
            {
                "scene_id": str(s.id),
                "scene_number": s.scene_number,
                "start_minute": st,
                "end_minute": et,
                "duration_minutes": et - st,
                "setting": f"{s.setting} {s.time_of_day}",
                "location_id": str(s.location_id),
            }
            for s, st, et in shots
        ]

    @action(methods=["POST"], detail=False, path="call-sheet")
    async def call_sheet(
        self,
        request: Any,
        payload: FilmCallSheetRequest,
    ) -> DailyCallSheet:
        """Generate official daily call sheet with backward calculated actor calls and meal break times."""
        cal_dict = {c.day_number: c for c in payload.dataset.calendar}
        cal_day = cal_dict.get(payload.day_number) or CalendarDay(
            day_number=payload.day_number, calendar_date=f"Day {payload.day_number:02d}"
        )
        loc_dict = {loc.id: loc for loc in payload.dataset.locations}
        tal_dict = {t.id: t for t in payload.dataset.talents}

        res = await asyncio.to_thread(
            optimize_production_schedule,
            payload.dataset,
        )
        day_scenes = [
            s
            for s in payload.dataset.scenes
            if res.scene_day_assignments.get(str(s.id)) == payload.day_number
            or res.scene_day_assignments.get(s.id) == payload.day_number
        ]

        return await asyncio.to_thread(
            generate_daily_call_sheet,
            payload.dataset,
            payload.day_number,
            day_scenes,
            cal_day,
            loc_dict,
            tal_dict,
            hospital_info=payload.hospital_info,
            general_crew_call_time=payload.general_crew_call_time,
            shooting_call_time=payload.shooting_call_time,
            optimize_intraday=payload.optimize_intraday,
        )
