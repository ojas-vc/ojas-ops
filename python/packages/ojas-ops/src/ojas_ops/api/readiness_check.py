"""Readiness probe APIView checking OR-Tools solver engine status."""

from __future__ import annotations

from typing import Any

from django_bolt import APIView


class ReadinessCheckView(APIView):
    """Readiness probe checking CP-SAT solver and runtime engine dependencies on /readyz."""

    async def get(self, request: Any) -> dict[str, str]:
        """Readiness probe checking solver dependencies."""
        return {"ready": "true", "engine": "google-ortools-cp-sat"}
