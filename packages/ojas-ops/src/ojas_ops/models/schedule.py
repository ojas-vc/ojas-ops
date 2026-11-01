"""Schedule result models representing generated schedules and resource assignments."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from enum import StrEnum

import msgspec


class ScheduleStatus(StrEnum):
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    MODEL_INVALID = "model_invalid"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"


class ScheduledTask(msgspec.Struct, kw_only=True):
    """Execution window and assignments for a scheduled task."""

    task_id: str
    start: int
    end: int
    duration: int
    assigned_resources: list[str] = msgspec.field(default_factory=list)
    is_delayed: bool = False
    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    def overlaps(self, other: ScheduledTask) -> bool:
        """Return True if this task overlaps in time with another task."""
        return max(self.start, other.start) < min(self.end, other.end)


class ResourceAssignment(msgspec.Struct, kw_only=True):
    """Resource utilization and chronological task assignments."""

    resource_id: str
    task_ids: list[str] = msgspec.field(default_factory=list)
    total_utilized_time: int = 0
    idle_time: int = 0
    overtime: int = 0


class ScheduleResult(msgspec.Struct, kw_only=True):
    """Comprehensive outcome of a schedule optimization run."""

    status: ScheduleStatus
    objective_value: float = 0.0
    tasks: dict[str, ScheduledTask] = msgspec.field(default_factory=dict)
    resources: dict[str, ResourceAssignment] = msgspec.field(default_factory=dict)
    makespan: int = 0
    solve_time_seconds: float = 0.0
    wall_time: float = 0.0
    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    @property
    def is_feasible(self) -> bool:
        return self.status in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE)

    def get_task(self, task_id: str) -> ScheduledTask | None:
        return self.tasks.get(task_id)

    def get_resource_tasks(self, resource_id: str) -> list[ScheduledTask]:
        """Return chronological list of scheduled tasks for a given resource."""
        assigned = self.resources.get(resource_id)
        if not assigned:
            return []
        tasks = [self.tasks[tid] for tid in assigned.task_ids if tid in self.tasks]
        tasks.sort(key=lambda t: t.start)
        return tasks
