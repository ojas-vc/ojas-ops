"""Liveness probe APIView reporting overall service availability."""

from __future__ import annotations

from typing import Any

from django_bolt import APIView


class HealthCheckView(APIView):
    """Liveness probe reporting service status on /healthz."""

    async def get(self, request: Any) -> dict[str, str]:
        """Basic service health check."""
        return {"status": "ok", "service": "ojas-ops"}
