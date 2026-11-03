"""Django-Bolt API for Ojas Ops."""

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

from ojas_ops.api.adapters import AdaptersViewSet
from ojas_ops.api.calendars import CalendarViewSet
from ojas_ops.api.health import HealthCheckView, ReadinessCheckView
from ojas_ops.api.models_views import (
    DisruptionLogModelViewSet,
    OptimizationJobModelViewSet,
    ScenarioRecordModelViewSet,
    ScheduleRunModelViewSet,
)
from ojas_ops.api.scenarios import ScenarioViewSet
from ojas_ops.api.schedules import ScheduleViewSet
from ojas_ops.api.simulation import SimulationViewSet
from ojas_ops.api.visualizations import VisualizationViewSet
from ojas_ops.api.workflows import WorkflowViewSet

api = BoltAPI(
    prefix="",
    openapi_config=OpenAPIConfig(
        title="Ojas Ops Optimization API",
        version="0.3.0",
        description="Deterministic Operations Research, Scheduling, Simulation, and Domain Adapters Engine",
    ),
)

# --- 1. ORM Model-Based Views (Full CRUD: list, retrieve, create, update, partial_update, destroy) ---
api.viewset("/schedules/runs", tags=["schedules-runs"])(ScheduleRunModelViewSet)
api.viewset("/workflows/jobs", tags=["workflows-jobs"])(OptimizationJobModelViewSet)
api.viewset("/scenarios/records", tags=["scenarios-records"])(ScenarioRecordModelViewSet)
api.viewset("/simulation/logs", tags=["simulation-logs"])(DisruptionLogModelViewSet)

# --- 2. Domain Service ViewSets (Deterministic Solvers, Adapters, Pipelines) ---
api.viewset("/schedules", tags=["schedules"])(ScheduleViewSet)
api.viewset("/workflows", tags=["workflows"])(WorkflowViewSet)
api.viewset("/simulation", tags=["simulation"])(SimulationViewSet)
api.viewset("/visualizations", tags=["visualizations"])(VisualizationViewSet)
api.viewset("/adapters", tags=["adapters"])(AdaptersViewSet)
api.viewset("/calendars", tags=["calendars"])(CalendarViewSet)
api.viewset("/scenarios", tags=["scenarios"])(ScenarioViewSet)

# --- 3. Telemetry and Health Probes (APIViews) ---
api.view("/healthz", tags=["health"])(HealthCheckView)
api.view("/readyz", tags=["health"])(ReadinessCheckView)

__all__ = [
    "AdaptersViewSet",
    "CalendarViewSet",
    "DisruptionLogModelViewSet",
    "HealthCheckView",
    "OptimizationJobModelViewSet",
    "ReadinessCheckView",
    "ScenarioRecordModelViewSet",
    "ScenarioViewSet",
    "ScheduleRunModelViewSet",
    "ScheduleViewSet",
    "SimulationViewSet",
    "VisualizationViewSet",
    "WorkflowViewSet",
    "api",
]
