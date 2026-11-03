"""Django-Bolt API for Ojas Ops."""

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

from ojas_ops.api import health, scenarios, schedules, workflows

api = BoltAPI(
    prefix="",
    openapi_config=OpenAPIConfig(
        title="Ojas Ops Optimization API",
        version="0.2.0",
        description="Deterministic Operations Research, Scheduling, and Simulation Engine",
    ),
)

api.include_router(schedules.router, prefix="/schedules")
api.include_router(workflows.router, prefix="/workflows")
api.include_router(scenarios.router, prefix="/scenarios")
api.include_router(health.router, prefix="")

__all__ = ["api"]
