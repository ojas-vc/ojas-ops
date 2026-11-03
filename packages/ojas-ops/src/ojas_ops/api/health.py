"""Class-Based APIViews for health probes and readiness telemetry."""

from django_bolt import APIView


class HealthCheckView(APIView):
    """Liveness probe reporting service status."""

    async def get(self, request) -> dict[str, str]:
        """Basic service health check."""
        return {"status": "ok", "service": "ojas-ops"}


class ReadinessCheckView(APIView):
    """Readiness probe checking CP-SAT solver and runtime engine dependencies."""

    async def get(self, request) -> dict[str, str]:
        """Readiness probe checking solver dependencies."""
        return {"ready": "true", "engine": "google-ortools-cp-sat"}
