"""Domain models and Django database entities for Ojas Ops."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

# Pure msgspec.Struct domain records (always available with zero external dependencies)
from ojas_ops.models.calendar import CalendarEvent, CalendarKind
from ojas_ops.models.resource import Resource, ResourceType
from ojas_ops.models.schedule import (
    ResourceAssignment,
    ScheduledTask,
    ScheduleResult,
    ScheduleStatus,
)
from ojas_ops.models.task import (
    DependencyType,
    ResourceRequirement,
    Task,
    TaskDependency,
    TaskPriority,
)
from ojas_ops.models.time import Horizon, IntervalWindow, TimeWindow

# Concrete Django models (loaded on-demand or when Django settings are configured)
_DJANGO_MODELS = {
    "DisruptionLog": "ojas_ops.models.disruption_log",
    "OptimizationJob": "ojas_ops.models.optimization_job",
    "ProjectWorkspace": "ojas_ops.models.project_workspace",
    "ScenarioRecord": "ojas_ops.models.scenario_record",
    "ScheduleRun": "ojas_ops.models.schedule_run",
}


def __getattr__(name: str):
    if name in _DJANGO_MODELS:
        import importlib

        mod = importlib.import_module(_DJANGO_MODELS[name])
        val = getattr(mod, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


try:
    from django.conf import settings

    if settings.configured:
        from ojas_ops.models.disruption_log import DisruptionLog  # noqa: F401
        from ojas_ops.models.optimization_job import OptimizationJob  # noqa: F401
        from ojas_ops.models.project_workspace import ProjectWorkspace  # noqa: F401
        from ojas_ops.models.scenario_record import ScenarioRecord  # noqa: F401
        from ojas_ops.models.schedule_run import ScheduleRun  # noqa: F401
except Exception:
    pass


__all__ = [
    "CalendarEvent",
    "CalendarKind",
    "DependencyType",
    "DisruptionLog",
    "Horizon",
    "IntervalWindow",
    "OptimizationJob",
    "ProjectWorkspace",
    "Resource",
    "ResourceAssignment",
    "ResourceRequirement",
    "ResourceType",
    "ScenarioRecord",
    "ScheduleResult",
    "ScheduleRun",
    "ScheduleStatus",
    "ScheduledTask",
    "Task",
    "TaskDependency",
    "TaskPriority",
    "TimeWindow",
]
