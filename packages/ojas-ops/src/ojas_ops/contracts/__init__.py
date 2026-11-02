"""Strictly typed, contract-first communication, request/response, and event contracts."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

from ojas_ops.contracts.base import (
    APIRequest,
    APIResponse,
    Contract,
    DomainEventContract,
    ValueObject,
)
from ojas_ops.contracts.common import (
    APIError,
    CostMinorUnits,
    DurationMinutes,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    HorizonContract,
    Identifier,
    OptimalityGapBasisPoints,
    PageInfo,
    PaginatedResponse,
    PaginationQuery,
    PositiveCapacity,
    RequestContext,
    ResourceId,
    ScenarioId,
    ScheduleId,
    ScheduleTimeContext,
    TaskId,
    TenantId,
    WindowId,
)
from ojas_ops.contracts.events import (
    DisruptionInjectedEvent,
    DisruptionInjectedPayload,
    DomainEvent,
    EventMetadata,
    ScheduleOptimizedEvent,
    ScheduleOptimizedPayload,
    ScheduleValidationFailedEvent,
    ScheduleValidationFailedPayload,
)
from ojas_ops.contracts.scheduling import (
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
from ojas_ops.contracts.simulation import (
    DisruptionContract,
    DisruptionType,
    RescheduleRequest,
    RescheduleResponse,
    SimulateDisruptionRequest,
    SimulateDisruptionResponse,
)

__all__ = [
    # Base
    "APIRequest",
    "APIResponse",
    "Contract",
    "DomainEventContract",
    "ValueObject",
    # Common
    "APIError",
    "CostMinorUnits",
    "DurationMinutes",
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "HorizonContract",
    "Identifier",
    "OptimalityGapBasisPoints",
    "PageInfo",
    "PaginatedResponse",
    "PaginationQuery",
    "PositiveCapacity",
    "RequestContext",
    "ResourceId",
    "ScheduleId",
    "ScheduleTimeContext",
    "ScenarioId",
    "TaskId",
    "TenantId",
    "WindowId",
    # Scheduling
    "OptimizeScheduleRequest",
    "OptimizeScheduleResponse",
    "ResourceContract",
    "ResourceRequirementContract",
    "SolveConfigContract",
    "SolveStrategy",
    "TaskContract",
    "ValidateScheduleRequest",
    "ValidateScheduleResponse",
    # Simulation
    "DisruptionContract",
    "DisruptionType",
    "RescheduleRequest",
    "RescheduleResponse",
    "SimulateDisruptionRequest",
    "SimulateDisruptionResponse",
    # Events
    "DisruptionInjectedEvent",
    "DisruptionInjectedPayload",
    "DomainEvent",
    "EventMetadata",
    "ScheduleOptimizedEvent",
    "ScheduleOptimizedPayload",
    "ScheduleValidationFailedEvent",
    "ScheduleValidationFailedPayload",
]
