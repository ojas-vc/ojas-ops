# Ojas Ops — Strictly Typed, Contract-First API & Architecture Design Guide

**Architecture Standards · Low-Level Design · Python · msgspec · OR-Tools CP-SAT · REST · RPC · Events · Internal APIs**

**Status:** Engineering Standard & Strictly Typed Conversion Guide
**Architecture:** Contract-First, Strictly Typed, Deterministic Optimization
**Primary Language:** Python 3.11–3.14 (Ruff `py314` target)
**Primary Data Contract Technology:** msgspec (`msgspec>=0.22.0`)
**Primary Optimization Engine:** Google OR-Tools CP-SAT (`ortools>=9.15.6755`)
**Static Type Checking Gate:** Mypy (`mypy>=1.10.0`) · Pyright compatible

---

# 1. Purpose and Architectural Vision

Ojas Ops adopts a **Strictly Typed, Contract-First Architecture**.

Every component that communicates with another component must have an explicitly defined, statically verifiable, and strictly validated contract. This applies regardless of whether communication happens through:

- REST APIs over HTTP (OpenAPI 3.1).
- RPC APIs such as gRPC (Protocol Buffers v3).
- Internal Python interfaces and engine bridges (`typing.Protocol`).
- Asynchronous messaging and domain events (msgspec + AsyncAPI).
- Background jobs, long-running optimization tasks, and Temporal workflows.
- Scenario definitions, benchmark datasets, and golden regression assertions.
- Operational calendars and non-Gregorian / cultural providers.
- CLI commands, test harnesses, and scheduled operations.

The objective is to eliminate loosely typed communication, undocumented assumptions, implicit data conversions (such as floating-point monetary values in combinatorial solvers), untyped dictionaries, and accidental coupling between components.

## 1.1 Core Architectural Principle

> No component should depend on another component's internal implementation. Components must communicate through explicit, versioned, strictly typed, and independently validated contracts.

Ojas Ops is the **Open Operations Research & Optimization Framework** powering deterministic combinatorial scheduling, resource allocation, simulation, and planning. It serves core operational domains through specialized domain adapters:

- **Film Production:** Scene scheduling, cast/crew turnaround windows, shooting locations, daylight availability.
- **Manufacturing:** Industrial and aerospace job-shop scheduling, machine capacity, sequence-dependent setup matrices.
- **Healthcare Workforce:** Ward nurse rostering, skill mix, maximum workload hours, mandatory recovery rest windows.
- **Academic Timetabling:** Course sections, room facilities, instructor conflicts, student curricula.
- **Event Run-Sheets:** Multi-track conference schedules, speaker availability, AV sound checks, keynote handoffs.
- **Marketing Flighting:** Multi-channel ad flighting, creative deadlines, budget caps, channel capacity.

These domain adapters share a common optimization core:

1. **Fluent Orchestrator:** `Scheduler` API.
2. **Typed Data Models:** `Task`, `Resource`, `Horizon`, `IntervalWindow`, `TimeWindow`, `ScheduleResult`.
3. **Constraint Formulations:** Precedence (FS, SS, FF, SF), No-Overlap, Cumulative Capacities, Setup Matrices, Workload Limits.
4. **Objective Goals:** Makespan, Tardiness, Cost, Idle Time, Baseline Stability, Weighted Composite.
5. **Solvers Bridge:** Google OR-Tools CP-SAT backend compiler.
6. **Pluggable Calendars:** Standard shift calendars and Hindu Cultural / Panchang calendars (Shubh Muhurats, Rahu Kalam).
7. **Independent Deterministic Validator:** Solver-agnostic verification engine (`ScheduleValidator`).
8. **Simulation & Rescheduling:** Disruption modeling, impact analysis, and minimally disruptive rescheduling.
9. **Data-Driven Scenarios:** Declarative JSON/CSV benchmarks with embedded golden assertions.

The contract architecture ensures that Ojas Ops can run as an embedded Python library, a distributed async microservice, or a remote RPC solver service without changing domain logic.

## 1.2 Core Design Principles

| Principle | Engineering Requirement |
|---|---|
| **Contract-first** | Define msgspec schemas and Protocols before implementing algorithms or endpoints |
| **Strict typing** | Ban untyped dictionaries (`dict[str, Any]`), raw `Any`, and implicit type coercion |
| **Pure-integer solver invariant** | Scale all costs, weights, and durations to integer minor units for Google OR-Tools CP-SAT |
| **Explicit boundary validation** | Validate external inputs strictly at trust boundaries with `msgspec.json.Decoder(strict=True)` |
| **Single source of truth** | Maintain canonical data definitions in `msgspec.Struct` models; generate external schemas |
| **Transport independence** | Keep core optimization logic decoupled from HTTP, gRPC, Celery, and Temporal transports |
| **Independent auditability** | Every schedule result must be verifiable by the independent validator without the solver |
| **Versioning & stability** | Make breaking schema changes explicit using semantic versioning and deprecation windows |
| **Deterministic repeatability** | Parameterize random seeds and solver configurations to ensure reproducible solutions |
| **Observability & traceability** | Include correlation IDs, tenant IDs, and solver telemetry metrics on all responses |

---

# 2. Contract Architecture

Distinguish five fundamental categories of contracts in Ojas Ops.

## 2.1 Data Contracts

Define the shape, types, constraints, and semantics of data flowing into and out of Ojas Ops.

**Technology:** `msgspec.Struct` with `forbid_unknown_fields=True` and `kw_only=True`.

Examples: `Task`, `Resource`, `ScheduleResult`, `ValidationReport`, `ScenarioDefinition`, `ExpectedResult`.

## 2.2 Behavioral Contracts

Define operations, methods, preconditions, postconditions, and mathematical invariants for internal components.

**Technology:** `typing.Protocol` with runtime checkability where required.

Examples: `OptimizationEngine`, `ScheduleValidatorProtocol`, `CalendarProviderProtocol`, `ScheduleRepository`.

## 2.3 Transport Contracts

Define how external clients, microservices, and frontends communicate with Ojas Ops over network boundaries.

**Technologies:** OpenAPI 3.1 (REST), Protocol Buffers v3 (gRPC), AsyncAPI (Event-driven).

## 2.4 Operational Contracts

Define execution semantics, resource limits, and solver operational parameters.

**Approach:** Explicit configuration contracts (`SolveConfig`, timeouts, worker threads, relative gap limit, random seeds, retry policies, and idempotency keys).

## 2.5 Compatibility Contracts

Define schema evolution rules, backward/forward compatibility, and golden regression assertions.

**Approach:** Automated schema compatibility checks in CI, golden dataset verification (`test_scenarios.py`), and expand-and-contract migrations.

---

# 3. Technology Standards

Establish the following technology choices as the mandatory engineering standards for Ojas Ops:

