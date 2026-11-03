"""Class-Based ViewSet for marketing campaign budget flighting and cadence optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.marketing_flighting import MarketingFlightingScheduler
from ojas_ops.schemas.adapters import (
    MarketingOptimizeRequest,
    MarketingOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class MarketingFlightingAdapterViewSet(ViewSet):
    """Class-Based ViewSet managing marketing flighting and cadence on /adapters/marketing-flighting."""

    @action(methods=["POST"], detail=False, path="optimize")
    async def optimize_marketing(
        self,
        request: Any,
        payload: MarketingOptimizeRequest,
    ) -> MarketingOptimizeResponse:
        """Optimize multi-channel marketing budget allocation and continuous flighting cadence."""

        def _solve() -> MarketingOptimizeResponse:
            mkt = MarketingFlightingScheduler(
                horizon_days=payload.horizon_days,
            )
            for ch in payload.channels:
                mkt.channels[ch.id] = ch
            for fl in payload.flights:
                mkt.flights[fl.id] = fl
            sched = mkt.build_scheduler()
            cfg = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config=cfg)
            schedule_map: dict[str, dict[str, int]] = {
                fl.id: {
                    "start": res.tasks[fl.id].start if fl.id in res.tasks else 0,
                    "end": res.tasks[fl.id].end if fl.id in res.tasks else 0,
                }
                for fl in payload.flights
            }
            total_spend = sum(fl.duration_days * fl.daily_budget_cents for fl in payload.flights)
            return MarketingOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                total_spend_cents=total_spend,
                flights=schedule_map,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)
