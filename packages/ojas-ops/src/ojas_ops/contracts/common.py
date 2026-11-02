"""Shared primitive contracts, validated identifiers, timestamps, and error responses."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

from datetime import datetime
from enum import StrEnum
from typing import Annotated

import msgspec

from ojas_ops.contracts.base import APIResponse, Contract, ValueObject

# --- Validated Scaled Types ---
DurationMinutes = Annotated[int, msgspec.Meta(ge=0, le=525_600)]
PositiveCapacity = Annotated[int, msgspec.Meta(ge=1, le=10_000)]
CostMinorUnits = Annotated[int, msgspec.Meta(ge=0)]
OptimalityGapBasisPoints = Annotated[int, msgspec.Meta(ge=0, le=10_000)]

# --- Validated Identifiers ---
Identifier = Annotated[
    str,
    msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$"),
]

TaskId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ResourceId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ScheduleId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ScenarioId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
TenantId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
WindowId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]


# --- Time & Planning Horizon Contracts ---
class HorizonContract(ValueObject, frozen=True, kw_only=True):
    """Discrete planning horizon for combinatorial solvers."""

    start: int = 0
    end: int = 1440  # e.g., 1 day in 1-minute ticks


class ScheduleTimeContext(Contract, kw_only=True):
    """Bridge between wall-clock timestamps and solver discrete horizon ticks."""

    reference_timestamp_utc: datetime
    tick_duration_seconds: int = 60  # 1 tick = 60 seconds
    horizon_start_tick: int = 0
    horizon_end_tick: int = 1440


# --- Pagination Contracts ---
class PaginationQuery(Contract, kw_only=True):
    """Cursor-based pagination query parameters."""

    limit: Annotated[int, msgspec.Meta(ge=1, le=200)] = 50
    cursor: str | None = None


class PageInfo(ValueObject, frozen=True, kw_only=True):
    """Cursor pagination navigation metadata."""

    has_next_page: bool
    next_cursor: str | None = None
    total_count: int | None = None


class PaginatedResponse[T](APIResponse, kw_only=True):
    """Generic paginated collection envelope."""

    items: list[T]
    page_info: PageInfo


# --- Error Contracts ---
class ErrorCode(StrEnum):
    """Authoritative operational error codes."""

    VALIDATION_FAILED = "VALIDATION_FAILED"
    INFEASIBLE_CONSTRAINTS = "INFEASIBLE_CONSTRAINTS"
    SOLVER_TIMEOUT = "SOLVER_TIMEOUT"
    MODEL_INVALID = "MODEL_INVALID"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_OVERALLOCATED = "RESOURCE_OVERALLOCATED"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_SOLVER_ERROR = "INTERNAL_SOLVER_ERROR"


class ErrorDetail(ValueObject, frozen=True, kw_only=True):
    """Specific field or constraint violation error detail."""

    field: str | None = None
    code: str = ""
    message: str = ""


class APIError(Contract, kw_only=True):
    """Structured error payload conforming to RFC 7807 guidelines."""

    code: ErrorCode
    message: str
    details: list[ErrorDetail] = msgspec.field(default_factory=list)


class ErrorResponse(APIResponse, kw_only=True):
    """Standard error response envelope."""

    error: APIError
    request_id: str
    tenant_id: str | None = None


# --- Security & Request Context ---
class RequestContext(Contract, kw_only=True):
    """Cryptographically verified multi-tenant caller identity context."""

    tenant_id: str
    actor_id: str
    correlation_id: str
    roles: list[str] = msgspec.field(default_factory=list)