| Area | Standard | Rationale & Ecosystem Fit |
|---|---|---|
| **Python Version** | Python 3.11–3.14 (Ruff `py314`) | High-performance Python with modern type union syntax (`X \| Y`), `StrEnum`, and pattern matching |
| **Data Contracts & Validation** | `msgspec>=0.22.0` | 10–50x faster serialization than Pydantic/dataclasses; microsecond JSON/MessagePack encoding |
| **Combinatorial Solver** | Google OR-Tools CP-SAT (`>=9.15.6755`) | Industry-standard deterministic constraint programming engine; SAT-based integer solver |
| **Static Type Checking** | Mypy (`>=1.10.0`) | Configured via `Makefile` (`make typecheck`, `make mypy`, `make check`); Pyright compatible |
| **Formatting and Linting** | Ruff (`>=0.8.0`) | Lightning-fast linter and formatter enforcing standard Python rules (`E`, `F`, `I`, `UP`, `B`, `C4`) |
| **Unit & Integration Testing** | pytest (`>=8.0.0`) | Standard test suite supporting fast inner-loop execution (`make test-fast`) and coverage |
| **Property-Based Testing** | Hypothesis | Exhaustive fuzz testing of constraint invariants and mathematical schedule boundaries |
| **Scenario Verification** | Native Ojas Ops Scenarios | Declarative JSON/CSV test datasets with embedded golden assertions (`verify_expected()`) |
| **REST Documentation** | OpenAPI 3.1 | Machine-readable API specifications generated directly from canonical contract schemas |
| **HTTP Framework** | django-bolt / FastAPI ASGI | Rust-powered async API within Ojas platform; lightweight ASGI for standalone ops services |
| **RPC & Interoperability** | gRPC + Protocol Buffers v3 | High-throughput typed RPC for inter-service solver calls and non-Python clients |
| **Event Schemas & Streaming** | msgspec + AsyncAPI | Strictly typed domain events (`ScheduleOptimizedEvent`, `DisruptionInjectedEvent`) |
| **Workflow Orchestration** | Temporal Python SDK | Durable stateful workflows for multi-minute combinatorial optimization jobs |
| **Serialization Formats** | JSON / MessagePack / Protobuf | Zero-overhead JSON for REST, MessagePack for caching/internal IPC, Protobuf for gRPC |

### 3.1 Critical Solver Invariant: Integer Scaling for CP-SAT

> [!IMPORTANT]
> **Google OR-Tools CP-SAT is a pure integer solver.** It does not support floating-point decision variables or coefficients in objectives or constraints.
>
> All costs, monetary rates, penalty weights, and time durations must be represented as **scaled integer minor units** (e.g. `cost_minor: int`, `cost_per_time_unit_minor: int`, or integer weight multipliers). Floating-point arithmetic introduces non-deterministic rounding errors and is strictly prohibited in solver models.

---

# 4. Canonical Contract Definitions with msgspec

## 4.1 Repository and Subsystem Structure

Ojas Ops organizes its contracts directly within the `ojas-ops` package under the `ojas_ops.contracts` module.

> [!NOTE]
> **Strict Modular Boundary:**
> `ojas_ops.contracts` houses purely declarative data structures, wire DTOs, and serialization logic. It must never import from `ojas_ops.solvers` or Google OR-Tools.

```text
ojas-ops/
├── Makefile                               # Developer & CI commands (make check, make test, etc.)
├── pyproject.toml                         # Workspace definition (Python >=3.11, <3.15)
├── uv.lock                                # Pinned dependencies
├── packages/
│   └── ojas-ops/                          # Core standalone framework
│       ├── pyproject.toml
│       ├── src/
│       │   └── ojas_ops/
│       │       ├── __init__.py            # Public package exports
│       │       ├── contracts/             # Strictly typed wire contracts, DTOs & events
│       │       │   ├── __init__.py
│       │       │   ├── base.py            # Contract, APIRequest, APIResponse, ValueObject
│       │       │   ├── common.py          # Identifiers, pagination, errors, RequestContext
│       │       │   ├── scheduling.py      # OptimizeScheduleRequest, OptimizeScheduleResponse
│       │       │   ├── simulation.py      # DisruptionRequest, RescheduleResponse
│       │       │   └── events.py          # ScheduleOptimizedEvent, DisruptionInjectedEvent
│       │       ├── models/                # Core typed domain models (Task, Resource, Horizon, etc.)
│       │       ├── constraints/           # Precedence, No-Overlap, Cumulative, Setup, Workload
│       │       ├── objectives/            # Makespan, Tardiness, Cost, Idle Time, Stability
│       │       ├── solvers/               # CP-SAT compilation bridge & configuration
│       │       ├── calendars/             # Standard & Cultural/Panchang calendar providers
│       │       ├── scheduling/            # Fluent Scheduler orchestrator
│       │       ├── simulation/            # What-if disruption modeling & reactive rescheduling
│       │       ├── scenarios/             # Declarative scenario models, loaders & runners
│       │       ├── adapters/              # 6 industry-specific domain adapters
│       │       └── validation/            # Independent deterministic validator & reporting
│       └── tests/                         # Pytest test suite across all subsystems
│
├── examples/                              # Runnable end-to-end domain examples & benchmark datasets
│   ├── basic_scheduling/
│   ├── manufacturing/
│   ├── nurse_rostering/
│   ├── film_production/
│   ├── academic_timetabling/
│   ├── event_run_sheets/
│   ├── festival_calendar/
│   └── marketing_flighting/
│
├── schemas/                               # Generated or checked external schemas
│   ├── openapi/                           # OpenAPI 3.1 REST contracts
│   ├── protobuf/                          # Protobuf v3 gRPC definitions
│   └── asyncapi/                          # AsyncAPI event definitions
│
└── docs/                                  # Documentation site (MkDocs Material)
    ├── index.md
    ├── architecture.md
    ├── guidelines.md                      # This design guide
    ├── models.md
    ├── constraints.md
    ├── objectives.md
    ├── solvers.md
    ├── validation.md
    ├── simulation.md
    ├── scenarios.md
    └── adapters.md
```

The `contracts/` module must not import heavy runtime dependencies like OR-Tools CP-SAT or database engines. It must contain purely declarative data structures, type constraints, and serialization logic.

## 4.2 Standard msgspec Configuration

Use explicit struct configuration rather than relying on loose defaults:

```python
from __future__ import annotations
import msgspec


class Contract(msgspec.Struct, forbid_unknown_fields=True, kw_only=True):
    """Base contract for all Ojas Ops data structures.

    Enforces strict typing, explicit keyword-only initialization,
    and automatic rejection of unknown payload fields.
    """

    pass


class APIRequest(Contract):
    """Base contract for external incoming requests."""

    pass


class APIResponse(Contract):
    """Base contract for outgoing API responses."""

    pass


class ValueObject(Contract, frozen=True):
    """Immutable value object contract (e.g. intervals, time windows)."""

    pass


class DomainEventContract(Contract, frozen=True):
    """Immutable domain event contract for message brokers."""

    pass
```

