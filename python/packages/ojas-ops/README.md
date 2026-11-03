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

## Framework Architecture & Layered Package Layout

The package follows strict separation of concerns, isolation of serialization, and a **1-class-per-file** structure across all layers:

- **`schemas`**: Consolidated strictly typed `msgspec.Struct` contract layer (canonical DTOs, events, API payloads, domain value objects, and solver contracts).
- **`abstract_models`**: Reusable Django abstract models with auditing fields (`id`, `tenant_id`, `created_at`, `updated_at`). 1 model per file.
- **`models`**: Concrete Django ORM database models (`ScheduleRun`, `OptimizationJob`, `ScenarioRecord`, `DisruptionLog`). 1 model per file.
- **`serializers`**: Dedicated Django Bolt serialization layer with full and create serializers per model (`ScheduleRunSerializer`, `ScheduleRunCreateSerializer`, etc.). 1 serializer module per model.
- **`selectors`**: Pure read-only query selectors with sync and async `a*` methods. 1 selector module per model.
- **`api`**: Modern RESTful Django Bolt API with **strictly 1 ViewSet / ModelViewSet / APIView per file** (50 total routes mounted via `BoltAPI`).
- **`admin`**: Django admin registration classes. 1 `ModelAdmin` per file.
- **`solvers`**: Google OR-Tools CP-SAT compilation, candidate pools, and execution engine.
- **`temporal`**: Durable workflows (`ScheduleOptimizationWorkflow`, `FilmScheduleApprovalWorkflow`) and worker pools.
- **`adapters`**: 6 domain adapters for Film (Hierarchical Macro/Micro Cross-Boarding), Manufacturing, Healthcare, Academic Timetabling, Events, and Marketing.
- **`visualization`**: HTML tables, SVG stripboards, DOOD matrices, and Gantt chart renderers.

---

## Canonical RESTful API Endpoints

All endpoints follow RESTful standards (plural kebab-case resources, semantic lookup params, standard HTTP verbs):

| Resource / Endpoint | HTTP Method | Handler / View Class | Description |
|---------------------|-------------|----------------------|-------------|
| `/schedule-runs` | `GET`, `POST` | `ScheduleRunModelViewSet` | List/filter and create schedule run records |
| `/schedule-runs/{id}` | `GET`, `PATCH`, `DELETE` | `ScheduleRunModelViewSet` | Retrieve, update, delete schedule run |
| `/optimization-jobs` | `GET`, `POST` | `OptimizationJobModelViewSet` | List and submit optimization jobs |
| `/optimization-jobs/{id}` | `GET`, `PATCH`, `DELETE` | `OptimizationJobModelViewSet` | Retrieve, update, delete optimization job |
| `/optimization-jobs/dispatch` | `POST` | `OptimizationJobModelViewSet.dispatch_solve` | Dispatch long-running async solve |
| `/optimization-jobs/hitl-dispatch` | `POST` | `OptimizationJobModelViewSet.dispatch_hitl` | Dispatch Human-in-the-Loop workflow |
| `/optimization-jobs/{workflow_id}/workflow-status` | `GET` | `OptimizationJobModelViewSet.get_workflow_status` | Query live Temporal workflow execution status |
| `/optimization-jobs/{workflow_id}/approvals` | `POST` | `OptimizationJobModelViewSet.submit_workflow_approval` | Submit review decision (`APPROVED`/`REJECTED`) |
| `/optimization-jobs/{workflow_id}/approval-state` | `GET` | `OptimizationJobModelViewSet.get_workflow_approval_state` | Query HITL approval state |
| `/scenarios` | `GET`, `POST` | `ScenarioModelViewSet` | List and create scenario benchmark records |
| `/scenarios/{id}` | `GET`, `PATCH`, `DELETE` | `ScenarioModelViewSet` | Retrieve, update, delete scenario record |
| `/scenarios/generate` | `POST` | `ScenarioModelViewSet.generate_scenario` | Generate synthetic benchmark scenario |
| `/scenarios/{id}/execute` | `POST` | `ScenarioModelViewSet.execute_scenario` | Execute benchmark scenario with golden assertions |
| `/disruption-logs` | `GET`, `POST` | `DisruptionLogModelViewSet` | List and record disruption audit entries |
| `/disruption-logs/{id}` | `GET`, `PATCH`, `DELETE` | `DisruptionLogModelViewSet` | Retrieve, update, delete disruption log |
| `/schedules/optimize` | `POST` | `ScheduleViewSet.optimize_schedule` | Synchronous CP-SAT combinatorial solve |
| `/schedules/validate` | `POST` | `ScheduleViewSet.validate_schedule` | Independent deterministic validation |
| `/simulations/disruptions` | `POST` | `SimulationViewSet.simulate_disruptions` | Simulate disruptions and calculate delay impacts |
| `/simulations/reschedule` | `POST` | `SimulationViewSet.reschedule_active` | Reactive re-optimization preserving baseline stability |
| `/visualizations/stripboards/html` | `POST` | `VisualizationViewSet.render_stripboard_html` | Render interactive HTML stripboard table |
| `/visualizations/stripboards/svg` | `POST` | `VisualizationViewSet.render_stripboard_svg` | Render vector SVG stripboard graphic |
| `/visualizations/dood-reports` | `POST` | `VisualizationViewSet.render_dood_html` | Render HTML Day Out of Days (DOOD) cast matrix |
| `/visualizations/gantt-charts` | `POST` | `VisualizationViewSet.render_gantt_svg` | Render vector SVG Gantt chart |
| `/visualizations/reports` | `POST` | `VisualizationViewSet.export_full_report_html` | Export standalone print-ready HTML report |
| `/calendars/cultural/intervals` | `POST` | `CulturalCalendarViewSet.get_intervals` | Compute Panchang & Rahu Kalam blackout intervals |
| `/calendars/standard/blackouts` | `POST` | `StandardCalendarViewSet.get_blackouts` | Compute shift, business hour, and weekend blackouts |
| `/adapters/film-production/optimize` | `POST` | `FilmProductionAdapterViewSet.optimize_film` | Optimize film shoot with DOOD cast minimization |
| `/adapters/manufacturing/optimize` | `POST` | `ManufacturingAdapterViewSet.optimize_manufacturing` | Optimize job shop with changeover setups |
| `/adapters/workforce/optimize` | `POST` | `WorkforceAdapterViewSet.optimize_workforce` | Optimize nurse and shift rostering |
| `/adapters/marketing-flighting/optimize` | `POST` | `MarketingFlightingAdapterViewSet.optimize_marketing` | Optimize marketing flight cadence and budget |
| `/adapters/academic-timetables/optimize` | `POST` | `AcademicTimetableAdapterViewSet.optimize_academic` | Optimize university class timetables |
| `/adapters/event-run-sheets/optimize` | `POST` | `EventRunSheetAdapterViewSet.optimize_events` | Optimize multi-track conference run sheets |
| `/healthz` | `GET` | `HealthCheckView` | Lightweight liveness probe |
| `/readyz` | `GET` | `ReadinessCheckView` | Readiness check verifying DB and Redis/Temporal |

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
