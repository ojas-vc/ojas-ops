"""Typed msgspec schema contracts for Ojas Ops."""

from ojas_ops.schemas.common import RequestContext, ScheduleId, TaskId, TenantId
from ojas_ops.schemas.events import (
    DisruptionInjectedEvent,
    DisruptionInjectedPayload,
    DomainEvent,
    EventMetadata,
    ScheduleOptimizedEvent,
    ScheduleOptimizedPayload,
    ScheduleValidationFailedEvent,
    ScheduleValidationFailedPayload,
)
from ojas_ops.schemas.resource import Resource, ResourceType
from ojas_ops.schemas.schedule import (
    ResourceAssignment,
    ScheduledTask,
    ScheduleResult,
    ScheduleStatus,
)
from ojas_ops.schemas.scheduling import (
    OptimizeScheduleRequest,
    OptimizeScheduleResponse,
    ResourceContract,
    ResourceRequirementContract,
    SolveConfigContract,
    SolveStrategy,
    TaskContract,
    ValidateScheduleRequest,
    ValidateScheduleResponse,
)
from ojas_ops.schemas.simulation import (
    DisruptionContract,
    DisruptionType,
    RescheduleRequest,
    RescheduleResponse,
    SimulateDisruptionRequest,
    SimulateDisruptionResponse,
)
from ojas_ops.schemas.task import (
    DependencyType,
    ResourceRequirement,
    Task,
    TaskDependency,
    TaskPriority,
)
from ojas_ops.schemas.time import Horizon, IntervalWindow, TimeWindow

__all__ = [
    "DependencyType",
    "DisruptionContract",
    "DisruptionInjectedEvent",
    "DisruptionInjectedPayload",
    "DisruptionType",
    "DomainEvent",
    "EventMetadata",
    "Horizon",
    "IntervalWindow",
    "OptimizeScheduleRequest",
    "OptimizeScheduleResponse",
    "RequestContext",
    "RescheduleRequest",
    "RescheduleResponse",
    "Resource",
    "ResourceAssignment",
    "ResourceContract",
    "ResourceRequirement",
    "ResourceRequirementContract",
    "ResourceType",
    "ScheduleId",
    "ScheduleOptimizedEvent",
    "ScheduleOptimizedPayload",
    "ScheduleResult",
    "ScheduleStatus",
    "ScheduleValidationFailedEvent",
    "ScheduleValidationFailedPayload",
    "ScheduledTask",
    "SimulateDisruptionRequest",
    "SimulateDisruptionResponse",
    "SolveConfigContract",
    "SolveStrategy",
    "Task",
    "TaskContract",
    "TaskDependency",
    "TaskId",
    "TaskPriority",
    "TenantId",
    "TimeWindow",
    "ValidateScheduleRequest",
    "ValidateScheduleResponse",
]