### Key Configuration Rules:
1. `forbid_unknown_fields=True` on all request and domain contracts to reject misspelled or unexpected fields at the boundary.
2. `kw_only=True` to eliminate argument ordering bugs when creating complex models.
3. `frozen=True` for value objects, intervals, and event records to guarantee immutability.
4. `strict=True` on all `msgspec.json.Decoder` instances to forbid loose type coercions (e.g. auto-converting string `"123"` to `int 123` or string `"true"` to `bool`).

## 4.3 Strict Decoding at Boundaries

Every boundary that accepts external JSON, YAML, or MessagePack must validate data with strict decoding:

```python
import msgspec
from ojas_ops.models import Task

# Initialize a reusable, thread-safe strict decoder
task_decoder = msgspec.json.Decoder(type=Task, strict=True)

# Decode incoming payload strictly
try:
    task = task_decoder.decode(raw_json_bytes)
except msgspec.ValidationError as exc:
    # Handle schema violation cleanly at the boundary
    raise InvalidRequestError(f"Schema validation failed: {exc}") from exc
```

Never do:
```python
# PROHIBITED: Untyped parsing without boundary validation
data = json.loads(request_body)
task = Task(id=data["id"], duration=data["duration"])
```

## 4.4 Explicit Constraints and Type Annotations

Express operational boundaries directly in type annotations using `Annotated` and `msgspec.Meta`:

```python
from typing import Annotated
import msgspec

# Non-negative durations in minutes (0 allowed for milestone markers)
DurationMinutes = Annotated[int, msgspec.Meta(ge=0, le=525_600)]

# Positive resource capacity (must be at least 1)
PositiveCapacity = Annotated[int, msgspec.Meta(ge=1, le=10_000)]

# Monetary values and costs in integer minor units (e.g. cents/paise)
CostMinorUnits = Annotated[int, msgspec.Meta(ge=0)]

# Relative optimality gap limit in basis points (e.g. 100 bp = 1.0%)
OptimalityGapBasisPoints = Annotated[int, msgspec.Meta(ge=0, le=10_000)]


class ResourceRequirementContract(Contract):
    resource_id: str
    capacity: PositiveCapacity = 1
    candidate_pool: list[str] = msgspec.field(default_factory=list)


class TaskContract(Contract):
    id: str
    duration: DurationMinutes
    name: str = ""
    cost_minor: CostMinorUnits = 0
    required_resources: list[str] = msgspec.field(default_factory=list)
    resource_requirements: list[ResourceRequirementContract] = msgspec.field(default_factory=list)
    dependencies: list[str] = msgspec.field(default_factory=list)
```

---

# 5. Contract Taxonomy and Naming Conventions

Ojas Ops enforces strict, unambiguous taxonomy for all contract artifacts.

## 5.1 Categorization of Contracts

- **Command:** An instruction requesting Ojas Ops to perform an action (e.g. `OptimizeScheduleCommand`).
- **Query:** A request to read information without side effects (e.g. `GetScheduleQuery`).
- **Request DTO:** Transport-specific wire input (e.g. `OptimizeScheduleRequest`).
- **Response DTO:** Transport-specific wire output (e.g. `OptimizeScheduleResponse`).
- **Result:** Application/domain level outcome (e.g. `ScheduleResult`, `ValidationReport`).
- **Domain Event:** A published fact stating that an operational event occurred (e.g. `ScheduleOptimizedEvent`).
- **Specification (Spec):** A declarative definition used in benchmarks or scenarios (e.g. `TaskSpec`, `ResourceSpec`).

## 5.2 Naming Conventions Table

| Contract Type | Naming Convention | Ojas Ops Example |
|---|---|---|
| **REST Request** | `[Verb][Entity]Request` | `OptimizeScheduleRequest`, `ValidateScheduleRequest` |
| **REST Response** | `[Verb][Entity]Response` | `OptimizeScheduleResponse`, `ValidateScheduleResponse` |
| **Application Command** | `[Verb][Entity]Command` | `SolveScheduleCommand`, `SimulateDisruptionCommand` |
| **Application Query** | `Get[Entity]Query` / `List[Entity]Query` | `GetScheduleQuery`, `ListScenariosQuery` |
| **Domain Result** | `[Entity]Result` / `[Entity]Report` | `ScheduleResult`, `ValidationReport` |
| **Domain Event** | `[Entity][PastTenseVerb]Event` | `ScheduleOptimizedEvent`, `DisruptionInjectedEvent` |
| **Scenario Spec** | `[Entity]Spec` | `TaskSpec`, `ResourceSpec`, `TransitionSpec` |
| **Repository Protocol** | `[Entity]Repository` | `ScheduleRepository`, `ScenarioRepository` |
| **Engine Protocol** | `[Functionality]Engine` / `Provider` | `OptimizationEngine`, `CalendarProvider` |
| **External Client** | `[System]Client` | `TemporalWorkflowClient`, `PanchangAPIClient` |

Banned vague names: `Data`, `Payload`, `Info`, `Item`, `Object`, `Record`, `ResultDto`.

---

# 6. Common Contracts

Shared foundational contracts prevent ad-hoc reinvention of identifiers, timestamps, pagination, and error representations.

## 6.1 Identifiers

Never use unconstrained, arbitrary strings for resource, task, or tenant identifiers.

```python
from typing import Annotated
import msgspec

# Identifiers must be alphanumeric, hyphen, or underscore between 1 and 64 characters
Identifier = Annotated[
    str,
    msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$"),
]

TaskId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ResourceId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ScheduleId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
ScenarioId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
TenantId = Annotated[str, msgspec.Meta(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")]
```

Using `Annotated` with `msgspec.Meta` provides **both** static type documentation for Mypy and strict runtime validation during deserialization.

## 6.2 Timestamps and Horizons

Combinatorial solvers operate on **discrete planning horizons** (integer ticks, usually representing minutes), whereas client systems communicate in **ISO 8601 wall-clock UTC datetimes**.

```python
from datetime import datetime
from ojas_ops.contracts.base import Contract, ValueObject


class HorizonContract(ValueObject):
    """Discrete planning horizon for combinatorial solvers."""

    start: int = 0
    end: int = 1440  # e.g. 1 day in minutes


class ScheduleTimeContext(Contract):
    """Bridge between wall-clock timestamps and solver horizon ticks."""

    reference_timestamp_utc: datetime
    tick_duration_seconds: int = 60  # 1 tick = 1 minute
    horizon_start_tick: int = 0
    horizon_end_tick: int = 1440
```

