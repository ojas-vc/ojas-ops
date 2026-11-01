"""Task and activity data structures for scheduling."""

from __future__ import annotations

from enum import StrEnum

import msgspec

from ojas_ops.models.time import TimeWindow


class TaskPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def weight(self) -> int:
        mapping = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.HIGH: 5,
            TaskPriority.CRITICAL: 10,
        }
        return mapping[self]


class DependencyType(StrEnum):
    FS = "finish_to_start"  # Predecessor finishes before successor starts
    SS = "start_to_start"  # Predecessor starts before successor starts
    FF = "finish_to_finish"  # Predecessor finishes before successor finishes
    SF = "start_to_finish"  # Predecessor starts before successor finishes


class ResourceRequirement(msgspec.Struct, kw_only=True):
    """Resource requirement specification with capacity or candidate pool."""

    resource_id: str
    capacity: int = 1
    # If candidate_pool is provided, solver can select one resource from this pool
    candidate_pool: list[str] = msgspec.field(default_factory=list)


class TaskDependency(msgspec.Struct, kw_only=True):
    """Explicit dependency relation between two tasks with lag."""

    predecessor_id: str
    successor_id: str
    dependency_type: DependencyType = DependencyType.FS
    min_lag: int = 0
    max_lag: int | None = None


class Task(msgspec.Struct, kw_only=True):
    """A unit of schedulable work."""

    id: str
    duration: int
    name: str = ""
    time_window: TimeWindow | None = None
    required_resources: list[str] = msgspec.field(default_factory=list)
    resource_requirements: list[ResourceRequirement] = msgspec.field(default_factory=list)
    dependencies: list[str] = msgspec.field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    fixed_start: int | None = None
    cost: float = 0.0
    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.duration < 0:
            msg = f"Task '{self.id}' cannot have negative duration: {self.duration}"
            raise ValueError(msg)
        if not self.name:
            self.name = self.id
        # Automatically populate resource_requirements from required_resources if empty
        if self.required_resources and not self.resource_requirements:
            self.resource_requirements = [
                ResourceRequirement(resource_id=rid, capacity=1) for rid in self.required_resources
            ]
        elif self.resource_requirements and not self.required_resources:
            self.required_resources = [req.resource_id for req in self.resource_requirements]
