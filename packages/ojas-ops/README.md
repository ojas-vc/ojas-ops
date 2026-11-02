# Ojas Ops (`ojas-ops`)

### Open Operations Research & Optimization Framework

**Model. Schedule. Optimize. Execute.**

`ojas-ops` is an open-source, extensible Python framework for constraint-based scheduling, resource allocation, mathematical optimization, simulation, and operational planning.

Powered by [Google OR-Tools](https://developers.google.com/optimization) CP-SAT and typed with [msgspec](https://jcristharif.com/msgspec/).

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-blue.svg)](https://www.python.org/)
[![Solver](https://img.shields.io/badge/Solver-Google%20OR--Tools-green.svg)](https://developers.google.com/optimization)
[![Package](https://img.shields.io/badge/Package-uv-purple.svg)](https://docs.astral.sh/uv/)

---

## Installation

```bash
uv add ojas-ops
```

Or via `pip`:

```bash
pip install ojas-ops
```

---

## Quick Start

```python
from ojas_ops import Scheduler
from ojas_ops.models import IntervalWindow, ResourceType

scheduler = Scheduler()

# 1. Add resource
scheduler.add_resource("main-hall", capacity=1, resource_type=ResourceType.FACILITY)

# 2. Add tasks
scheduler.add_task("prep-session", duration=30, required_resources=["main-hall"])
scheduler.add_task(
    "keynote", duration=60, required_resources=["main-hall"], dependencies=["prep-session"]
)

# 3. Add blackout & target windows
scheduler.add_blackout_window(
    resource_id="main-hall",
    window=IntervalWindow(start=40, end=90, label="cleaning"),
)
scheduler.add_target_window(
    task_id="keynote",
    window=IntervalWindow(start=100, end=200, label="auspicious_window"),
    hard=True,
)

# 4. Solve with Google OR-Tools CP-SAT
scheduler.minimize("makespan")
result = scheduler.solve()
print(f"Status: {result.status.value}, Makespan: {result.makespan} mins")

# 5. Independent deterministic validation
validation = scheduler.validate(result)
print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")
```

---

## Framework Architecture

- **`models`**: Strict `msgspec.Struct` domain primitives (`Task`, `Resource`, `Horizon`, `IntervalWindow`, `ScheduleResult`).
- **`calendars`**: Operational standard calendars (`StandardCalendarProvider`) and non-Gregorian / Hindu Panchang / astrological providers (`CulturalCalendarProvider`).
- **`constraints`**: Precedence (`FS`, `SS`, `FF`, `SF`), no-overlap, cumulative capacity, blackout/target windows, sequence-dependent transitions, min rest, and max workload.
- **`objectives`**: Makespan, lateness/tardiness, resource idle time, financial cost, baseline stability, and weighted composites.
- **`solvers`**: Google OR-Tools CP-SAT compilation, candidate pools, and execution engine.
- **`validation`**: Independent deterministic feasibility verification without solver dependencies.
- **`simulation`**: Operational disruption injection, schedule stability metrics, and reactive rescheduling.
- **`adapters`**: 6 domain adapters for Film (Two-Level Hierarchical Decomposition: Level 1 Macro Cross-Boarding with continuous soundstage leases, multi-unit concurrency, and SAG-AFTRA DOOD; Level 2 Micro Intraday Shot Scheduling with camera transitions and golden-hour solar bounds), Manufacturing, Healthcare, Academic Timetabling, Events, and Marketing.
- **`scenarios`**: Typed scenario definitions (`ScenarioDefinition`), fast `msgspec` JSON & CSV loaders, synthetic large-scale benchmark generators, golden expected assertions verification, and execution runner (`run_scenario`).
- **`research`**: Mathematical optimization research frameworks and formal proofs, including the [Film Shooting Schedule Optimization Framework](../../research/film-shooting-schedule-optimization-framework.md).

---

## Documentation

Full documentation is available in the [`docs/`](../../docs/) directory:

- [Architecture & Design](../../docs/architecture.md)
- [Scheduler API Reference](../../docs/api.md)
- [Domain Models](../../docs/models.md)
- [Calendar Providers](../../docs/calendars.md)
- [Constraints Engine](../../docs/constraints.md)
- [Optimization Objectives](../../docs/objectives.md)
- [CP-SAT Solvers](../../docs/solvers.md)
- [Validation Engine](../../docs/validation.md)
- [Simulation & Rescheduling](../../docs/simulation.md)
- [Industry Domain Adapters](../../docs/adapters.md)
- [Scenarios & Golden Datasets](../../docs/scenarios.md)

---

## License

Licensed under the Apache License, Version 2.0. Copyright © 2026 CHITRAM.AI PRIVATE LIMITED.