Rules:
- Wall-clock datetimes must always be timezone-aware UTC (`datetime.timezone.utc`).
- The reference mapping between integer tick `0` and wall-clock UTC must be explicitly declared.
- Naive datetimes without timezone information are rejected at the boundary.

## 6.3 Pagination for Operational Collections

Standardize cursor-based pagination for schedules, scenario runs, and task catalogs:

```python
class PaginationQuery(Contract):
    limit: Annotated[int, msgspec.Meta(ge=1, le=200)] = 50
    cursor: str | None = None


class PageInfo(ValueObject):
    has_next_page: bool
    next_cursor: str | None = None
    total_count: int | None = None


class PaginatedResponse[T](APIResponse):
    items: list[T]
    page_info: PageInfo
```

## 6.4 Standard Error Contract

Every Ojas Ops service returns errors conforming to an RFC 7807-inspired typed error contract:

```python
from enum import StrEnum
from ojas_ops.contracts.base import Contract, ValueObject


class ErrorCode(StrEnum):
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INFEASIBLE_CONSTRAINTS = "INFEASIBLE_CONSTRAINTS"
    SOLVER_TIMEOUT = "SOLVER_TIMEOUT"
    MODEL_INVALID = "MODEL_INVALID"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_OVERALLOCATED = "RESOURCE_OVERALLOCATED"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_SOLVER_ERROR = "INTERNAL_SOLVER_ERROR"


class ErrorDetail(ValueObject):
    field: str | None = None
    code: str
    message: str


class APIError(Contract):
    code: ErrorCode
    message: str
    details: list[ErrorDetail] = msgspec.field(default_factory=list)


class ErrorResponse(APIResponse):
    error: APIError
    request_id: str
    tenant_id: str | None = None
```

---

# 7. Behavioral Contracts with Protocol

Data structures define data shapes; `typing.Protocol` defines behavioral promises, abstracting solvers, storage, and calendar engines from application logic.

## 7.1 Optimization Engine Protocol

```python
from typing import Protocol, runtime_checkable
from ojas_ops.models import Horizon, ScheduleResult, Task, Resource
from ojas_ops.constraints import Constraint
from ojas_ops.objectives import Objective
from ojas_ops.solvers.config import SolveConfig


@runtime_checkable
class OptimizationEngine(Protocol):
    """Abstract solver bridge protocol."""

    def solve(
        self,
        tasks: list[Task],
        resources: list[Resource],
        constraints: list[Constraint],
        objectives: list[Objective],
        horizon: Horizon,
        config: SolveConfig | None = None,
    ) -> ScheduleResult:
        """Compile constraints and objectives to solver model, solve, and return result."""
        ...
```

Concrete implementations:
- `CPSatSolver`: Google OR-Tools CP-SAT solver backend.
- `MockOptimizationEngine`: Deterministic fixture engine for unit testing.
- `RemoteGrpcSolverClient`: Remote RPC solver bridge for offloading heavy compute.

## 7.2 Independent Schedule Validator Protocol

```python
@runtime_checkable
class ScheduleValidatorProtocol(Protocol):
    """Protocol for independent schedule feasibility verification."""

    def validate(
        self,
        tasks: list[Task],
        resources: list[Resource],
        constraints: list[Constraint],
        result: ScheduleResult,
        horizon: Horizon,
    ) -> ValidationReport:
        """Deterministically verify all constraints without invoking any solver."""
        ...
```

## 7.3 Calendar Provider Protocol

```python
@runtime_checkable
class CalendarProviderProtocol(Protocol):
    """Protocol for operational and cultural calendar blackout/target providers."""

    def get_blackout_windows(
        self,
        resource_id: str,
        horizon: Horizon,
    ) -> list[IntervalWindow]:
        """Return unavailable time windows (e.g. Rahu Kalam, maintenance, rest)."""
        ...

    def get_target_windows(
        self,
        task_id: str,
        horizon: Horizon,
    ) -> list[IntervalWindow]:
        """Return preferred or mandatory target windows (e.g. Shubh Muhurat)."""
        ...
```

## 7.4 Behavioral Invariants and Guarantees

Every implementation of an Ojas Ops protocol must satisfy documented mathematical invariants:

1. **Determinism:** If `config.random_seed` and input models are identical, `solve()` must return identical schedule assignments.
2. **Feasibility Invariant:** If `ScheduleResult.status == ScheduleStatus.OPTIMAL` or `FEASIBLE`, `ScheduleValidator.validate()` must return `report.is_valid == True` with zero `Severity.ERROR` violations.
3. **Non-destructive Simulation:** Simulating disruptions (`Simulator.simulate()`) must never mutate baseline schedule instances in place; it must return a fresh `SimulationResult`.

---

# 8. REST API Contracts

REST is the primary public HTTP interface for Ojas Ops services, documented strictly via OpenAPI 3.1.

## 8.1 Resource URL Taxonomy

```http
POST   /api/v1/schedules/optimize            # Trigger schedule optimization
GET    /api/v1/schedules/{schedule_id}       # Retrieve solved schedule & assignments
POST   /api/v1/schedules/{schedule_id}/validate # Run independent validation
POST   /api/v1/schedules/{schedule_id}/simulate # Simulate operational disruptions
DELETE /api/v1/schedules/{schedule_id}       # Cancel or delete schedule

POST   /api/v1/scenarios/run                 # Execute a scenario dataset against golden criteria
GET    /api/v1/scenarios/{scenario_id}       # Fetch scenario definition
GET    /api/v1/scenarios/{scenario_id}/benchmarks # Retrieve historical benchmarks
```

## 8.2 Comprehensive Endpoint Contract: Optimize Schedule

### Request Contract:

```python
from enum import StrEnum
from ojas_ops.contracts.base import APIRequest, APIResponse, Contract
from ojas_ops.models import Task, Resource, Horizon
from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus


class SolveStrategy(StrEnum):
    FAST = "fast"
    BALANCED = "balanced"
    DEEP_OPTIMAL = "deep_optimal"


class OptimizeScheduleRequest(APIRequest):
    tenant_id: str
    project_id: str
    tasks: list[Task]
    resources: list[Resource]
    horizon: Horizon
    strategy: SolveStrategy = SolveStrategy.BALANCED
    max_time_seconds: float = 30.0
    random_seed: int = 42
    enable_cultural_calendar: bool = False
```

### Response Contract:

```python
class OptimizeScheduleResponse(APIResponse):
    schedule_id: str
    status: ScheduleStatus
    makespan: int
    objective_value: float
    solve_time_seconds: float
    tasks_scheduled_count: int
    result: ScheduleResult
    validation_summary: str
```

### HTTP Wire Specification:

```http
POST /api/v1/schedules/optimize
Host: ops.ojas.vc
Authorization: Bearer <jwt-token>
Idempotency-Key: 7b848c08-fc18-425b-9d48-356a5c1a79d2
Content-Type: application/json
```

