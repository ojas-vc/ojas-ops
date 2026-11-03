"""Class-Based ViewSet for workforce and nurse shift rostering optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.workforce import WorkforceScheduler
from ojas_ops.schemas.adapters import (
    WorkforceOptimizeRequest,
    WorkforceOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class WorkforceAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing workforce shift rostering on /adapters/workforce."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_workforce(
        self,
        request: Any,
        payload: WorkforceOptimizeRequest,
    ) -> WorkforceOptimizeResponse:
        """Optimize staff shift rostering with qualification matching and mandatory rest intervals."""

        def _solve() -> WorkforceOptimizeResponse:
            wf = WorkforceScheduler(
                horizon_minutes=payload.horizon_minutes,
            )
            for s in payload.staff:
                wf.staff[s.id] = s
            for sh in payload.shifts:
                wf.shifts[sh.id] = sh
            sched = wf.build_scheduler()
            cfg = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config=cfg)
            assignments: dict[str, list[str]] = {
                sh.id: res.tasks[sh.id].assigned_resources if sh.id in res.tasks else []
                for sh in payload.shifts
            }
            return WorkforceOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                solve_time_seconds=res.solve_time_seconds,
                assignments=assignments,
            )

        return await asyncio.to_thread(_solve)
