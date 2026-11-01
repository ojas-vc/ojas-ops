# Simulation & Rescheduling

Operational schedules are constantly disrupted by unforeseen events:

- An actor or key technician falls ill.
- A critical machine suffers mechanical breakdown.
- Bad weather disrupts outdoor event setups or filming.
- An urgent priority order arrives in a manufacturing plant.
- A lunar festival or statutory holiday date shifts.

The Ojas Ops `ScenarioSimulator` supports what-if simulation, impact analysis, and minimally-disruptive rescheduling.

```python
from ojas_ops.simulation import (
    ScenarioSimulator,
    Disruption,
    DisruptionType,
    ScheduleStabilityMetrics,
    calculate_stability_metrics,
)
```

---

## 1. Disruption Modeling

Disruptions are represented by the `Disruption` struct:

```python
class Disruption(msgspec.Struct, kw_only=True):
    type: DisruptionType
    resource_id: str | None = None
    task_id: str | None = None
    start: int | None = None
    end: int | None = None
    delta: int = 0
    description: str = ""
    new_task: Task | None = None
```

### Supported Disruption Types (`DisruptionType`)

| Type                      | Description                                        | Effect on Model                                      |
| :------------------------ | :------------------------------------------------- | :--------------------------------------------------- |
| `RESOURCE_UNAVAILABLE`    | Machine outage, location cancellation, sick leave. | Adds blackout window $[start, end)$ to the resource. |
| `TASK_DELAYED`            | Material shipment or arrival delay.                | Increases task `earliest_start` by $\delta$.         |
| `TASK_DURATION_INCREASED` | Unexpected complexity, extra scene retakes.        | Increases task `duration` by $\delta$.               |
| `TASK_ADDED`              | Urgent emergency order or unscripted scene.        | Injects a new task into the scheduling model.        |
| `TASK_CANCELLED`          | Scene cut or cancelled session.                    | Removes task and frees its allocated resources.      |
| `CAPACITY_REDUCED`        | Fleet reduction, partial crew absence.             | Decreases cumulative resource capacity by $\delta$.  |

---

## 2. Running a Reschedule Simulation

```python
from ojas_ops import Scheduler
from ojas_ops.simulation import Disruption, DisruptionType

scheduler = Scheduler()
# ... configure resources, tasks, constraints ...
baseline_schedule = scheduler.solve()

# Simulate machine breakdown from t=120 to t=180
breakdown = Disruption(
    type=DisruptionType.RESOURCE_UNAVAILABLE,
    resource_id="cnc_mill_01",
    start=120,
    end=180,
    description="Coolant pump failure",
)

# Reschedule at current_time = 100 (freeze tasks started before t=100)
outcome = scheduler.reschedule(
    baseline=baseline_schedule,
    disruptions=[breakdown],
    current_time=100,
    freeze_completed_tasks=True,
    stability_weight=1.5,  # High weight minimizes moving unrelated tasks
    makespan_weight=0.5,
)

print(f"Reschedule Status: {outcome.rescheduled_result.status.value}")
print(f"Directly Affected Tasks: {outcome.affected_tasks}")
print(f"Tasks Moved: {outcome.stability_metrics.tasks_moved_count}")
print(f"Total Displacement: {outcome.stability_metrics.total_displacement} mins")
print(f"Schedule Stability Ratio: {outcome.stability_metrics.preserved_ratio * 100:.1f}%")
```

---

## 3. Stability Metrics (`ScheduleStabilityMetrics`)

Ojas Ops quantitatively measures the disruption caused by rescheduling:

```python
class ScheduleStabilityMetrics(msgspec.Struct, kw_only=True):
    tasks_moved_count: int = 0  # Number of tasks whose start time shifted
    total_tasks_count: int = 0  # Total tasks in baseline
    preserved_ratio: float = 1.0  # Fraction of tasks remaining at baseline time
    total_displacement: int = 0  # Sum of absolute start deviations
    max_displacement: int = 0  # Maximum single-task start shift
    makespan_delta: int = 0  # Change in overall completion time
    cost_delta: float = 0.0  # Change in financial objective
    displaced_tasks: list[str] = []  # IDs of tasks that shifted
```
