"""Domain event schemas for asynchronous message brokers and audit streaming."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from ojas_ops.schemas.base import DomainEventContract, FrozenContract


class EventMetadata(DomainEventContract, frozen=True, kw_only=True):
    """Standardized event envelope metadata for all domain events."""

    event_id: UUID
    event_type: str
    tenant_id: str
    correlation_id: str
    occurred_at: datetime
    event_version: int = 1
    causation_id: str | None = None
    published_at: datetime | None = None


# --- Schedule Optimized Event ---
class ScheduleOptimizedPayload(FrozenContract, frozen=True, kw_only=True):
    """Payload published when a schedule optimization run completes successfully."""

    schedule_id: str
    project_id: str
    tenant_id: str
    status: str
    makespan: int
    objective_value: float
    tasks_count: int
    solve_time_seconds: float


class ScheduleOptimizedEvent(
    DomainEventContract,
    tag="schedule.optimized",
    tag_field="event_type",
    frozen=True,
    kw_only=True,
):
    """Event emitted when a schedule has been solved and optimized."""

    metadata: EventMetadata
    data: ScheduleOptimizedPayload


# --- Disruption Injected Event ---
class DisruptionInjectedPayload(FrozenContract, frozen=True, kw_only=True):
    """Payload published when an operational disruption affects an active schedule."""

    schedule_id: str
    delay_minutes: int = 0
    disrupted_task_id: str | None = None
    blackout_resource_id: str | None = None
    blackout_start: int | None = None
    blackout_end: int | None = None


class DisruptionInjectedEvent(
    DomainEventContract,
    tag="schedule.disruption_injected",
    tag_field="event_type",
    frozen=True,
    kw_only=True,
):
    """Event emitted when a real-world delay or resource breakdown occurs."""

    metadata: EventMetadata
    data: DisruptionInjectedPayload


# --- Schedule Validation Failed Event ---
class ScheduleValidationFailedPayload(FrozenContract, frozen=True, kw_only=True):
    """Payload published when a schedule fails independent deterministic validation."""

    schedule_id: str
    tenant_id: str
    violations_count: int
    error_count: int
    summary: str = ""


class ScheduleValidationFailedEvent(
    DomainEventContract,
    tag="schedule.validation_failed",
    tag_field="event_type",
    frozen=True,
    kw_only=True,
):
    """Event emitted when a proposed schedule violates hard constraints."""

    metadata: EventMetadata
    data: ScheduleValidationFailedPayload


# Exhaustive tagged union for decoding polymorphic domain events
DomainEvent = ScheduleOptimizedEvent | DisruptionInjectedEvent | ScheduleValidationFailedEvent
