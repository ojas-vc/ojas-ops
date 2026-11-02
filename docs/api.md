# Scheduler API Reference

The `Scheduler` class (`ojas_ops.scheduling.Scheduler`) provides the primary fluent interface for modeling, optimizing, validating, and simulating operational schedules.

```python
from ojas_ops import Scheduler

scheduler = Scheduler()
```

---

## 1. Class: `Scheduler`

### Constructor

```python
Scheduler(
    *,
    horizon: Horizon | None = None,
    solver_config: SolverConfig | None = None,
)
```

- **`horizon`** _(optional)_: Sets default temporal boundary and discretization units. If omitted, calculated dynamically.
- **`solver_config`** _(optional)_: Configures timeout, CPU worker count, and random seed.

---

## 2. Resource Management

### `add_resource()`

Registers an operational entity (person, machine, facility, equipment, channel) capable of executing tasks.

```python
scheduler.add_resource(
    id: str,
    *,
    name: str = "",
    capacity: int = 1,
    resource_type: ResourceType = ResourceType.MACHINE,
    cost_per_time_unit: float = 0.0,
    regular_capacity_limit: int | None = None,
    skills: list[str] | None = None,
    blackout_windows: list[IntervalWindow] | None = None,
    metadata: dict[str, str] | None = None,
) -> Resource
```

**Parameters:**

- `id` _(str)_: Unique identifier for the resource.
- `capacity` _(int, default=1)_: Maximum concurrent tasks. If `capacity == 1`, disjunctive non-overlapping is automatically applied. If `capacity > 1`, cumulative resource scheduling is applied.
- `resource_type` _(ResourceType)_: Category (`PERSON`, `MACHINE`, `LOCATION`, `EQUIPMENT`, `FACILITY`, `CHANNEL`).
- `cost_per_time_unit` _(float)_: Monetary cost per minute/hour of active utilization.
- `regular_capacity_limit` _(int | None)_: Threshold beyond which overtime is calculated.
- `skills` _(list[str])_: Capabilities for candidate-pool matching in workforce problems.
- `blackout_windows` _(list[IntervalWindow])_: Resource-specific maintenance or leave intervals.

---

## 3. Task Management

### `add_task()`

Registers a schedulable activity.

```python
scheduler.add_task(
    id: str,
    *,
    duration: int,
    name: str = "",
    required_resources: list[str] | None = None,
    resource_requirements: list[ResourceRequirement] | None = None,
    dependencies: list[str] | None = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    time_window: TimeWindow | None = None,
    fixed_start: int | None = None,
    cost: float = 0.0,
    metadata: dict[str, str] | None = None,
) -> Task
```

**Parameters:**

- `id` _(str)_: Unique task identifier.
- `duration` _(int)_: Work duration in discrete integer units (minutes, hours). Must be $\ge 0$.
- `required_resources` _(list[str])_: List of resource IDs that must be allocated concurrently.
- `resource_requirements` _(list[ResourceRequirement])_: Advanced multi-resource demands or candidate pool choices (e.g. choose 1 of 5 qualified technicians).
- `dependencies` _(list[str])_: Predecessor task IDs (Finish-to-Start).
- `priority` _(TaskPriority)_: Importance level (`LOW`, `NORMAL`, `HIGH`, `CRITICAL`).
- `time_window` _(TimeWindow | None)_: Bounding window (`earliest_start`, `latest_end`, `deadline`).
- `fixed_start` _(int | None)_: Pins the task to an exact start time (e.g., keynote, ritual).

---

## 4. Constraints Configuration

### `add_dependency()`

Creates explicit precedence with lag between two tasks.

```python
scheduler.add_dependency(
    predecessor_id: str,
    successor_id: str,
    *,
    dependency_type: DependencyType = DependencyType.FS,
    min_lag: int = 0,
    max_lag: int | None = None,
) -> PrecedenceConstraint
```

- `dependency_type`: `FS` (Finish-to-Start), `SS` (Start-to-Start), `FF` (Finish-to-Finish), `SF` (Start-to-Finish).
- `min_lag`: Minimum buffer required between task milestones.
- `max_lag`: Maximum allowable gap (e.g., concrete curing or process freshness).

### `add_blackout_window()`

Restricts tasks or resources from executing during an interval.

```python
scheduler.add_blackout_window(
    *,
    window: IntervalWindow,
    resource_id: str | None = None,
    task_id: str | None = None,
) -> BlackoutWindowConstraint
```

### `add_target_window()`

Requires a task to execute within an allowed/auspicious window.

```python
scheduler.add_target_window(
    *,
    task_id: str,
    window: IntervalWindow,
    hard: bool = True,
) -> TargetWindowConstraint
```

