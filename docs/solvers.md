# Solvers & CP-SAT Engine

Ojas Ops leverages the **Google OR-Tools CP-SAT** constraint programming engine as its primary mathematical solver.

```python
from ojas_ops.solvers import CpSatSolver, SolverConfig
```

---

## 1. Solver Configuration: `SolverConfig`

```python
class SolverConfig(msgspec.Struct, kw_only=True):
    time_limit_seconds: float = 30.0
    num_workers: int = 8
    random_seed: int = 42
    log_search_progress: bool = False
    relative_gap_limit: float = 0.0
    stop_after_first_solution: bool = False
```

### Parameter Details

- **`time_limit_seconds`** _(float)_: Maximum wall-clock seconds the solver is permitted to search. Default is `30.0`. If reached, the solver returns the best feasible solution discovered so far.
- **`num_workers`** _(int)_: Number of parallel search threads. Modern CP-SAT achieves near-linear speedups with parallel portfolios (LNS, sat search, linear relaxation). Default is `8`.
- **`random_seed`** _(int)_: Ensures reproducible optimization runs across identical hardware and solver builds.
- **`log_search_progress`** _(bool)_: When set to `True`, streams CP-SAT's internal search progression, bounds, and cut generators to stdout.
- **`relative_gap_limit`** _(float)_: Relative optimality stopping threshold (e.g. `0.05` for 5% gap). Default is `0.0` (exact optimality).
- **`stop_after_first_solution`** _(bool)_: Exits immediately once any valid feasible schedule is found, minimizing latency when exact optimality is not required.

---

## 2. Warm Start & Solution Hints

When re-optimizing or solving a disrupted schedule, Ojas Ops supports warm-starting the search by injecting previous variable assignments as solution hints:

```python
# Pass known good start times to accelerate CP-SAT branch-and-bound search
scheduler.solve(hints={"task_01": 0, "task_02": 90, "task_03": 180})
```

The CP-SAT solver tests these hints before starting search heuristics, drastically reducing time-to-first-solution and tightening initial dual bounds.

---

## 3. Solver Telemetry & Metadata

Upon completion, `ScheduleResult.metadata` captures granular solver search statistics:

| Key                    | Description                                         | Example      |
| :--------------------- | :-------------------------------------------------- | :----------- |
| `solver_status_name`   | Raw CP-SAT completion status string.                | `"OPTIMAL"`  |
| `num_branches`         | Total search decision branches explored.            | `"66"`       |
| `num_conflicts`        | Number of conflict learning clauses generated.      | `"0"`        |
| `user_time`            | Total CPU compute time consumed.                    | `"0.0193s"`  |
| `deterministic_time`   | Deterministic ticks elapsed (hardware independent). | `"0.0023"`   |
| `best_objective_bound` | Best mathematical dual bound proven by solver.      | `"330.0000"` |

---

## 4. Compilation Mechanics

The `CpSatSolver` compiles Ojas Ops domain models into OR-Tools primitives:

### 4.1 Interval Variables

For each task $i$, the solver creates:

```python
start_var = model.new_int_var(earliest_start, latest_start, f"start_{task_id}")
end_var = model.new_int_var(earliest_end, latest_end, f"end_{task_id}")
interval_var = model.new_interval_var(start_var, duration, end_var, f"interval_{task_id}")
```

### 4.2 Alternative Resource Candidate Pools

When a task can be performed by one of several qualified resources (e.g. any available ICU nurse):

1. For each candidate resource $r \in \text{Pool}$:
   - A boolean presence variable is created: `pres = model.new_bool_var(...)`
   - An optional interval is created: `opt_int = model.new_optional_interval_var(start_var, duration, end_var, pres, ...)`
   - The optional interval joins resource $r$'s `no_overlap` constraint.
2. An exact-choice constraint is enforced:
   ```python
   model.add_exactly_one([pres_1, pres_2, ..., pres_k])
   ```
   This guarantees that exactly one resource is selected, and only the chosen resource's calendar and constraints are activated.

---

## 5. Solver Status Mapping

| OR-Tools Status | Ojas Ops Status (`ScheduleStatus`) | Interpretation                                                                                |
| :-------------- | :--------------------------------- | :-------------------------------------------------------------------------------------------- |
| `OPTIMAL`       | `ScheduleStatus.OPTIMAL`           | Proven mathematically optimal schedule found within the time limit.                           |
| `FEASIBLE`      | `ScheduleStatus.FEASIBLE`          | A valid feasible schedule was found, but optimality proof did not complete within time limit. |
| `INFEASIBLE`    | `ScheduleStatus.INFEASIBLE`        | Mathematically impossible to satisfy all hard constraints simultaneously.                     |
| `MODEL_INVALID` | `ScheduleStatus.MODEL_INVALID`     | Invalid variable bounds or conflicting formulation.                                           |
| `UNKNOWN`       | `ScheduleStatus.UNKNOWN`           | Search terminated without discovering any feasible point.                                     |
