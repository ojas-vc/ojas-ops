# Typed Domain Models

All core data structures in Ojas Ops are implemented using `msgspec.Struct`, providing high performance, compact memory footprint, and microsecond-level JSON serialization.

Import root:

```python
from ojas_ops.models import (
    IntervalWindow,
    TimeWindow,
    Horizon,
    Task,
    TaskPriority,
    DependencyType,
    TaskDependency,
    ResourceRequirement,
    Resource,
    ResourceType,
    CalendarEvent,
    CalendarKind,
    ScheduleResult,
    ScheduledTask,
    ResourceAssignment,
    ScheduleStatus,
)
```

---

## 1. Time & Window Primitives

### `IntervalWindow`

Represents a continuous interval $[start, end)$ on integer coordinates.

```python
class IntervalWindow(msgspec.Struct, kw_only=True):
    start: int
    end: int
    label: str = ""
    hard: bool = True
```

**Methods:**

- `duration -> int`: Returns `end - start`.
- `contains(point: int) -> bool`: Checks if point is within $[start, end)$.
- `overlaps(other_start: int, other_end: int) -> bool`: Returns `True` if intervals overlap.
- `encloses(other_start: int, other_end: int) -> bool`: Checks if $[other\_start, other\_end]$ is completely inside.

### `TimeWindow`

Defines operational boundaries and deadlines for task execution.

```python
class TimeWindow(msgspec.Struct, kw_only=True):
    earliest_start: int | None = None
    latest_start: int | None = None
    earliest_end: int | None = None
    latest_end: int | None = None
    deadline: int | None = None
```

### `Horizon`

Defines the planning temporal scope and discretization granularity.

```python
class Horizon(msgspec.Struct, kw_only=True):
    start: int = 0
    end: int = 1440
    granularity: int = 1  # 1 minute, 15 minutes, 1 hour
```

---

## 2. Tasks & Activities

### `Task`

A schedulable unit of work.

```python
class Task(msgspec.Struct, kw_only=True):
    id: str
    duration: int
    name: str = ""
    time_window: TimeWindow | None = None
    required_resources: list[str] = []
    resource_requirements: list[ResourceRequirement] = []
    dependencies: list[str] = []
    priority: TaskPriority = TaskPriority.NORMAL
    fixed_start: int | None = None
    cost: float = 0.0
    metadata: dict[str, str] = {}
```

### `TaskPriority`

```python
class TaskPriority(StrEnum):
    LOW = "low"  # Weight = 1
    NORMAL = "normal"  # Weight = 2
    HIGH = "high"  # Weight = 5
    CRITICAL = "critical"  # Weight = 10
```

### `DependencyType`

```python
class DependencyType(StrEnum):
    FS = "finish_to_start"  # Pred ends before Succ starts
    SS = "start_to_start"  # Pred starts before Succ starts
    FF = "finish_to_finish"  # Pred ends before Succ ends
    SF = "start_to_finish"  # Pred starts before Succ ends
```

### `ResourceRequirement`

Specifies resource demands, supporting alternative candidate pools:

```python
class ResourceRequirement(msgspec.Struct, kw_only=True):
    resource_id: str
    capacity: int = 1
    candidate_pool: list[str] = []  # Solver will pick 1 from pool
```

---

## 3. Resources

### `Resource`

Represents an entity required to execute tasks (people, machines, locations).

```python
class Resource(msgspec.Struct, kw_only=True):
    id: str
    name: str = ""
    capacity: int = 1
    resource_type: ResourceType = ResourceType.MACHINE
    cost_per_time_unit: float = 0.0
    overtime_cost_per_time_unit: float = 0.0
    regular_capacity_limit: int | None = None
    skills: list[str] = []
    blackout_windows: list[IntervalWindow] = []
    metadata: dict[str, str] = {}
```

### `ResourceType`

```python
class ResourceType(StrEnum):
    PERSON = "person"
    MACHINE = "machine"
    LOCATION = "location"
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    CHANNEL = "channel"
```

---

## 4. Scheduling Outcomes & Results

### `ScheduleResult`

Comprehensive result returned by solver execution.

```python
class ScheduleResult(msgspec.Struct, kw_only=True):
    status: ScheduleStatus
    objective_value: float = 0.0
    tasks: dict[str, ScheduledTask] = {}
    resources: dict[str, ResourceAssignment] = {}
    makespan: int = 0
    solve_time_seconds: float = 0.0
    wall_time: float = 0.0
    metadata: dict[str, str] = {}

    @property
    def is_feasible(self) -> bool:
        return self.status in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE)
```

### `ScheduledTask`

```python
class ScheduledTask(msgspec.Struct, kw_only=True):
    task_id: str
    start: int
    end: int
    duration: int
    assigned_resources: list[str] = []
    is_delayed: bool = False
    metadata: dict[str, str] = {}
```

### `ResourceAssignment`

```python
class ResourceAssignment(msgspec.Struct, kw_only=True):
    resource_id: str
    task_ids: list[str] = []
    total_utilized_time: int = 0
    idle_time: int = 0
    overtime: int = 0
```