### `add_transition_matrix()`

Enforces sequence-dependent setup times or turnaround buffers between tasks on a resource.

```python
scheduler.add_transition_matrix(
    *,
    resource_id: str,
    transition_matrix: dict[tuple[str, str], int],
    default_buffer: int = 0,
) -> TransitionConstraint
```

### `add_min_rest()`

Enforces minimum rest/recovery interval between consecutive tasks on a resource (e.g. nurse shifts).

```python
scheduler.add_min_rest(resource_id: str, min_rest: int) -> MinRestConstraint
```

### `add_max_workload()`

Limits cumulative working hours assigned to a resource over the horizon.

```python
scheduler.add_max_workload(resource_id: str, max_duration: int) -> MaxWorkloadConstraint
```

### `add_calendar()`

Attaches a calendar provider (e.g., `StandardCalendarProvider`, `CulturalCalendarProvider`).

```python
scheduler.add_calendar(calendar: CalendarProvider) -> None
```

---

## 5. Optimization & Solving

### `minimize()`

Sets the optimization objective.

```python
scheduler.minimize(objective_name: str | Objective, **kwargs) -> None
```

Supported string identifiers:

- `"makespan"`: Minimize overall completion time.
- `"cost"`: Minimize resource hourly costs + overtime + task costs.
- `"idle_time"`: Minimize gap dead-time between tasks on resources.
- `"tardiness"`: Minimize deadline lateness penalties.
- Or pass a custom `Objective` / `WeightedCompositeObjective`.

### `solve()`

Compiles and solves the CP-SAT model.

```python
scheduler.solve(config: SolverConfig | None = None) -> ScheduleResult
```

Returns a `ScheduleResult` containing:

- `status`: `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `TIMEOUT`.
- `makespan`: Earliest time all tasks complete.
- `tasks`: Dictionary mapping `task_id` to `ScheduledTask(start, end, duration, assigned_resources)`.
- `resources`: Dictionary mapping `resource_id` to `ResourceAssignment(task_ids, total_utilized_time, idle_time, overtime)`.

---

## 6. Validation & Rescheduling

### `validate()`

Runs independent deterministic validation.

```python
scheduler.validate(result: ScheduleResult | None = None) -> ValidationReport
```

Returns a `ValidationReport` with `is_valid: bool`, `violations: list[ConstraintViolation]`, and `summary: str`.

### `reschedule()`

Performs what-if disruption simulation and stability-preserving rescheduling.

```python
scheduler.reschedule(
    baseline: ScheduleResult,
    disruptions: list[Disruption],
    current_time: int = 0,
    freeze_completed_tasks: bool = True,
    stability_weight: float = 1.0,
    makespan_weight: float = 0.5,
) -> SimulationOutcome
```

Returns a `SimulationOutcome` with:

- `rescheduled_result`: The new schedule.
- `validation_report`: Independent validation of the new schedule.
- `stability_metrics`: `ScheduleStabilityMetrics` measuring displaced tasks and total time shift.
- `affected_tasks`: List of task IDs directly impacted by the disruptions.

---

## 7. Scenarios & Golden Benchmarks

Exported directly from `ojas_ops` and `ojas_ops.scenarios`:

### `load_scenario()`

Loads a typed `ScenarioDefinition` from a JSON file via `msgspec`:

```python
scenario = load_scenario("path/to/scenario.json")
```

### `build_scheduler()`

Constructs and configures an operational `Scheduler` populated with all resources, tasks, candidate pools, transitions, workloads, and calendars declared in a scenario:

```python
scheduler = build_scheduler(scenario)
```

### `verify_expected()`

Evaluates the solved schedule against golden expected assertions embedded in the dataset:

```python
failures = verify_expected(scenario, result, report)
```

Returns a `list[str]` of assertion failure messages (empty if all conditions passed).

### `run_scenario()`

Executes an end-to-end scenario run (load $\rightarrow$ solve $\rightarrow$ validate $\rightarrow$ verify golden assertions):

```python
run_result = run_scenario("path/to/scenario.json", print_summary=True)
if run_result.is_success:
    print(f"Optimal makespan: {run_result.result.makespan}")
```

### Tabular CSV Ingestion

```python
tasks = load_tasks_from_csv("path/to/tasks.csv")
resources = load_resources_from_csv("path/to/resources.csv")
```

### Synthetic Benchmark Generators

```python
from ojas_ops.scenarios import (
    generate_jobshop_scenario,
    generate_workforce_scenario,
    generate_film_scenario,
    generate_benchmark_suite,
)

suite = generate_benchmark_suite("benchmarks/output", scales=["small", "medium", "large"])
```
