"""Class-Based ViewSet for academic course timetabling optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.academic import AcademicTimetableScheduler
from ojas_ops.schemas.adapters import (
    AcademicOptimizeRequest,
    AcademicOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class AcademicTimetableAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing classroom and faculty academic timetables on /adapters/academic-timetables."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_academic(
        self,
        request: Any,
        payload: AcademicOptimizeRequest,
    ) -> AcademicOptimizeResponse:
        """Optimize clash-free university timetables for rooms, courses, and professors."""

        def _solve() -> AcademicOptimizeResponse:
            acad = AcademicTimetableScheduler(
                horizon_minutes=payload.horizon_minutes,
            )
            for c in payload.cohorts:
                acad.cohorts[c.id] = c
            for inst in payload.instructors:
                acad.instructors[inst.id] = inst
            for room in payload.classrooms:
                acad.classrooms[room.id] = room
            for cl in payload.classes:
                acad.classes[cl.id] = cl
            sched = acad.build_scheduler()
            cfg = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config=cfg)
            timetable: dict[str, dict[str, Any]] = {
                tid: {
                    "start": t.start,
                    "end": t.end,
                    "resources": t.assigned_resources,
                }
                for tid, t in res.tasks.items()
            }
            return AcademicOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                schedule=timetable,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)