```json
{
  "tenant_id": "ten-manufacturing-01",
  "project_id": "aerospace-jobshop-q4",
  "tasks": [
    {
      "id": "cnc-mill-job-1",
      "duration": 120,
      "name": "Milling Titanium Turbine Blade",
      "required_resources": ["workstation-cnc-01"],
      "cost_minor": 250000
    }
  ],
  "resources": [
    {
      "id": "workstation-cnc-01",
      "capacity": 1,
      "resource_type": "machine"
    }
  ],
  "horizon": {
    "start": 0,
    "end": 1440
  },
  "strategy": "balanced",
  "max_time_seconds": 15.0,
  "random_seed": 42
}
```

---

# 9. RPC Contracts (gRPC & Protocol Buffers)

When high-throughput, sub-millisecond serialization, or cross-language communication with external solver clusters is required, gRPC with Protocol Buffers v3 is used.

## 9.1 Protobuf Contract Specification

```protobuf
syntax = "proto3";

package ojas.ops.v1;

option go_package = "github.com/ojas-vc/ojas-ops/gen/go/v1;ops_v1";
option java_package = "vc.ojas.ops.v1";

service OptimizationService {
  rpc OptimizeSchedule(OptimizeScheduleRequest) returns (OptimizeScheduleResponse);
  rpc ValidateSchedule(ValidateScheduleRequest) returns (ValidateScheduleResponse);
  rpc StreamOptimizationProgress(OptimizeScheduleRequest) returns (stream OptimizationProgressUpdate);
}

message TaskMessage {
  string id = 1;
  int32 duration = 2;
  string name = 3;
  repeated string required_resources = 4;
  repeated string dependencies = 5;
  int64 cost_minor = 6;
  int32 fixed_start = 7;
}

message ResourceMessage {
  string id = 1;
  int32 capacity = 2;
  string resource_type = 3;
  int64 cost_per_time_unit_minor = 4;
}

message HorizonMessage {
  int32 start = 1;
  int32 end = 2;
}

message OptimizeScheduleRequest {
  string tenant_id = 1;
  string project_id = 2;
  repeated TaskMessage tasks = 3;
  repeated ResourceMessage resources = 4;
  HorizonMessage horizon = 5;
  double max_time_seconds = 6;
  int32 random_seed = 7;
}

message ScheduledTaskMessage {
  string task_id = 1;
  int32 start = 2;
  int32 end = 3;
  int32 duration = 4;
  repeated string assigned_resources = 5;
}

message OptimizeScheduleResponse {
  string schedule_id = 1;
  string status = 2;
  int32 makespan = 3;
  double objective_value = 4;
  double solve_time_seconds = 5;
  map<string, ScheduledTaskMessage> tasks = 6;
}

message OptimizationProgressUpdate {
  int32 branches_explored = 1;
  int32 conflicts = 2;
  double best_objective_bound = 3;
  double current_objective = 4;
  double elapsed_seconds = 5;
}
```

## 9.2 Mapping Between msgspec and Protobuf

Keep domain logic isolated to `msgspec.Struct`. Implement explicit bidirectional converters in transport adapters:

```python
def task_to_proto(task: Task) -> TaskMessage:
    return TaskMessage(
        id=task.id,
        duration=task.duration,
        name=task.name,
        required_resources=task.required_resources,
        dependencies=task.dependencies,
        cost_minor=int(task.cost * 100),  # Scaled to integer minor units
    )


def proto_to_task(msg: TaskMessage) -> Task:
    return Task(
        id=msg.id,
        duration=msg.duration,
        name=msg.name,
        required_resources=list(msg.required_resources),
        dependencies=list(msg.dependencies),
        cost=msg.cost_minor / 100.0,
    )
```

---

# 10. Event-Driven Contracts

Ojas Ops integrates asynchronously with the rest of the Ojas platform via strictly typed domain events.

## 10.1 Standard Event Envelope

```python
from datetime import datetime
from uuid import UUID
from typing import Literal
from ojas_ops.contracts.base import Contract, DomainEventContract


class EventMetadata(DomainEventContract):
    event_id: UUID
    event_type: str
    event_version: int
    tenant_id: str
    correlation_id: str
    causation_id: str | None = None
    occurred_at: datetime
    published_at: datetime | None = None
```

## 10.2 Strongly Typed Event Payloads

```python
class ScheduleOptimizedPayload(Contract, frozen=True):
    schedule_id: str
    project_id: str
    tenant_id: str
    status: str  # "optimal", "feasible", "infeasible"
    makespan: int
    objective_value: float
    tasks_count: int
    solve_time_seconds: float


class ScheduleOptimizedEvent(
    DomainEventContract,
    tag="schedule.optimized",
    tag_field="event_type",
):
    metadata: EventMetadata
    data: ScheduleOptimizedPayload


class DisruptionInjectedPayload(Contract, frozen=True):
    schedule_id: str
    disrupted_task_id: str | None = None
    delay_minutes: int = 0
    blackout_resource_id: str | None = None
    blackout_start: int | None = None
    blackout_end: int | None = None


class DisruptionInjectedEvent(
    DomainEventContract,
    tag="schedule.disruption_injected",
    tag_field="event_type",
):
    metadata: EventMetadata
    data: DisruptionInjectedPayload
```

## 10.3 Transactional Outbox Pattern for Schedule Events

When persisting schedules to an ACID store, never emit events directly over the network inside the database transaction. Always write the event to an outbox table in the same transaction to guarantee at-least-once delivery:

1. Commit schedule state + outbox event in one transaction.
2. Background outbox relayer publishes event to Kafka/RabbitMQ/Redis Stream.
3. Consumers process events idempotently using `metadata.event_id`.

---

# 11. Background Jobs and Temporal Contracts

Complex combinatorial optimization runs (e.g. 5,000-task aerospace job shops or monthly hospital ward rostering) can exceed HTTP timeout boundaries. These long-running operations are orchestrated via **Temporal workflows**.

## 11.1 Workflow Contract Definition

```python
from temporalio import workflow
from temporalio import activity
from datetime import timedelta
from ojas_ops.contracts.base import Contract
from ojas_ops.models import Horizon, ScheduleResult, Task, Resource
from ojas_ops.validation import ValidationReport


class RunOptimizationWorkflowInput(Contract):
    tenant_id: str
    scenario_id: str
    tasks: list[Task]
    resources: list[Resource]
    horizon: Horizon
    timeout_seconds: float = 300.0


class RunOptimizationWorkflowResult(Contract):
    schedule_id: str
    is_feasible: bool
    makespan: int
    validation_errors_count: int
    schedule_result: ScheduleResult
```

## 11.2 Activity Contracts and Determinism Rules

