# Ojas Ops Documentation

### Open Operations Research & Optimization Framework

**Model. Schedule. Optimize. Execute.**

Ojas Ops is an extensible Python framework for constraint-based scheduling, resource allocation, mathematical optimization, simulation, and operational planning.

Built on [Google OR-Tools](https://developers.google.com/optimization) CP-SAT and typed with [msgspec](https://jcristharif.com/msgspec/), Ojas Ops provides a deterministic optimization foundation that spans multiple industries through a shared core and specialized domain adapters.

---

## Key Highlights

- **Deterministic Mathematical Optimization:** Powered by Google OR-Tools CP-SAT constraint programming engine—no probabilistic AI hallucinations in core scheduling logic.
- **High-Performance Typed Data Structures:** Structured with `msgspec.Struct` for microsecond-level serialization, strict typing, and zero overhead.
- **Pluggable Calendar Engine:** Native support for both standard business operational calendars (shifts, weekends, maintenance) and non-Gregorian / cultural calendars (astrological auspicious Shubh Muhurats, Rahu Kalam blackout intervals, and dynamic lunar/tithi offsets).
- **Independent Validation Seam:** Schedules are validated by a deterministic verification engine without any dependency on the CP-SAT solver, guaranteeing auditability and correctness.
- **Reactive Rescheduling & Simulation:** Built-in what-if scenario simulation that applies operational disruptions, freezes past execution, and solves with schedule stability objectives.
- **6 Out-of-the-Box Industry Adapters:** Specialized domain models for Film Production, Manufacturing, Healthcare Workforce Rostering, Academic Timetabling, Conference Run-Sheets, and Marketing Campaign Flighting.

---

## Quick Navigation

```text
                                  Ojas Ops
                                      │
     ┌────────────────────────┬───────┴────────┬────────────────────────┐
     ▼                        ▼                ▼                        ▼
Architecture & Design    Core Scheduling   Constraints & Goals    Domain Adapters
- System Overview        - Scheduler API   - Precedence           - Film Production
- Mathematical Model     - Typed Models    - No-Overlap           - Manufacturing
- Solver Abstraction     - Calendars       - Setup Matrices       - Healthcare Rostering
- Independent Audit      - Validation      - Rest & Workload      - Academic Timetabling
- Rescheduling Loop      - Simulation      - Multi-Objective      - Conference Run-Sheets
                                                                  - Campaign Flighting
```

| Section                         | Description                                                                                 |
| :------------------------------ | :------------------------------------------------------------------------------------------ |
| [Architecture](architecture.md) | High-level system topology, CP-SAT translation, and deterministic verification.             |
| [API Reference](api.md)         | Comprehensive reference for the fluent `Scheduler` orchestrator.                            |
| [Domain Models](models.md)      | `Task`, `Resource`, `Horizon`, `IntervalWindow`, `TimeWindow`, `ScheduleResult`.            |
| [Calendars](calendars.md)       | Standard operational calendars and Hindu Panchang / Cultural calendar providers.            |
| [Constraints](constraints.md)   | Precedence, cumulative capacity, no-overlap, blackout/target windows, setup matrices.       |
| [Objectives](objectives.md)     | Makespan, tardiness, idle time, financial cost, and baseline schedule stability.            |
| [Solvers](solvers.md)           | Google OR-Tools CP-SAT compilation, optional resource pools, and tuning parameters.         |
| [Validation](validation.md)     | Independent feasibility and constraint verification without solver dependencies.            |
| [Simulation](simulation.md)     | Disruption modeling, impact analysis, and minimally disruptive rescheduling.                |
| [Domain Adapters](adapters.md)  | Ready-to-use adapters for film, manufacturing, healthcare, academic, events, and marketing. |

---

## Installation

Add `ojas-ops` to your Python 3.11–3.14 project using `uv`:

```bash
uv add ojas-ops
```

Or install via `pip`:

```bash
pip install ojas-ops
```

---

## 5-Minute Quick Start

```python
from ojas_ops import Scheduler
from ojas_ops.models import IntervalWindow, ResourceType

# 1. Initialize the fluent scheduler
scheduler = Scheduler()

# 2. Add an operational resource (e.g., Auditorium or Workstation)
scheduler.add_resource(
    id="main-auditorium",
    capacity=1,
    resource_type=ResourceType.FACILITY,
)

# 3. Add tasks and dependencies
scheduler.add_task(
    id="sound-check",
    duration=30,  # minutes
    required_resources=["main-auditorium"],
)
scheduler.add_task(
    id="keynote-launch",
    duration=60,
    required_resources=["main-auditorium"],
    dependencies=["sound-check"],
)

# 4. Enforce an operational blackout window (e.g., maintenance or reset)
scheduler.add_blackout_window(
    resource_id="main-auditorium",
    window=IntervalWindow(start=40, end=90, label="maintenance_cleaning"),
)

# 5. Anchor keynote to an auspicious target window (e.g., Shubh Muhurat)
scheduler.add_target_window(
    task_id="keynote-launch",
    window=IntervalWindow(start=100, end=200, label="shubh_muhurat"),
    hard=True,
)

# 6. Optimize makespan (completion time)
scheduler.minimize("makespan")

# 7. Solve with Google OR-Tools CP-SAT
result = scheduler.solve()
print(f"Status: {result.status.value}")
print(f"Makespan: {result.makespan} mins")

for task_id, task in result.tasks.items():
    print(f" - [{task.start:03d}m - {task.end:03d}m] {task_id} (Duration: {task.duration}m)")

# 8. Deterministically validate feasibility independently of the solver
validation = scheduler.validate(result)
print(f"Validation: {'PASSED' if validation.is_valid else 'FAILED'} - {validation.summary}")
```
