"""Django-Bolt API for Ojas Ops."""

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

from ojas_ops.api.academic_timetable_adapter import AcademicTimetableAdapterViewSet
from ojas_ops.api.cultural_calendar import CulturalCalendarViewSet
from ojas_ops.api.disruption_log import DisruptionLogModelViewSet
from ojas_ops.api.event_run_sheet_adapter import EventRunSheetAdapterViewSet
from ojas_ops.api.film_production_adapter import FilmProductionAdapterViewSet
from ojas_ops.api.health_check import HealthCheckView
from ojas_ops.api.manufacturing_adapter import ManufacturingAdapterViewSet
from ojas_ops.api.marketing_flighting_adapter import MarketingFlightingAdapterViewSet
from ojas_ops.api.optimization_job import OptimizationJobModelViewSet
from ojas_ops.api.pipeline import PipelineModelViewSet
from ojas_ops.api.project_workspace import ProjectWorkspaceModelViewSet
from ojas_ops.api.readiness_check import ReadinessCheckView
from ojas_ops.api.ruleset import RulesetViewSet
from ojas_ops.api.scenario import ScenarioModelViewSet
from ojas_ops.api.schedule_run import ScheduleRunModelViewSet
from ojas_ops.api.schedules import ScheduleViewSet
from ojas_ops.api.simulations import SimulationViewSet
from ojas_ops.api.standard_calendar import StandardCalendarViewSet
from ojas_ops.api.visualizations import VisualizationViewSet
from ojas_ops.api.workforce_adapter import WorkforceAdapterViewSet

api = BoltAPI(
    prefix="",
    middleware=[
        {
            "type": "cors",
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "QUERY"],
            "headers": None,
            "credentials": False,
            "max_age": 3600,
        }
    ],
    openapi_config=OpenAPIConfig(
        title="Ojas Ops Optimization API",
        version="0.4.0",
        description="Deterministic Operations Research, Scheduling, Simulation, and Domain Adapters Engine",
    ),
)

# --- 1. Model-Based CRUD Resources (Plural Nouns, Kebab-Case) ---
api.viewset("/schedule-runs", tags=["schedule-runs"])(ScheduleRunModelViewSet)
api.viewset("/optimization-jobs", tags=["optimization-jobs"])(OptimizationJobModelViewSet)
api.viewset("/scenarios", tags=["scenarios"])(ScenarioModelViewSet)
api.viewset("/disruption-logs", tags=["disruption-logs"])(DisruptionLogModelViewSet)
api.viewset("/projects", tags=["projects"])(ProjectWorkspaceModelViewSet)

# --- 2. Operations Research & Scheduling Services ---
api.viewset("/pipelines", tags=["pipelines"])(PipelineModelViewSet)
api.viewset("/rulesets", tags=["rulesets"])(RulesetViewSet)
api.viewset("/schedules", tags=["schedules"])(ScheduleViewSet)
api.viewset("/simulations", tags=["simulations"])(SimulationViewSet)
api.viewset("/visualizations", tags=["visualizations"])(VisualizationViewSet)
api.viewset("/calendars/cultural", tags=["calendars"])(CulturalCalendarViewSet)
api.viewset("/calendars/standard", tags=["calendars"])(StandardCalendarViewSet)

# --- 3. Domain Adapter Verticals ---
api.viewset("/adapters/film-production", tags=["adapters-film"])(FilmProductionAdapterViewSet)
api.viewset("/adapters/manufacturing", tags=["adapters-manufacturing"])(ManufacturingAdapterViewSet)
api.viewset("/adapters/workforce", tags=["adapters-workforce"])(WorkforceAdapterViewSet)
api.viewset("/adapters/marketing-flighting", tags=["adapters-marketing"])(
    MarketingFlightingAdapterViewSet
)
api.viewset("/adapters/academic-timetables", tags=["adapters-academic"])(
    AcademicTimetableAdapterViewSet
)
api.viewset("/adapters/event-run-sheets", tags=["adapters-events"])(EventRunSheetAdapterViewSet)

# --- 4. Cloud-Native Probes ---
api.view("/healthz", tags=["health"])(HealthCheckView)
api.view("/readyz", tags=["health"])(ReadinessCheckView)

__all__ = [
    "AcademicTimetableAdapterViewSet",
    "CulturalCalendarViewSet",
    "DisruptionLogModelViewSet",
    "EventRunSheetAdapterViewSet",
    "FilmProductionAdapterViewSet",
    "HealthCheckView",
    "ManufacturingAdapterViewSet",
    "MarketingFlightingAdapterViewSet",
    "OptimizationJobModelViewSet",
    "PipelineModelViewSet",
    "ProjectWorkspaceModelViewSet",
    "ReadinessCheckView",
    "RulesetViewSet",
    "ScenarioModelViewSet",
    "ScheduleRunModelViewSet",
    "ScheduleViewSet",
    "SimulationViewSet",
    "StandardCalendarViewSet",
    "VisualizationViewSet",
    "WorkforceAdapterViewSet",
    "api",
]
