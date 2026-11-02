# Constraints Engine

Ojas Ops distinguishes strictly between **Hard Constraints** (conditions that must be satisfied for feasibility) and **Soft Constraints** (preferences optimized in objective functions).

Import root:

```python
from ojas_ops.constraints import (
    PrecedenceConstraint,
    TimeWindowConstraint,
    FixedTimeConstraint,
    NoOverlapConstraint,
    CumulativeResourceConstraint,
    BlackoutWindowConstraint,
    TargetWindowConstraint,
    TransitionConstraint,
    MinRestConstraint,
    MaxWorkloadConstraint,
)
```

---

## 1. Temporal Constraints

### 1.1 `PrecedenceConstraint`

Enforces dependency ordering between a predecessor and successor task.

```python
PrecedenceConstraint(
    predecessor_id: str,
    successor_id: str,
    dependency_type: DependencyType = DependencyType.FS,
    min_lag: int = 0,
    max_lag: int | None = None,
)
```

| Dependency Type         | Mathematical Meaning                 | Use Case                                                              |
| :---------------------- | :----------------------------------- | :-------------------------------------------------------------------- |
| `FS` (Finish-to-Start)  | `succ.start >= pred.end + min_lag`   | Standard sequential tasks (e.g. cutting before milling).              |
| `SS` (Start-to-Start)   | `succ.start >= pred.start + min_lag` | Synchronized starts (e.g. lighting rigs turn on when filming begins). |
| `FF` (Finish-to-Finish) | `succ.end >= pred.end + min_lag`     | Synchronized completions.                                             |
| `SF` (Start-to-Finish)  | `succ.end >= pred.start + min_lag`   | Relay handovers (e.g. guard shift transitions).                       |

### 1.2 `TimeWindowConstraint`

Restricts task execution boundaries:

```python
TimeWindowConstraint(
    task_id: str,
    earliest_start: int | None = None,
    latest_start: int | None = None,
    earliest_end: int | None = None,
    latest_end: int | None = None,
    deadline: int | None = None,
)
```

### 1.3 `FixedTimeConstraint`

Pins a task to an exact start time $t_{fixed}$:

```python
FixedTimeConstraint(task_id="opening_keynote", fixed_start=0)
```

---

## 2. Resource Constraints

### 2.1 `NoOverlapConstraint` (Disjunctive Scheduling)

For a unitary resource (capacity = 1), ensures that assigned tasks do not overlap in time:
$$\max(s_i, s_j) \ge \min(e_i, e_j) \quad \forall i \neq j \in T_r$$
Modeled in CP-SAT via `model.add_no_overlap(intervals)`.

### 2.2 `CumulativeResourceConstraint`

For shared resource pools with capacity $C > 1$, ensures that concurrent active tasks never exceed capacity:
$$\sum_{i \in T_r \mid s_i \le t < e_i} \text{demand}_i \le C \quad \forall t$$
Modeled in CP-SAT via `model.add_cumulative(intervals, demands, capacity)`.

---

## 3. Window & Interval Constraints

### 3.1 `BlackoutWindowConstraint`

Prevents tasks or resources from operating during an unavailable window $[W_{start}, W_{end})$:

- **Resource Blackouts:** Compiled directly into native fixed interval variables:
  $$I_{\text{blackout}} = \text{IntervalVar}(W_{start}, W_{end} - W_{start}, W_{end})$$
  Injected directly into `model.add_no_overlap(intervals)` or `model.add_cumulative()`, enabling CP-SAT's highest-speed interval propagation.
- **Task Blackouts:** Enforces non-overlap disjunction between the task interval and blackout interval:
  $$e_i \le W_{start} \quad \lor \quad s_i \ge W_{end}$$

### 3.2 `TargetWindowConstraint`

Requires a task to execute entirely within a designated target window $[T_{start}, T_{end}]$:
$$s_i \ge T_{start} \quad \land \quad e_i \le T_{end}$$

---

## 4. Sequence-Dependent Setup & Transitions

### `TransitionConstraint`

Enforces sequence-dependent setup times, travel times, or venue turnaround buffers:

```python
TransitionConstraint(
    resource_id: str,
    transition_matrix: dict[tuple[str, str], int],
    default_buffer: int = 0,
)
```

**Formulation via CP-SAT Circuit:**
To eliminate sub-tours and enforce a strict single chronological sequence across all tasks assigned to resource $r$, Ojas Ops compiles transitions using CP-SAT's specialized Hamiltonian circuit constraint:
- A dummy root node is added to anchor the start and end of the resource's schedule.
- Directed literal arcs $l_{i, j}$ are created between every pair of assigned tasks $(i, j)$ and the root node.
- `model.add_circuit(arcs)` guarantees a single continuous Hamiltonian tour passing through each active task exactly once.
- For every active arc $l_{i, j} = 1$, the linear transition spacing is enforced:
$$s_j \ge e_i + \text{setup}(i, j)$$

**Example:**

```python
scheduler.add_transition_matrix(
    resource_id="main_auditorium",
    transition_matrix={
        ("keynote_session", "panel_session"): 20,  # 20 mins to set up panel table
        ("panel_session", "banquet"): 45,  # 45 mins to clear hall for dining
    },
    default_buffer=15,
)
```

---

## 5. Workload & Recovery Constraints

### 5.1 `MinRestConstraint`

Guarantees a mandatory recovery gap between consecutive tasks on the same person or equipment:
$$s_{j} \ge e_{i} + \text{min\_rest} \quad \text{for consecutive } i, j$$

### 5.2 `MaxWorkloadConstraint`

Restricts cumulative working time assigned to a resource across the horizon:
$$\sum_{i \in \text{Assigned}(r)} d_i \le \text{max\_workload}$$
When candidate pools are used, this integrates directly with the binary presence variables:
$$\sum_{i} \text{pres}_{i, r} \cdot d_i \le \text{max\_workload}$$
