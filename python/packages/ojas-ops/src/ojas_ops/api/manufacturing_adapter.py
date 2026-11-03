"""Class-Based ViewSet for industrial manufacturing job-shop schedule optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.manufacturing import ManufacturingScheduler
from ojas_ops.schemas.adapters import (
    ManufacturingOptimizeRequest,
    ManufacturingOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class ManufacturingAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing manufacturing job-shop sequences on /adapters/manufacturing."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_manufacturing(
        self,
        request: Any,
        payload: ManufacturingOptimizeRequest,
    ) -> ManufacturingOptimizeResponse:
        """Optimize industrial job-shop sequence with family changeover setup matrices."""

        def _solve() -> ManufacturingOptimizeResponse:
            mfg = ManufacturingScheduler()
            for m in payload.machines:
                mfg.machines[m.id] = m
            for j in payload.jobs:
                mfg.jobs[j.id] = j
            for s in payload.setup_matrix:
                mfg.set_family_setup_time(s.machine_id, s.from_family, s.to_family, s.setup_minutes)
            sched = mfg.build_scheduler()
            cfg = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config=cfg)
            return ManufacturingOptimizeResponse(
                makespan=res.makespan,
                status=res.status.value,
                solve_time_seconds=res.solve_time_seconds,
                tasks={
                    tid: res.tasks[tid].assigned_resources if tid in res.tasks else []
                    for tid in sched.tasks
                },
            )

        return await asyncio.to_thread(_solve)
