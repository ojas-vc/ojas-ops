"""Class-Based ViewSet for film production shooting schedule optimization."""

from __future__ import annotations

import asyncio
from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.adapters.film_production import (
    FilmScheduleResult,
    ProductionDataset,
    optimize_production_schedule,
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
        return await asyncio.to_thread(optimize_production_schedule, payload)