```python
@activity.defn
async def solve_cpsat_activity(
    input_data: RunOptimizationWorkflowInput,
) -> ScheduleResult:
    """Execute CP-SAT solve inside an isolated, resource-governed activity."""
    from ojas_ops.solvers.cp_sat import CPSatSolver
    from ojas_ops.solvers.config import SolveConfig

    solver = CPSatSolver()
    config = SolveConfig(max_time_in_seconds=input_data.timeout_seconds)
    return solver.solve(
        tasks=input_data.tasks,
        resources=input_data.resources,
        constraints=[],
        objectives=[],
        horizon=input_data.horizon,
        config=config,
    )


@activity.defn
async def validate_schedule_activity(
    result: ScheduleResult,
) -> ValidationReport:
    """Run independent deterministic validation on the solved schedule."""
    from ojas_ops.validation.validator import ScheduleValidator

    validator = ScheduleValidator()
    return validator.validate(
        tasks=[],
        resources=[],
        constraints=[],
        result=result,
        horizon=Horizon(0, result.makespan),
    )


@workflow.defn
class ScheduleOptimizationWorkflow:
    @workflow.run
    async def run(
        self,
        input_data: RunOptimizationWorkflowInput,
    ) -> RunOptimizationWorkflowResult:
        # Step 1: Solve combinatorial schedule
        schedule_result = await workflow.execute_activity(
            solve_cpsat_activity,
            input_data,
            start_to_close_timeout=timedelta(seconds=input_data.timeout_seconds + 30),
            heartbeat_timeout=timedelta(seconds=15),
        )

        # Step 2: Validate schedule independently
        validation_report = await workflow.execute_activity(
            validate_schedule_activity,
            schedule_result,
            start_to_close_timeout=timedelta(seconds=30),
        )

        return RunOptimizationWorkflowResult(
            schedule_id=f"sched-{input_data.scenario_id}",
            is_feasible=schedule_result.is_feasible,
            makespan=schedule_result.makespan,
            validation_errors_count=validation_report.error_count,
            schedule_result=schedule_result,
        )
```

> [!CAUTION]
> **Temporal Workflow Determinism Rule:** Workflow code must never call `datetime.now()`, generate random numbers, or access network/database directly. All I/O and heavy solver computations must be isolated inside activities.

---

# 12. Strict Typing Rules

Enforce these strict typing rules across the entire Ojas Ops codebase.

## 12.1 Prohibited Anti-Patterns

The following patterns are banned repository-wide:

```python
# BANNED: Untyped dictionary
def solve_schedule(payload: dict): ...


# BANNED: Any types
def process_tasks(tasks: list[Any]) -> Any: ...


# BANNED: Loose keyword arguments
def add_constraint(**kwargs): ...


# BANNED: Stringly-typed status
def update_status(status: str): ...  # Must use ScheduleStatus enum


# BANNED: Raw float for monetary costs/rates in solvers
cost_per_hour: float = 120.50  # Must be integer minor units: 12050
```

## 12.2 Preferred Patterns: Tagged Unions for Constraints & Objectives

Polymorphic operational constraints and objectives must be modeled as **tagged unions** in `msgspec`:

```python
import msgspec
from typing import Literal


class BaseConstraintContract(msgspec.Struct, tag=True, tag_field="constraint_type"):
    pass


class PrecedenceConstraintContract(BaseConstraintContract, tag="precedence"):
    predecessor_id: str
    successor_id: str
    dependency_type: Literal["FS", "SS", "FF", "SF"] = "FS"
    min_lag: int = 0
    max_lag: int | None = None


class NoOverlapConstraintContract(BaseConstraintContract, tag="no_overlap"):
    resource_id: str


class CumulativeConstraintContract(BaseConstraintContract, tag="cumulative"):
    resource_id: str
    capacity: int


class SetupMatrixConstraintContract(BaseConstraintContract, tag="setup_matrix"):
    resource_id: str
    transition_matrix: dict[str, int]


# Exhaustive tagged union
ConstraintContract = (
    PrecedenceConstraintContract
    | NoOverlapConstraintContract
    | CumulativeConstraintContract
    | SetupMatrixConstraintContract
)
```

When decoded with `msgspec.json.decode(payload, type=ConstraintContract)`, `msgspec` automatically inspects `constraint_type` and instantiates the exact concrete typed struct.

## 12.3 Enums vs Literals

- Use `enum.StrEnum` for core reusable domain types (`ScheduleStatus`, `ResourceType`, `TaskPriority`, `DependencyType`, `Severity`).
- Use `typing.Literal` for closed sets of string tags within localized wire DTOs (`Literal["fast", "balanced", "deep_optimal"]`).

---

# 13. Security and Multi-Tenant Isolation

Ojas Ops is engineered for secure, multi-tenant deployment.

## 13.1 Multi-Tenant Context Invariants

Every operational request must carry a cryptographically verified `RequestContext`:

```python
class RequestContext(Contract):
    tenant_id: str
    actor_id: str
    correlation_id: str
    roles: list[str] = msgspec.field(default_factory=list)
```

### Security Rules:
1. **Never trust `tenant_id` from client payloads:** Derive and verify `tenant_id` from trusted JWT claims or platform auth middleware (`ojas_tenants.http`).
2. **Strict Data Isolation:** Every query, schedule retrieval, and scenario run must filter strictly by `tenant_id`.
3. **Solver CPU & Memory Quotas:** Prevent denial-of-service or solver starvation by enforcing per-tenant CPU limits (`worker_threads <= 8`) and timeout bounds (`max_time_in_seconds <= 300`).

---

# 14. Operational Contracts (Solvers & Concurrency)

## 14.1 Solver Execution Parameters

```python
class SolveConfig(Contract):
    """Operational parameters passed to Google OR-Tools CP-SAT."""

    max_time_in_seconds: float = 30.0
    relative_gap_limit: float = 0.01  # 1.0% optimality gap
    num_workers: int = 8
    random_seed: int = 42
    log_search_progress: bool = False
    enable_warm_start: bool = True
```

## 14.2 Idempotency and Determinism

- Optimization endpoints must accept an `Idempotency-Key` header.
- Solvers must set `random_seed` explicitly. The same seed, tasks, resources, and constraints will produce identical mathematical schedules.

## 14.3 Optimistic Concurrency on Schedules

Active schedules undergo human adjustment and reactive rescheduling. Prevent race conditions using version-based optimistic locking:

```http
GET /api/v1/schedules/sched-123
ETag: W/"v4-hash-a1b2c3d4"
```

```http
PATCH /api/v1/schedules/sched-123
If-Match: W/"v4-hash-a1b2c3d4"
```

If another planner or automated agent has modified the schedule, return `412 Precondition Failed`.

---

# 15. Contract Versioning and Evolution

Contracts are consumed by frontends, workers, and partner systems. Follow semantic versioning strictly:

