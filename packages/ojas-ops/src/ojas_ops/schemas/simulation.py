"""Disruption modeling, what-if simulation, and reactive rescheduling schemas."""

from __future__ import annotations

from enum import StrEnum

import msgspec

from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus
from ojas_ops.schemas.base import APIRequest, APIResponse, Contract
from ojas_ops.schemas.common import ResourceId, ScheduleId, TaskId, TenantId


class DisruptionType(StrEnum):
    """Classification of real-world operational disruptions."""

    TASK_DELAY = "task_delay"
    RESOURCE_BREAKDOWN = "resource_breakdown"
    TASK_CANCELLATION = "task_cancellation"
    CAPACITY_REDUCTION = "capacity_reduction"


class DisruptionContract(Contract, kw_only=True):
    """Specification of an operational disturbance applied to a schedule."""

    disruption_type: DisruptionType
    task_id: TaskId | None = None
    delay_minutes: int = 0
    resource_id: ResourceId | None = None
    blackout_start: int | None = None
    blackout_end: int | None = None
    description: str = ""


class SimulateDisruptionRequest(APIRequest, kw_only=True):
    """Request contract to simulate disruption impact and reactive rescheduling."""

    tenant_id: TenantId
    schedule_id: ScheduleId
    baseline_schedule: ScheduleResult
    disruptions: list[DisruptionContract] = msgspec.field(default_factory=list)
    current_time: int = 0  # Frozen past boundary; tasks started before this cannot move


class SimulateDisruptionResponse(APIResponse, kw_only=True):
    """Response contract returning what-if impact analysis and rescheduled plan."""

    schedule_id: ScheduleId
    is_feasible: bool
    original_makespan: int
    new_makespan: int
    rescheduled_result: ScheduleResult
    affected_tasks: list[TaskId] = msgspec.field(default_factory=list)
    stability_metric: float = 0.0


class RescheduleRequest(APIRequest, kw_only=True):
    """Request contract to re-optimize an active schedule with stability objectives."""

    tenant_id: TenantId
    schedule_id: ScheduleId
    disruptions: list[DisruptionContract]
    stability_weight: float = 1.0
    current_time: int = 0


class RescheduleResponse(APIResponse, kw_only=True):
    """Response contract returning committed rescheduled outcome."""

    schedule_id: ScheduleId
    status: ScheduleStatus
    result: ScheduleResult
    makespan: int
    solve_time_seconds: float
