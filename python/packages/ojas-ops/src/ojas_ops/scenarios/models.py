"""Scenario data models for golden datasets and reproducible benchmarks."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import msgspec

from ojas_ops.models.resource import ResourceType
from ojas_ops.models.schedule import ScheduleResult
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import Horizon, IntervalWindow, TimeWindow
from ojas_ops.validation.report import ValidationReport


class ScenarioMetadata(msgspec.Struct, kw_only=True):
    """Scenario descriptive metadata and scale classification."""

    name: str
    description: str = ""
    domain: str = "general"
    scale: str = "medium"  # small, medium, large, benchmark
    version: str = "1.0"
    tags: list[str] = msgspec.field(default_factory=list)


class ResourceSpec(msgspec.Struct, kw_only=True):
    """Specification of a resource in a scenario dataset."""

    id: str
    name: str = ""
    capacity: int = 1
    resource_type: ResourceType = ResourceType.MACHINE
    cost_per_time_unit: float = 0.0
    regular_capacity_limit: int | None = None
    skills: list[str] = msgspec.field(default_factory=list)
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)
    metadata: dict[str, str] = msgspec.field(default_factory=dict)


class CandidateRequirementSpec(msgspec.Struct, kw_only=True):
    """Resource requirement selecting from a candidate pool."""

    candidate_pool: list[str]
    capacity: int = 1


class TaskSpec(msgspec.Struct, kw_only=True):
    """Specification of a task in a scenario dataset."""

    id: str
    duration: int
    name: str = ""
    required_resources: list[str] = msgspec.field(default_factory=list)
    candidate_pools: list[CandidateRequirementSpec] = msgspec.field(default_factory=list)
    dependencies: list[str] = msgspec.field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    time_window: TimeWindow | None = None
    fixed_start: int | None = None
    cost: float = 0.0
    metadata: dict[str, str] = msgspec.field(default_factory=dict)


class TransitionSpec(msgspec.Struct, kw_only=True):
    """Sequence-dependent setup or turnaround buffer matrix specification."""

    resource_id: str
    default_buffer: int = 0
    # Map from "task1,task2" to buffer duration
    matrix: dict[str, int] = msgspec.field(default_factory=dict)


class WorkloadSpec(msgspec.Struct, kw_only=True):
    """Resource workload or minimum recovery rest specification."""

    resource_id: str
    max_duration: int | None = None
    min_rest: int | None = None


class MuhuratSpec(msgspec.Struct, kw_only=True):
    """Auspicious target window specification with optional task association."""

    start: int
    end: int
    task_id: str | None = None
    label: str = "Shubh Muhurat"
    hard: bool = True


class CalendarSpec(msgspec.Struct, kw_only=True):
    """Calendar provider specification for cultural or standard windows."""

    type: str = "cultural"  # cultural or standard
    enable_rahu_kalam: bool = True
    enable_yamagandam: bool = True
    muhurats: list[MuhuratSpec] = msgspec.field(default_factory=list)


class ObjectiveSpec(msgspec.Struct, kw_only=True):
    """Optimization objective specification."""

    type: str = "makespan"  # makespan, cost, idle_time, tardiness, composite
    is_maximize: bool = False
    weight: float = 1.0
    sub_objectives: list[dict[str, str | float | bool]] = msgspec.field(default_factory=list)


class ExpectedResult(msgspec.Struct, kw_only=True):
    """Golden expected results and benchmark assertions defined directly in the dataset."""

    status: str = "optimal"  # optimal or feasible
    is_valid: bool = True
    max_makespan: int | None = None
    min_makespan: int | None = None
    max_objective_value: float | None = None
    expected_task_count: int | None = None
    task_assertions: dict[str, dict[str, int | str]] = msgspec.field(default_factory=dict)


class ScenarioDefinition(msgspec.Struct, kw_only=True):
    """Complete, self-contained, typed operational scenario dataset."""

    metadata: ScenarioMetadata
    horizon: Horizon | None = None
    resources: list[ResourceSpec] = msgspec.field(default_factory=list)
    tasks: list[TaskSpec] = msgspec.field(default_factory=list)
    transitions: list[TransitionSpec] = msgspec.field(default_factory=list)
    workloads: list[WorkloadSpec] = msgspec.field(default_factory=list)
    calendar: CalendarSpec | None = None
    objective: ObjectiveSpec = msgspec.field(default_factory=ObjectiveSpec)
    expected: ExpectedResult | None = None


class ScenarioRunResult(msgspec.Struct, kw_only=True):
    """Outcome of running a scenario through solving, validation, and golden verification."""

    scenario: ScenarioDefinition
    result: ScheduleResult
    report: ValidationReport
    verification_failures: list[str] = msgspec.field(default_factory=list)

    @property
    def is_success(self) -> bool:
        """True if the schedule is valid and all golden assertions passed."""
        return self.report.is_valid and len(self.verification_failures) == 0