- **MAJOR (v2.0):** Breaking changes (field deletion, renaming, type changes, semantic shifts).
- **MINOR (v1.1):** Backward-compatible additions (new optional fields with defaults, new endpoints).
- **PATCH (v1.0.1):** Bug fixes, documentation updates, constraint metadata refinements.

### Expand-and-Contract Migration Pattern:
1. **Expand:** Add new field `cost_minor: int` alongside deprecated `cost: float`.
2. **Dual-Support:** Populate both during a transition release window.
3. **Migrate:** Update all clients and scenarios to consume `cost_minor`.
4. **Contract:** Remove deprecated `cost` in the next major version.

---

# 16. Contract Testing and Quality Gates

Ojas Ops enforces a 4-level automated contract testing hierarchy:

```text
Level 1: msgspec Schema Validation & Type Safety
Level 2: Behavioral Contract & Protocol Verification
Level 3: Provider-Consumer Integration Testing
Level 4: Declarative Scenarios & Golden Benchmark Regression
```

## 16.1 Level 4: Golden Scenario Assertions

Ojas Ops provides built-in scenario assertion testing (`test_scenarios.py`):

```python
from ojas_ops.scenarios import load_scenario, verify_expected, run_scenario


def test_manufacturing_golden_scenario():
    scenario = load_scenario("examples/manufacturing/data/industrial_jobshop.json")
    run_result = run_scenario(scenario)

    assert run_result.schedule_result.is_feasible
    # Deterministic verification against embedded golden bounds
    verification = verify_expected(scenario, run_result.schedule_result)
    assert verification["all_passed"], f"Golden assertions failed: {verification}"
```

## 16.2 Property-Based Testing with Hypothesis

Verify mathematical invariants across randomly generated task graphs:

```python
from hypothesis import given, strategies as st
from ojas_ops import Scheduler


@given(
    durations=st.lists(st.integers(min_value=1, max_value=120), min_size=2, max_size=10),
)
def test_precedence_invariants(durations):
    scheduler = Scheduler()
    scheduler.add_resource("worker", capacity=1)

    prev_id = None
    for idx, dur in enumerate(durations):
        t_id = f"task_{idx}"
        deps = [prev_id] if prev_id else []
        scheduler.add_task(id=t_id, duration=dur, required_resources=["worker"], dependencies=deps)
        prev_id = t_id

    result = scheduler.solve()
    assert result.is_feasible

    # Invariant: Each task must start after its predecessor finishes
    for idx in range(1, len(durations)):
        t_curr = result.get_task(f"task_{idx}")
        t_prev = result.get_task(f"task_{idx - 1}")
        assert t_curr.start >= t_prev.end
```

## 16.3 CI/CD Quality Gates

Every pull request must pass the automated Makefile quality gates:

```bash
make check            # [1/3] Ruff format check, [2/3] Ruff lint, [3/3] Mypy type analysis
make test-fast        # Pytest test suite across all subsystems
make test-scenarios   # Golden benchmark assertions across all 8 example domains
```

---

# 17. Documentation Standards & Cross-References

Every public model, constraint, solver, and adapter must be thoroughly documented in the documentation suite:

| Document | Primary Focus |
|---|---|
| [architecture.md](architecture.md) | High-level system topology, CP-SAT translation, and deterministic verification. |
| [api.md](api.md) | Fluent `Scheduler` orchestrator reference, scenario loaders, and runners. |
| [models.md](models.md) | `Task`, `Resource`, `Horizon`, `IntervalWindow`, `TimeWindow`, `ScheduleResult`. |
| [calendars.md](calendars.md) | Standard business operational shifts and Hindu Panchang cultural calendars. |
| [constraints.md](constraints.md) | Precedence (FS/SS/FF/SF), cumulative, no-overlap, setup matrices, windows. |
| [objectives.md](objectives.md) | Makespan, tardiness, financial cost, idle time, baseline schedule stability. |
| [solvers.md](solvers.md) | Google OR-Tools CP-SAT compilation, candidate resource pools, and tuning. |
| [validation.md](validation.md) | Independent feasibility and constraint verification without solver dependencies. |
| [simulation.md](simulation.md) | Disruption modeling, what-if impact analysis, and reactive rescheduling. |
| [scenarios.md](scenarios.md) | Data-driven scenario schemas, golden assertions, CSV loading, and generators. |
| [adapters.md](adapters.md) | 6 ready-to-use industry adapters (film, manufacturing, health, academic, events, marketing). |

---

# 18. API & Contract Design Workflow

When introducing new models, adapters, or endpoints to Ojas Ops, follow this 10-step workflow:

1. **Define the Use Case:** Clarify domain constraints (e.g. film turnaround rest vs nurse overtime).
2. **Model Mathematical Primitives:** Map requirements to Tasks, Resources, Intervals, and Capacities.
3. **Author Canonical `msgspec.Struct`:** Define strictly typed schemas with `forbid_unknown_fields=True`.
4. **Enforce Integer Scaling Invariant:** Ensure all monetary rates, costs, and penalties are integer minor units.
5. **Declare Behavioral Protocols:** Define service interfaces with `typing.Protocol`.
6. **Implement Independent Validation Check:** Add verification rules to `ScheduleValidator`.
7. **Write Unit & Property Tests:** Test schema decoding, error cases, and Hypothesis invariants.
8. **Add Declarative Scenario & Golden Dataset:** Create reproducible JSON dataset in `examples/*/data/`.
9. **Implement Solver Compilation:** Bridge model to Google OR-Tools CP-SAT in `solvers/cp_sat.py`.
10. **Pass CI Gates:** Run `make check` (Ruff + Mypy) and verify 100% test pass rate.

---

# 19. Contract Design Review Checklist

Use this checklist during architecture reviews and pull requests:

### Data Structure & Strict Typing
- [ ] Model inherits from `msgspec.Struct` with `kw_only=True` and `forbid_unknown_fields=True`.
- [ ] No untyped dictionaries (`dict[str, Any]`) or unconstrained `Any` types.
- [ ] Costs, monetary rates, and penalty weights use integer minor units (no raw floats in solver models).
- [ ] Identifiers use validated types (`Annotated[str, msgspec.Meta(pattern=...)]`).
- [ ] Polymorphic models use tagged unions (`tag=True`, `tag_field="..."`).
- [ ] Unknown fields are strictly rejected at boundaries.

### Mathematical & Behavioral Correctness
- [ ] Concrete engine implements the corresponding `typing.Protocol`.
- [ ] Determinism is guaranteed via parameterized random seeds.
- [ ] Feasibility is independently verified by `ScheduleValidator`.
- [ ] What-if simulation does not mutate baseline schedule state in place.

### Interoperability & Transport
- [ ] External inputs decode via `msgspec.json.Decoder(strict=True)`.
- [ ] REST endpoints specify OpenAPI 3.1 request/response schemas.
- [ ] gRPC messages mirror domain contracts with explicit conversion helpers.
- [ ] Errors conform to the standard RFC 7807-inspired `ErrorResponse` contract.

