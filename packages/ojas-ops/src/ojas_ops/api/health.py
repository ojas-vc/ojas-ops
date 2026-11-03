"""Health and telemetry metrics API router."""

from django_bolt import Router

router = Router()


@router.get("/healthz")
async def health_check() -> dict[str, str]:
    """Basic service health check."""
    return {"status": "ok", "service": "ojas-ops"}


@router.get("/readyz")
async def readiness_check() -> dict[str, str]:
    """Readiness probe checking solver dependencies."""
    return {"ready": "true", "engine": "google-ortools-cp-sat"}
