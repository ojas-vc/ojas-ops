"""Scheduling request, response, and solver parameter schemas."""

from __future__ import annotations

from enum import StrEnum

import msgspec

from ojas_ops.models.resource import ResourceType
from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.schemas.base import APIRequest, APIResponse, Contract
from ojas_ops.schemas.common import (
    CostMinorUnits,
    DurationMinutes,
    HorizonContract,
    OptimalityGapBasisPoints,
    PositiveCapacity,
    ResourceId,
    ScheduleId,
    TaskId,
    TenantId,
)
from ojas_ops.validation.report import ValidationReport


class SolveStrategy(StrEnum):
    """Preset solver strategies balancing time limit and solution optimality."""

    FAST = "fast"
    BALANCED = "balanced"
    DEEP_OPTIMAL = "deep_optimal"


class SolveConfigContract(Contract, kw_only=True):
    """Operational parameters passed to Google OR-Tools CP-SAT."""

    max_time_in_seconds: float = 30.0
    relative_gap_limit: float = 0.01  # 1.0% optimality gap
    num_workers: int = 8
    random_seed: int = 42
    log_search_progress: bool = False
    enable_warm_start: bool = True
    gap_limit_basis_points: OptimalityGapBasisPoints = 100


class ResourceRequirementContract(Contract, kw_only=True):
    """Resource requirement with capacity and candidate pool alternatives."""

    resource_id: ResourceId
    capacity: PositiveCapacity = 1
    candidate_pool: list[ResourceId] = msgspec.field(default_factory=list)


class TaskContract(Contract, kw_only=True):
    """Strictly typed contract definition of a schedulable task."""

    id: TaskId
    duration: DurationMinutes
    name: str = ""
    cost_minor: CostMinorUnits = 0
    required_resources: list[ResourceId] = msgspec.field(default_factory=list)
    resource_requirements: list[ResourceRequirementContract] = msgspec.field(default_factory=list)
    dependencies: list[TaskId] = msgspec.field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    fixed_start: int | None = None
    metadata: dict[str, str] = msgspec.field(default_factory=dict)


class ResourceContract(Contract, kw_only=True):
    """Strictly typed contract definition of an operational resource."""

    id: ResourceId
    name: str = ""
    capacity: PositiveCapacity = 1
    resource_type: ResourceType = ResourceType.MACHINE
    cost_per_time_unit_minor: CostMinorUnits = 0
    skills: list[str] = msgspec.field(default_factory=list)
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)
    metadata: dict[str, str] = msgspec.field(default_factory=dict)


class OptimizeScheduleRequest(APIRequest, kw_only=True):
    """Request contract to trigger combinatorial schedule optimization."""

    tenant_id: TenantId
    project_id: str
    tasks: list[TaskContract]
    resources: list[ResourceContract]
    horizon: HorizonContract
    schedule_id: ScheduleId | None = None
    strategy: SolveStrategy = SolveStrategy.BALANCED
    max_time_seconds: float = 30.0
    random_seed: int = 42
    enable_cultural_calendar: bool = False


class OptimizeScheduleResponse(APIResponse, kw_only=True):
    """Response contract returning the optimal schedule plan or diagnostic report."""

    schedule_id: ScheduleId
    status: ScheduleStatus
    makespan: int
    objective_value: float
    result: ScheduleResult | None = None
    validation: ValidationReport | None = None
    solve_time_seconds: float = 0.0
    tasks_scheduled_count: int = 0
    validation_summary: str = "VALID"


class ValidateScheduleRequest(APIRequest, kw_only=True):
    """Request contract to validate an existing schedule plan against domain rules."""

    tenant_id: TenantId
    schedule_id: ScheduleId | None = None
    tasks: list[TaskContract] = msgspec.field(default_factory=list)
    resources: list[ResourceContract] = msgspec.field(default_factory=list)
    horizon: HorizonContract
    result: ScheduleResult | None = None
    schedule: ScheduleResult | None = None


class ValidateScheduleResponse(APIResponse, kw_only=True):
    """Response contract containing deterministic validation findings."""

    schedule_id: ScheduleId | None = None
    is_valid: bool = True
    error_count: int = 0
    warning_count: int = 0
    report: ValidationReport | None = None