### Testing & Verification
- [ ] Golden scenario dataset created with embedded `ExpectedResult` assertions.
- [ ] Property-based tests written with Hypothesis.
- [ ] `make check` (Ruff formatting + linting + Mypy typecheck) passes with zero errors.

---

# 20. Reference Architecture

```text
                               OJAS OPS ARCHITECTURE
                                         │
                                CONTRACTS FOUNDATION
                                         │
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
           DATA TYPES                BEHAVIOR                  SCHEMAS
        msgspec.Struct           typing.Protocol             OpenAPI 3.1
     (Tasks, Resources,       (OptimizationEngine,           Protobuf v3
      Schedules, Reports)      Validator, Calendar)            AsyncAPI
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         ▼
                                 APPLICATION LAYER
                                         │
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
           REST / ASGI                 RPC                    TEMPORAL
           django-bolt                 gRPC                   Workflows &
           FastAPI                  Protobuf v3               Activities
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         ▼
                                  DOMAIN ENGINE
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  Fluent Scheduler              Domain Adapters                  Scenario Simulator
 (Orchestrator)                 - Film Production                - Disruption Modeling
                                - Manufacturing Job Shop         - Impact Analysis
                                - Healthcare Rostering           - Stability Objectives
                                - Academic Timetables
                                - Conference Run-Sheets
                                - Campaign Flighting
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                           SOLVERS & VALIDATION CORE
                                         │
                ┌────────────────────────┴────────────────────────┐
                ▼                                                 ▼
     Google OR-Tools CP-SAT                             Independent Validator
   (Integer Constraint Engine)                      (Solver-Agnostic Verification)
```

---

# 21. Additional Architectural Decisions

| Decision | Standard | Rationale |
|---|---|---|
| **Contract Ownership** | Each subsystem owns its domain contracts | Prevents bloated monolithic contract files |
| **Shared Primitives** | Only true primitives in common (`TenantId`, `Horizon`) | Avoids the shared-model anti-pattern |
| **Integer Scaling** | All solver costs/weights in integer minor units | Required by Google OR-Tools CP-SAT integer engine |
| **Validation Seam** | Deterministic independent validator | Essential for audits, regulations, and golden tests |
| **Boundary Decoding** | Strict decoding with `strict=True` | Catches malformed data before hitting solver algorithms |
| **Cross-Module Calls** | Via declared Protocols or typed DTOs | Enables modular monolith or distributed microservices |

---

# 22. Recommended Implementation & Conversion Roadmap

To complete the strictly typed conversion across Ojas Ops, execute in phased milestones:

| Phase | Deliverable | Priority | Status |
|---|---|---|---|
| **Phase 1** | Strictly typed `msgspec.Struct` core domain models (`models/`) | Critical | Complete |
| **Phase 2** | Data-driven scenarios with embedded golden assertions (`scenarios/`) | Critical | Complete |
| **Phase 3** | Independent deterministic validator engine (`validation/`) | Critical | Complete |
| **Phase 4** | CP-SAT solver compilation with circuit transitions & blackouts (`solvers/`) | Critical | Complete |
| **Phase 5** | Convert floating-point costs to integer minor units across models & objectives | High | Ready for code migration |
| **Phase 6** | Tagged unions for polymorphic constraints & objectives | High | Ready for code migration |
| **Phase 7** | Modular wire contracts (`ojas_ops.contracts`) & OpenAPI 3.1 / Protobuf schemas | High | Planned |
| **Phase 8** | gRPC Protobuf definitions & Temporal workflow integration | Medium | Planned |

---

# 23. Architectural Decision Records (ADRs)

| ADR | Title | Decision Summary |
|---|---|---|
| **ADR-001** | Contract-First Development | Define strictly typed data and behavioral contracts before implementing engines or APIs |
| **ADR-002** | msgspec as Data Contract Standard | Standardize on `msgspec.Struct` for high-performance typed models and microsecond serialization |
| **ADR-003** | Google OR-Tools CP-SAT as Core Solver | Adopt CP-SAT for deterministic combinatorial optimization instead of probabilistic AI generation |
| **ADR-004** | Pure-Integer Solver Invariant | Scale all monetary rates, costs, and weights to integer minor units to eliminate float rounding errors |
| **ADR-005** | Independent Validator Seam | Implement `ScheduleValidator` to audit schedule feasibility deterministically without solver state |
| **ADR-006** | Data-Driven Scenarios & Golden Assertions | Embed expected metrics in declarative scenario datasets for reproducible regression benchmarking |
| **ADR-007** | typing.Protocol for Behavioral Interfaces | Decouple solver backends, calendar providers, and storage repositories behind Protocols |
| **ADR-008** | Pluggable Operational & Cultural Calendars | Support both standard business shifts and Hindu Panchang cultural windows (Muhurats/Rahu Kalam) |
| **ADR-009** | Tagged Unions for Polymorphism | Use `msgspec` tagged unions (`tag_field`) for polymorphic constraints, objectives, and events |
| **ADR-010** | Strict Decoding at Untrusted Boundaries | Mandate `Decoder(strict=True)` to reject unvalidated or coerced types at API boundaries |
| **ADR-011** | OpenAPI 3.1 & Protobuf v3 Transports | Expose REST endpoints via OpenAPI 3.1 and high-throughput RPC via Protobuf v3 |
| **ADR-012** | Temporal for Long-Running Solves | Orchestrate multi-minute optimization jobs through stateful, durable Temporal workflows |

---

# 24. Final Architectural Principles

The Ojas Ops engineering philosophy:

> **Everything is a contract.**
> No implicit interfaces. No undocumented assumptions. No untyped business boundaries. No floating-point solver rounding.

| Concern | Authoritative Standard |
|---|---|
| **Data Models** | `msgspec.Struct` (`kw_only=True`, `forbid_unknown_fields=True`) |
| **Mathematical Solver** | Google OR-Tools CP-SAT (pure-integer constraint programming) |
| **Behavioral Interfaces** | `typing.Protocol` |
| **REST APIs** | OpenAPI 3.1 |
| **RPC & Interoperability** | gRPC + Protocol Buffers v3 |
| **Domain Events** | Strictly typed event envelopes / AsyncAPI |
| **Long-Running Workflows** | Temporal workflow & activity definitions |
| **Boundary Validation** | `msgspec.json.Decoder(strict=True)` |
| **Correctness & Auditing** | Independent deterministic `ScheduleValidator` |
| **Regression Testing** | Data-driven scenarios with embedded golden assertions |
| **Quality Enforcement** | `make check` (Ruff formatting, Ruff linting, Mypy type analysis) |

This standard guarantees that Ojas Ops operates with mathematical precision, microsecond serialization performance, and absolute type safety.
