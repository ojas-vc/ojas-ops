"""Class-Based ViewSet for multi-track conference run sheet optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.event_run_sheets import EventRunSheetScheduler
from ojas_ops.schemas.adapters import (
    EventsOptimizeRequest,
    EventsOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class EventRunSheetAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing conference run sheets on /adapters/event-run-sheets."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_events(
        self,
        request: Any,
        payload: EventsOptimizeRequest,
    ) -> EventsOptimizeResponse:
        """Optimize multi-track conference agenda schedules with stage turnover setup times."""

        def _solve() -> EventsOptimizeResponse:
            ev = EventRunSheetScheduler(
                event_duration_minutes=payload.event_duration_minutes,
            )
            for h in payload.halls:
                ev.halls[h.id] = h
            for spk in payload.speakers:
                ev.speakers[spk.id] = spk
            for s in payload.sessions:
                ev.sessions[s.id] = s
            sched = ev.build_scheduler()
            cfg = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config=cfg)
            schedule: dict[str, dict[str, Any]] = {
                s.id: {
                    "start": res.tasks[s.id].start if s.id in res.tasks else 0,
                    "end": res.tasks[s.id].end if s.id in res.tasks else 0,
                    "resources": res.tasks[s.id].assigned_resources if s.id in res.tasks else [],
                }
                for s in payload.sessions
            }
            return EventsOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                session_assignments=schedule,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)
