# Ojas Ops

### Open Operations Research & Optimization Framework

**Model. Schedule. Optimize. Execute.**

Ojas Ops is an open-source, extensible Python framework for constraint-based scheduling, resource allocation, mathematical optimization, simulation, and operational planning.

Built on [Google OR-Tools](https://developers.google.com/optimization), powered by CP-SAT, and maintained by [CHITRAM.AI](https://chitram.ai), Ojas Ops provides reusable optimization infrastructure for solving complex real-world scheduling problems.

It is designed to support multiple industries through a common optimization core and extensible domain-specific models.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-blue.svg)](https://www.python.org/)
[![Solver](https://img.shields.io/badge/Solver-Google%20OR--Tools-green.svg)](https://developers.google.com/optimization)
[![Package](https://img.shields.io/badge/Package-uv-purple.svg)](https://docs.astral.sh/uv/)

---

## 1. Overview

Scheduling is a fundamental problem across almost every industry.

Organizations must coordinate people, machines, equipment, locations, tasks, materials, and time while satisfying operational constraints and optimizing competing objectives.

These problems are difficult because:

- Resources have limited availability and capacity.
- Tasks have dependencies and precedence requirements.
- Different activities have different durations.
- Resources may have specialized capabilities.
- Operational calendars and working hours vary.
- Multiple optimization objectives compete with each other.
- Unexpected events require schedules to be revised.
- Scheduling decisions need to be explainable and auditable.

Many organizations still rely on spreadsheets, manual coordination, static scheduling rules, or disconnected applications.

Ojas Ops aims to provide a reusable mathematical optimization foundation for these problems.

Instead of developing a different scheduling engine for every industry, developers can use a common framework and extend it with domain-specific requirements.

**One optimization foundation. Multiple industries. Reusable scheduling intelligence.**

## 2. Problem Statement

The goal of Ojas Ops is to simplify the development of reliable, extensible, and efficient scheduling and resource optimization systems.

The framework should enable developers to:

1. Model operational entities such as tasks, resources, calendars, and dependencies.
2. Define hard constraints and soft constraints.
3. Express optimization objectives.
4. Generate feasible schedules using mathematical optimization.
5. Compare alternative schedules and their trade-offs.
6. Validate scheduling results independently of the optimization solver.
7. Simulate operational changes and unexpected disruptions.
8. Reschedule affected activities while minimizing unnecessary changes.
9. Integrate optimization capabilities into existing business applications.
10. Build agentic AI applications around deterministic optimization engines.

The framework is designed around constraint programming and mathematical optimization, rather than relying on probabilistic AI-generated schedules.

## 3. Supported Domains and Use Cases

Ojas Ops is domain-independent. Its core abstractions can be applied to different operational scheduling problems.

### 3.1 Film & Media Production

Generate optimized shooting schedules using a **Two-Level Hierarchical Decomposition** (see the formal [Film Shooting Schedule Optimization Framework](research/film-shooting-schedule-optimization-framework.md)):

- **Level 1: Macro Combinatorial Cross-Boarding (CP-SAT MILP):**
  - Multi-unit concurrency (`MAIN`, `SECOND`, `SPLINTER`, `VFX`) with cross-unit lead cast exclusivity.
  - Continuous soundstage lease holding ($[\text{prep}, \text{strike}]$ span minimization) and physical facility disjunction.
  - Contractual talent availability, daily ceilings, minor child labor laws (DLSE/NCPCR), and SAG-AFTRA 10-day Drop-and-Pickup rules.
  - Completion bond high-hazard stunt deferral past production progress milestones (e.g., $\ge 70\%$).
  - Background extras clustering for large crowd scenes ($B_s \ge 50$).
  - Early VFX turnover deadlines and turnaround defense (mandatory 54h weekend turnaround).
  - Unidirectional costume distress progression and breakaway prop exhaustion limits.
- **Level 2: Micro Intra-Day Shot Sequencing (Disjunctive RCPSP-SDST):**
  - Camera setup transitions and axis rotation penalties ($\Delta \theta > 45^\circ$ setup angle changeovers, relighting buffers).
  - Natural light golden-hour dawn/dusk solar ephemeris bounds.
  - Statutory meal break compliance ($\le 6$ hours) and backward-calculated daily call sheets.

Optimization objectives:

- Minimize total shooting days and multi-unit production footprint.
- Minimize production costs and soundstage continuous lease liabilities.
- Minimize actor and crew idle time (SAG-AFTRA hold span minimization).
- Minimize location changes and setup changeover latency.
- Defend crew turnaround and eliminate fatigue-inducing "Fraturday" shifts.
- Maximize schedule robustness against weather and operational disruptions.

### 3.2 Manufacturing & Industrial Production

Generate production schedules by coordinating:

- Jobs and production orders.
- Machines and production resources.
- Production lines and work centres.
- Materials and inventory availability.
- Machine setup and changeover times.
- Job dependencies and precedence.
- Workforce and shift availability.
- Maintenance windows.
- Production capacity.
- Delivery deadlines.

Optimization objectives:

- Minimize makespan.
- Minimize production costs.
- Minimize machine idle time.
- Minimize setup and changeover time.
- Minimize tardiness.
- Maximize resource utilization.
- Improve production throughput.

### 3.3 Healthcare & Workforce Scheduling

Generate workforce schedules by coordinating:

- Nurses, doctors, and healthcare workers.
- Shifts and working hours.
- Staff availability and leave.
- Qualifications and skill requirements.
- Minimum staffing requirements.
- Rest periods and shift transitions.
- Department-specific staffing requirements.
- Workload distribution and fairness.

Optimization objectives:

- Satisfy staffing requirements.
- Minimize scheduling conflicts.
- Minimize overtime.
- Improve workload distribution.
- Respect staff preferences.
- Improve workforce utilization.

### 3.4 Education & Academic Timetabling

Generate academic timetables by coordinating:

- Courses and subjects.
- Faculty and instructor availability.
- Classrooms and laboratories.
- Student groups and batches.
- Classroom capacities.
- Time slots.
- Course dependencies.
- Examination schedules.

Optimization objectives:

- Eliminate faculty and student conflicts.
- Maximize classroom utilization.
- Minimize timetable gaps.
- Respect faculty preferences.
- Improve timetable distribution.

### 3.5 Event, Conference & Occasion Scheduling

Generate optimized multi-track agendas, venue space allocations, and operational run-sheets by coordinating:

- Multi-track conference tracks, keynote sessions, panel discussions, and workshops.
- Speakers, artists, and VIP availability windows with travel, prep, and buffer times.
- Halls, auditoriums, breakout rooms, and banquet spaces with varying capacities and AV capabilities.
- Vendor setup, turnaround, catering meal service, and tear-down windows.
- Exhibitor booth placement with competitor-separation constraints and footfall-tier distribution.
- B2B buyer-seller matchmaking time slots.
- Multi-ceremony occasion and wedding run-sheet sequences (milestones, rituals, banquets).

Optimization objectives:

- Eliminate room capacity violations and speaker assignment conflicts.
- Minimize attendee session overlap for concurrent high-demand topics.
- Maximize hall, stage, and booth space utilization.
- Minimize vendor turnaround dead-time and stage idle time.
- Minimize overtime penalties for crew, venue, and catering staff.

### 3.6 Marketing & Campaign Cadence Planning

Generate synchronized multi-channel advertising flight schedules and budget pacing by coordinating:

- Multi-stage campaign flights: teasers, launch blitzes, sustained engagement, and countdown flights.
- Marketing channels: Search, Social (Meta, LinkedIn), Programmatic, Email, SMS, WhatsApp, and OOH.
- Total budget envelopes with daily, weekly, and channel-specific min/max spend bounds.
- Audience frequency capping and fatigue constraints across channels (preventing over-saturation).
- Downstream sales team and call-center lead absorption capacity (matching ad spend to intake capacity).
- Content readiness and creative asset dependencies.

Optimization objectives:

- Maximize projected reach and conversion within a strict budget ceiling.
- Smooth inbound lead flow to match operational sales handling capacity.
- Maintain message cadence without exceeding channel-specific audience fatigue thresholds.
- Minimize budget allocation during historically low-converting time windows.

### 3.7 Cultural, Festival & Astrological Calendar-Aware Scheduling

Model operational schedules subject to non-Gregorian, lunar, astronomical, or culturally variable calendars:

- Auspicious timing windows (Shubh Muhurats, planetary hours, regional auspicious lagnas).
- Inauspicious blackout intervals (Rahu Kalam, Yamagandam, Gulika Kalam, Varjyam, Durmuhurtam).
- Lunar/Tithi-based dynamic campaign flighting (e.g., anchoring campaign milestones to D - 30 days before a shifting lunar festival).
- Seasonal demand surges (wedding seasons, festive shopping peaks like Dhanteras/Diwali) vs. cultural blackouts (Pitru Paksha, Kharmas, Chaturmas, solar/lunar eclipses).
- Regional workforce availability fluctuations due to festival leave (e.g., Durga Puja, Chhath, Pongal, Onam).
- Regulatory event constraints (statutory Dry Days, municipal curfew hours, sound emission limits).

Optimization objectives:

- Ensure high-value ceremonies, launches, or trades fall strictly within calculated auspicious intervals.
- Hard-exclude inauspicious windows and regulatory blackout hours from critical milestones.
- Rebalance manufacturing and logistics capacity around regional festival workforce availability.
- Align marketing and inventory readiness with lunar and festive demand spikes.

### 3.8 Additional Applications

The same optimization foundation can support:

- Employee and workforce rostering.
- Logistics and transportation scheduling.
- Supply chain planning.
- Construction project scheduling.
- Maintenance planning.
- Sports tournament scheduling.
- Field service scheduling.
- Project resource allocation.
- Franchise operations.
- Venture and business resource planning.

## 4. Core Concepts

Ojas Ops is organized around reusable scheduling primitives.

### Tasks and Activities

Represent work that needs to be completed.

Attributes may include:

- Unique identifier.
- Duration.
- Earliest start time.
- Latest completion time.
- Priority.
- Dependencies.
- Required resources.
- Execution requirements.

### Resources

Represent entities required to execute tasks.

Examples:

- People.
- Machines.
- Equipment.
- Locations.
- Rooms.
- Vehicles.
- Production lines.

Resource attributes may include:

- Availability.
- Capacity.
- Skills and capabilities.
- Cost.
- Working calendars.
- Resource dependencies.

### Time and Calendars

Represent scheduling horizons, temporal restrictions, and multi-calendar mappings.

Ojas Ops abstracts time into discrete integer intervals while decoupling the underlying calendar system through pluggable `CalendarProvider` adapters:

- **Operational Calendars:** Working hours, shifts, overtime rules, rest periods, and weekend definitions.
- **Variable & Non-Gregorian Calendars:** Lunar calendars, Tithi/Nakshatra cycles, Hindu Panchang, and Hijri calendars with shifting annual Gregorian dates.
- **Interval Inclusion & Exclusion Windows:** Auspicious windows (Muhurats), inauspicious intervals (Rahu Kalam), maintenance downtimes, and statutory blackout dates (Dry Days, public holidays).
- **Dynamic Date Offsets:** Tasks anchored to variable calendar events (e.g., `Festival_Date - 14 days` or `Tithi_Start + 2 hours`).
- **Turnaround & Buffer Intervals:** Sequence-dependent buffer intervals between tasks sharing a physical space (e.g., cleaning, sound checks, decor transitions).
- **Time Zones & Solar Windows:** Location-specific sunrise, sunset, and daylight constraints.

### Constraints

Represent conditions that determine whether a schedule is feasible or desirable.

#### Hard Constraints

Conditions that must be satisfied.

Examples:

- A resource cannot execute incompatible tasks simultaneously.
- A task cannot start before its dependencies are completed.
- An unavailable resource cannot be assigned.
- Resource capacity cannot be exceeded.
- Mandatory working-hour limits must be respected.

#### Soft Constraints

Preferences that the solver should optimize.

Examples:

- Minimize idle time.
- Minimize overtime.
- Minimize travel.
- Minimize location transitions.
- Balance workloads.
- Prefer certain time windows.
- Minimize schedule changes.

Hard constraints and soft constraints must remain distinguishable. A solver must not violate mandatory constraints merely to improve an objective score.

### Optimization Objectives

Support configurable optimization objectives such as:

- Minimize makespan.
- Minimize total cost.
- Minimize resource idle time.
- Minimize overtime.
- Minimize tardiness.
- Maximize resource utilization.
- Minimize transitions.
- Balance resource workloads.
- Minimize deviations from an existing schedule.

Multiple objectives may be combined using weighted optimization or staged optimization strategies.

## 5. Architecture

Ojas Ops follows a layered and extensible architecture.

```text
                    Applications & Agents
                              |
        +---------------------+---------------------+
        |                     |                     |
     FilmTech        Events & Confs       Marketing & GTM
        |                     |                     |
        +---------------------+---------------------+
                              |
                  Domain Scheduling Models
          (Run-Sheets, Campaign Flights, Rostering)
                              |
                Pluggable Calendar Providers
          (Gregorian, Panchang / Lunar, Statutory)
                              |
            Constraint & Objective Formulations
         (Intervals, Precedence, Cumulative, No-Overlap)
                              |
                      Optimization Core
                   (Google OR-Tools CP-SAT)
                              |
               Validation & Feasibility Engine
                              |
               Simulation, Replay & Analysis
                              |
                     Optimized Schedule
```

### Architectural Principles

**Domain Independence**

The optimization core must not depend on any particular industry.

**Composability**

Scheduling models, constraints, and objectives should be reusable.

**Deterministic Validation**

Schedule feasibility must be verified using deterministic validation rather than LLM judgments.

**Extensibility**

New industry-specific scheduling models should be added without unnecessarily modifying the core.

**Explainability**

Optimization results should expose objective values, constraint outcomes, solver status, and relevant trade-offs.

**Reproducibility**

Inputs, solver configuration, and results should be reproducible wherever the solver and execution configuration permit.

**Human Control**

Production-critical schedule changes should support explicit review and approval.

## 6. Technology Stack

| Layer                 | Technology                           |
| --------------------- | ------------------------------------ |
| Programming language  | Python (3.11–3.14, 3.14 recommended) |
| Package management    | uv                                   |
| Workspace management  | uv workspaces                        |
| Optimization          | Google OR-Tools                      |
| Constraint solver     | CP-SAT                               |
| Typed data structures | msgspec                              |
| Testing               | pytest                               |
| Linting               | Ruff                                 |
| Type checking         | mypy / pyright                       |
| Documentation         | MkDocs                               |
| CI/CD                 | GitHub Actions                       |

The core library should remain lightweight and independent of application frameworks.

Django, FastAPI, databases, Redis, message brokers, and agent frameworks should be optional integrations rather than mandatory dependencies.

## 7. Installation & Development Setup

Ojas Ops is managed with [uv](https://docs.astral.sh/uv/) workspaces and requires Python 3.11–3.14 (Python 3.14 recommended for optimal compatibility with the latest Google OR-Tools and msgspec binary wheels).

### 7.1 Using as a Dependency

Add `ojas-ops` to your project using `uv`:

```bash
uv add ojas-ops
```

Or install it into a virtual environment with `uv pip`:

```bash
uv pip install ojas-ops
```

The package distribution name is provisional until its availability on PyPI is verified.

### 7.2 Setting Up the Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ojas-vc/ojas-ops.git
   cd ojas-ops
   ```

2. **Pin the compatible Python version:**

   ```bash
   uv python pin 3.14
   ```

3. **Create the virtual environment and synchronize dependencies:**

   ```bash
   uv sync
   ```

4. **Verify the environment:**

   ```bash
   uv run python -c "import ortools, msgspec; from ortools.sat.python import cp_model; print('OR-Tools:', ortools.__version__); print('msgspec:', msgspec.__version__)"
   ```

5. **Run tests and quality checks:**

   ```bash
   # Run the test suite
   uv run pytest

   # Run Ruff linter and formatter
   uv run ruff check
   uv run ruff format
   ```

## 8. Quick Start

The following is an illustrative API for the intended developer experience. It is not yet a guarantee of the implemented public API.

```python
from ojas_ops import Scheduler
from ojas_ops.models import IntervalWindow

scheduler = Scheduler()

# Add a venue or production resource
scheduler.add_resource(
    id="main-auditorium",
    capacity=1,
)

# Add an event session or task
scheduler.add_task(
    id="keynote-launch",
    duration=60,  # minutes
    required_resources=["main-auditorium"],
)

# Enforce a blackout window (e.g., maintenance or Rahu Kalam)
scheduler.add_blackout_window(
    resource_id="main-auditorium",
    window=IntervalWindow(start=90, end=150, label="blackout_window"),
)

# Anchor to an auspicious target window (e.g., Shubh Muhurat)
scheduler.add_target_window(
    task_id="keynote-launch",
    window=IntervalWindow(start=180, end=300, label="shubh_muhurat"),
    hard=True,
)

scheduler.minimize("makespan")

result = scheduler.solve()
validation = scheduler.validate(result)

print(result)
print(validation)
```

Run scripts or test scenarios within the uv environment:

```bash
uv run python path/to/script.py
```

The API should expose enough of the underlying optimization model to support advanced use cases instead of hiding all mathematical concepts behind generic abstractions.

## 9. Project Structure

The initial implementation will use a uv workspace.

```text
ojas-ops/
│
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── LICENCE.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── NOTICE
│
├── packages/
│   └── ojas-ops/
│       ├── pyproject.toml
│       ├── src/
│       │   └── ojas_ops/
│       │       ├── __init__.py
│       │       ├── models/
│       │       ├── scheduling/
│       │       ├── calendars/
│       │       ├── constraints/
│       │       ├── objectives/
│       │       ├── solvers/
│       │       ├── validation/
│       │       ├── simulation/
│       │       ├── adapters/
│       │       └── scenarios/
│       │
│       └── tests/
│
├── examples/
│   ├── basic_scheduling/
│   ├── film_production/
│   ├── manufacturing/
│   ├── nurse_rostering/
│   ├── academic_timetabling/
│   ├── event_run_sheets/
│   ├── marketing_flighting/
│   └── festival_calendar/
│
├── benchmarks/
│
├── docs/
│
├── research/
│   └── film-shooting-schedule-optimization-framework.md
│
└── scripts/
```

Domain-specific packages may be split into separately installable distributions as the project matures.

## 10. Harness Engineering & Reliability

Ojas Ops should treat reliability, reproducibility, and evaluation as first-class engineering requirements.

The project should progressively incorporate:

- Input and output schema validation.
- Deterministic constraint verification.
- Solver execution tracing.
- Optimization run metadata.
- Reproducible test scenarios.
- Golden scheduling datasets.
- Regression tests.
- Performance benchmarks.
- Failure injection.
- Schedule replay.
- Evaluation metrics.
- Alternative solution comparisons.

### Scenarios & Golden Datasets Implementation

The `ojas_ops.scenarios` package implements Section 10's reliability and reproducibility requirements:

- **Typed Schemas:** `ScenarioDefinition` with embedded `ExpectedResult` assertions.
- **Microsecond Encoding/Decoding:** Built on `msgspec.Struct`.
- **Golden Benchmark Assertions:** Automated verification of solver status, makespan bounds, objective bounds, and task timing bounds (`verify_expected()`).
- **CSV Support:** Flat task and resource parsing for spreadsheet interoperability (`load_tasks_from_csv`, `load_resources_from_csv`).
- **Synthetic Benchmark Generators:** Scalable synthetic data generation (`generate_jobshop_scenario`, `generate_workforce_scenario`, `generate_film_scenario`, `generate_benchmark_suite`).
- **Unified Runner:** `run_scenario()` with formatted operational reporting.
- **Benchmark Datasets:** 11 runnable datasets across all 8 industry domains in `examples/**/data/`.

### Agentic AI Integration

LLMs and agents can help with:

- Interpreting natural-language scheduling requirements.
- Extracting information from documents.
- Generating candidate domain constraints.
- Identifying missing information.
- Explaining optimization results.
- Coordinating human approval workflows.
- Initiating rescheduling scenarios.

However, the optimization engine and deterministic validators remain responsible for generating and verifying schedules.

Agent frameworks should integrate through optional adapters. The core library must function without an LLM.

## 11. Simulation & Rescheduling

A scheduling system must adapt to operational changes.

Ojas Ops should support scenario-based simulation and rescheduling.

Example scenarios:

- A key actor becomes unavailable.
- A shooting location is cancelled.
- A machine becomes unavailable.
- A manufacturing order becomes urgent.
- A nurse requests a shift change.
- A classroom becomes unavailable.
- Weather disrupts outdoor activities.
- A production budget is reduced.
- A lunar festival date shifts (e.g., Tithi or regional holiday revision), requiring calendar milestone re-anchoring.
- A keynote speaker drops out or flight delay causes multi-track conference agenda disruption.
- A venue turnaround delay cascades into subsequent event banquets.
- An advertising campaign underperforms on Day 3, requiring dynamic budget flighting reallocation.

The system should:

1. Identify affected tasks and resources.
2. Determine impacted constraints.
3. Generate alternative schedules.
4. Validate all candidates.
5. Compare cost and operational impact.
6. Measure schedule disruption.
7. Return recommendations for approval.

Rescheduling should preserve unaffected portions of an existing schedule whenever practical.

## 12. Development Roadmap & Implementation Status

```text
  Phase 1: Core Engine         [COMPLETED]  - Models, CP-SAT, Calendars, Validator, Objectives
  Phase 2: Advanced Opt        [COMPLETED]  - Precedence, Capacities, Transitions, Workloads, Pools
  Phase 3: Domain Adapters     [COMPLETED]  - Film (Two-Level), Mfg, Workforce, Academic, Events, Mktg
  Phase 4: Simulation          [COMPLETED]  - Disruption Injection, Stability Metrics, Rescheduling
  Research Monograph           [COMPLETED]  - Formal Film Scheduling Framework & Two-Level Decomposition
  ─────────────────────────────────────────────────────────────────────────────────────────────
  Phase 5: Service Layer       [PENDING]    - FastAPI (REST / OpenAPI 3.1) & gRPC Wire Service
  Phase 6: Temporal Workflows  [PENDING]    - Temporal.io Durable Solves, Heartbeating, Interruption
  Phase 7: Agentic AI Tools    [PENDING]    - Antigravity / CrewAI / LangChain Tool Harness
  Phase 8: Integer Scaling     [PENDING]    - Uniform Minor Currency & Minute Contracts Across All Adapters
  Phase 9: Visualizations      [PENDING]    - Interactive Stripboards, DOOD Tables, Gantt Renderers
  Phase 10: CI/CD & Release    [PENDING]    - GitHub Actions Matrix (Py 3.11-3.14), PyPI Release Automation
```

### Completed Milestones

#### Phase 1 — Core Scheduling Engine (Completed)

- Strict `msgspec.Struct` core domain models (`Task`, `Resource`, `Horizon`, `IntervalWindow`, `ScheduleResult`).
- Discrete time abstractions and pure-integer interval formulation.
- Pluggable `CalendarProvider` architecture (`StandardCalendarProvider` and `CulturalCalendarProvider` with Hindu Panchang, Shubh Muhurats, Rahu Kalam, Yamagandam, and lunar tithi offsets).
- Google OR-Tools CP-SAT discrete solver compilation.
- Multi-objective functions (Makespan, Cost, Idle Time, Tardiness, Stability, and Weighted Composite).
- Independent deterministic validator seam (`ScheduleValidator`) verifying schedules without solver state.

#### Phase 2 — Advanced Optimization & Constraints (Completed)

- Precedence relations with directional bounds (`FS`, `SS`, `FF`, `SF`) and min/max lag intervals.
- Cumulative resource capacities and disjunctive no-overlap constraints (`NewIntervalVar`, `AddNoOverlap`).
- Sequence-dependent transition matrices (setup changeovers and turnaround buffers).
- Workload and rest regulation (`constraints/workload.py` for max continuous duration, min rest recovery).
- Solution pool and alternative schedule generation via solver callbacks.
- Data-driven scenario runner with declarative JSON/CSV loaders, synthetic benchmark generators, and golden assertions.

#### Phase 3 — Production Domain Adapters (Completed)

- **Film Production (`FilmProductionScheduler`):** Upgraded to a publication-grade **Two-Level Hierarchical Decomposition**:
  - _Level 1 Macro Cross-Boarding:_ Multi-unit concurrency (`MAIN`, `SECOND`, `SPLINTER`, `VFX`) with cross-unit lead cast exclusivity, continuous soundstage lease tracking, physical stage facility disjunction, SAG-AFTRA 10-day Drop-and-Pickup rules, minor child labor caps (DLSE/NCPCR), completion bond high-hazard stunt deferral, background extras day clustering, early VFX turnover deadlines, and turnaround defense.
  - _Level 2 Micro Intra-Day Shot Scheduling:_ Disjunctive setup transitions (`CameraSetup`), camera axis angle rotation and relighting setup penalties ($\Delta \theta > 45^\circ$), solar golden-hour dawn/dusk intervals, and backward-calculated daily call sheets (pickup, HMU, wardrobe, on-set calls).
- **Manufacturing (`ManufacturingScheduler`):** Job shop and flow shop scheduling with family changeovers.
- **Healthcare (`WorkforceScheduler`):** Nurse rostering, skill mix, consecutive shift ceilings, and mandatory rest.
- **Academic (`AcademicTimetableScheduler`):** Courses, faculty time windows, student cohorts, room capacities.
- **Events (`EventRunSheetScheduler`):** Multi-track conference schedules, speaker availability, AV sound checks.
- **Marketing (`MarketingFlightingScheduler`):** Ad flighting, channel pacing, budget constraints, creative lead times.

#### Phase 4 — Simulation & Rescheduling (Completed)

- Disruption modeling (`simulation/disruption.py` for delays, cancellations, resource breakdowns, blackout windows).
- Schedule drift and stability metrics ($\Delta \text{makespan}$, displaced tasks, total shift minutes).
- Reactive rescheduling with frozen historical baselines and minimal disruption objectives.

#### Research Framework & Academic Monograph (Completed)

- Publication-grade mathematical specification in [`research/film-shooting-schedule-optimization-framework.md`](research/film-shooting-schedule-optimization-framework.md):
  - 8-category constraint taxonomy.
  - Formal MILP / CP-SAT formulation and Disjunctive RCPSP-SDST micro-formulation.
  - Exact proofs of NP-hardness, decomposition rationale, and runnable Python reference code.

---

#### Phase 5 — Django-Bolt High-Performance API & Ecosystem Boilerplate (Completed)

- **Compulsory Ojas Boilerplate Package Structure:** Implemented standard folder-per-layer layout in `packages/ojas-ops/src/ojas_ops/`:
  - `apps.py` (`OjasOpsConfig`), `exceptions.py` (`OptimizationInfeasibleError`, `ScheduleValidationError`, `TemporalTimeoutError`).
  - `abstract_models/` (`AbstractScheduleRun`, `AbstractOptimizationJob`, `AbstractScenarioRecord`, `AbstractDisruptionLog`).
  - `models/` (`ScheduleRun`, `OptimizationJob`, `ScenarioRecord`, `DisruptionLog` with lazy-loading and backward-compatible struct exports).
  - `schemas/` (`time.py`, `task.py`, `resource.py`, `schedule.py`, `scheduling.py`, `simulation.py`, `events.py`).
  - `services/` (`optimizer.py`, `validator.py`, `simulator.py`, `temporal_dispatcher.py`).
  - `selectors/` (`schedule_runs.py`, `optimization_jobs.py`).
  - `admin/` (`schedule_run.py`, `optimization_job.py`, `scenario_record.py`, `disruption_log.py`).
  - `migrations/` (`0001_initial.py`).
- **Rust-Powered HTTP Engine via `django-bolt` (`ojas_ops.api`):**
  - High-throughput endpoints serving 300k+ req/sec using Actix Web + Tokio + PyO3 with full **Class-Based Views (CBVs)** and **Model-Based Views (`ModelViewSet`)**:
    - **Model-Based Views (`ModelViewSet` with Full CRUD, Pagination & Multi-Tenant Filtering):**
      - `ScheduleRunModelViewSet` at `/schedules/runs`:
        - `GET /schedules/runs` (paginated list with `tenant_id` filtering)
        - `POST /schedules/runs` (create record, HTTP 201)
        - `GET /schedules/runs/{id}` (retrieve details)
        - `PUT /schedules/runs/{id}` (full update)
        - `PATCH /schedules/runs/{id}` (partial update)
        - `DELETE /schedules/runs/{id}` (destroy, HTTP 204)
      - `OptimizationJobModelViewSet` at `/workflows/jobs`: Full CRUD for tracking async durable solver runs.
      - `ScenarioRecordModelViewSet` at `/scenarios/records`: Full CRUD for storing and querying benchmark runs.
      - `DisruptionLogModelViewSet` at `/simulation/logs`: Full CRUD for audit tracking of operational disruption events.
    - **Domain Service ViewSets (`ViewSet` with `@action` Methods):**
      - **Schedules (`ScheduleViewSet` at `/schedules`):**
        - `POST /schedules/optimize/sync` (synchronous CP-SAT solve for <=30s operations).
        - `POST /schedules/validate` (independent deterministic validation).
      - **Workflows (`WorkflowViewSet` at `/workflows`):**
        - `POST /workflows/solve` (dispatch async durable Temporal workflow for heavy optimization).
        - `POST /workflows/hitl/start` (dispatch Human-in-the-Loop review and approval workflow).
        - `GET /workflows/{workflow_id}/status` (query incumbent objective, best bound, and progress).
        - `POST /workflows/{workflow_id}/signal/approval` (signal approval/rejection with reviewer notes).
        - `GET /workflows/{workflow_id}/state` (query review status and reviewer decision).
      - **Simulation & Rescheduling (`SimulationViewSet` at `/simulation`):**
        - `POST /simulation/simulate` (inject disruptions and compute affected tasks & stability metrics).
        - `POST /simulation/reschedule` (reactive re-optimization balancing makespan with stability).
      - **Visualizations & Reports (`VisualizationViewSet` at `/visualizations`):**
        - `POST /visualizations/stripboard/html` (render interactive HTML stripboard with day breaks).
        - `POST /visualizations/stripboard/svg` (render vector SVG stripboard).
        - `POST /visualizations/dood/html` (render interactive DOOD cast utilization matrix).
        - `POST /visualizations/gantt/svg` (render vector SVG Gantt chart timeline with resource rows).
        - `POST /visualizations/report/html` (export standalone print-ready HTML page).
      - **Domain Adapters (`AdaptersViewSet` at `/adapters`):**
        - `POST /adapters/film/optimize` (extended film shooting schedule optimization with DOOD).
        - `POST /adapters/manufacturing/optimize` (job-shop sequence optimization with family changeovers).
        - `POST /adapters/workforce/optimize` (staff shift rostering with qualification matching and rest rules).
        - `POST /adapters/marketing/optimize` (multi-channel campaign cadence and budget flighting).
        - `POST /adapters/academic/optimize` (conflict-free academic timetables for classrooms and faculty).
        - `POST /adapters/events/optimize` (multi-track conference run sheets and hall turnaround buffers).
      - **Calendars & Cultural Panchang (`CalendarViewSet` at `/calendars`):**
        - `POST /calendars/cultural/intervals` (compute Rahu Kalam, Yamagandam, and auspicious muhurats).
        - `POST /calendars/standard/blackouts` (generate operational working shift and weekend blackout windows).
      - **Scenarios & Benchmarks (`ScenarioViewSet` at `/scenarios`):**
        - `POST /scenarios/run` (execute declarative scenario JSON and verify golden assertions).
        - `POST /scenarios/generate` (generate synthetic benchmark scenarios: jobshop, workforce, film).
    - **Telemetry and Health Probes (`APIView`):**
      - `HealthCheckView` at `GET /healthz` (liveness probe).
      - `ReadinessCheckView` at `GET /readyz` (CP-SAT solver engine and runtime readiness probe).
- **Dedicated Host Sandbox Project (`apps/sandbox/`):**
  - Standalone runnable Django host in `apps/sandbox/` (a first-class `uv` workspace member) with `manage.py`, `pyproject.toml`, `config/settings.py`, `config/urls.py`, and database migrations.
  - Management commands:
    - `python apps/sandbox/manage.py runbolt` (production HTTP serving).
    - `python apps/sandbox/manage.py run_scenario_benchmarks --scale small|medium|large` (executes optimization benchmarks and records results in DB).
    - `python apps/sandbox/manage.py run_temporal_worker` (launches worker cluster).

#### Phase 6 — Durable Long-Running Solves & Temporal.io Orchestration (Completed)

- **Worker Multiprocessing & Queue Separation (`ojas_ops.temporal`):**
  - Patterned after Temporal Python best practices (`worker_multiprocessing`, `custom_converter`):
  - `WORKFLOW_TASK_QUEUE` ("ojas-ops-workflows"): Lightweight, non-blocking workflow event loops.
  - `SOLVER_ACTIVITY_TASK_QUEUE` ("ojas-ops-solver-activities"): Dedicated multi-core CPU solver pool using `ProcessPoolExecutor`.
- **Custom `msgspec` Payload Converter (`converter.py`):**
  - `MsgspecEncodingPayloadConverter` and `OjasOpsPayloadConverter(CompositePayloadConverter)` enabling microsecond C-speed serialization of typed structs without JSON dict overhead.
- **CP-SAT Solution Heartbeating (`solve_activity.py`):**
  - `TemporalHeartbeatCallback` reporting real-time incumbent objective values, best bounds, and solution counts back to Temporal every 5 seconds.
- **Human-in-the-Loop Review & Approval (`FilmScheduleApprovalWorkflow`):**
  - Workflow orchestrating candidate solve, deterministic validation, and human review via `workflow.wait_condition` and signal methods (`submit_review_decision`).

#### Phase 7 — Multi-Framework AI Agent Tool Harness & Elicitation (Completed)

- **Framework Adapters (`ojas_ops.agents`):**
  - **Google Antigravity SDK (`providers/antigravity.py`):** Declarative tool specifications for `optimize_film_schedule`, `optimize_job_shop`, and `verify_schedule_feasibility`.
  - **Google ADK (`providers/google_adk.py`):** `ojas_adk_activity_tool` wrapper with graceful error recovery over Temporal activities.
  - **Anthropic Claude (`providers/anthropic.py`):** Claude Messages API tool declarations and tool-result message loop formatters.
  - **CrewAI (`providers/crewai.py`):** `CrewAIFilmOptimizerTool` and `CrewAIManufacturingOptimizerTool` extending `crewai.tools.BaseTool`.
  - **LangChain & LangGraph (`providers/langchain.py`):** `StructuredTool` bindings for film and manufacturing schedulers.
- **Unstructured Prompt Elicitation (`elicitation/prompt_templates.py`):**
  - Few-shot extraction prompts converting script breakdowns, call notes, and production orders into valid `ProductionDataset` and scenario JSONs.

#### Phase 8 — System-Wide Pure-Integer Harmonization (Completed)

- Standardized all domain adapters to the **Pure-Integer Solver Invariant**:
  - `ManufacturingScheduler`: Integer `hourly_rate_cents`, `available_minutes`, `setup_minutes` with dual-property floating-point bridges.
  - `WorkforceScheduler`: Integer `hourly_rate_cents`, `max_weekly_minutes`, `min_rest_minutes`.
  - `MarketingFlightingScheduler`: Integer `daily_budget_cents`, `daily_budget_cap_cents`.
  - Zero floating-point rounding errors or non-determinism across all CP-SAT model constraints.

#### Phase 9 — Interactive Visualizations & Renderers (Completed)

- **Visual Renderers (`ojas_ops.visualization`):**
  - `StripboardRenderer`: Multi-strip color-coded Master Stripboard in HTML and SVG (`INT. DAY` white, `EXT. DAY` yellow, `INT. NIGHT` green, `EXT. NIGHT` blue, and black day-break bars).
  - `DOODRenderer`: Day Out of Days cast matrix with standard industry badges (`SW`, `W`, `H`, `WF`, `SWF`, `DROP`) and financial hold liabilities.
  - `GanttRenderer`: Resource and machine occupancy Gantt charts with timeline axes and setup changeover indicators.
  - `export_standalone_html`: Self-contained, responsive, print-ready HTML report bundle generator.

#### Phase 10 — Packaging, CI/CD & Deployment (Completed)

- **GitHub Actions CI/CD (`.github/workflows/ci.yml`):**
  - Multi-OS matrix (`ubuntu-latest`, `macos-latest`) testing across Python `3.12`, `3.13`, and `3.14`.
  - Automated Ruff linting & formatting gate.
  - Automated package tests (`packages/ojas-ops/tests/`) and sandbox tests (`sandbox/tests/`).
  - Automated benchmark smoke test and example verifications.
- **Multi-Stage Production Dockerfile (`Dockerfile`):**
  - Python 3.14 slim image with pre-compiled virtualenv, uv, and production serving via `manage.py runbolt`.
- **Automated Example Verification (`scripts/verify_examples.py`):**
  - End-to-end verification of all 8 domain examples passing 100%.

## 13. Development, Build & Release Commands

A comprehensive `Makefile` automates local development, testing, packaging, and release operations:

| Command                | Purpose                                                                           |
| :--------------------- | :-------------------------------------------------------------------------------- |
| `make help`            | Display available targets and documentation                                       |
| `make install`         | Sync workspace dependencies and virtualenv with `uv`                              |
| `make check`           | Run format check, Ruff linter, and Mypy static type checker                       |
| `make fmt`             | Format codebase with Ruff                                                         |
| `make lint-fix`        | Auto-fix autofixable Ruff lint violations                                         |
| `make test`            | Run full pytest test suite (28+ tests)                                            |
| `make test-fast`       | Run tests in quiet, fail-fast mode                                                |
| `make examples`        | Execute all 8 domain examples and verify end-to-end solutions                     |
| `make clean`           | Clean build artifacts (`dist/`, `build/`), cache directories, and `.pytest_cache` |
| `make build`           | Build source distribution (`.tar.gz`) and wheel (`.whl`) into `dist/`             |
| `make build-check`     | Verify integrity and inspect contents of built distribution packages              |
| `make bump-patch`      | Increment patch version (`0.1.0` -> `0.1.1`) across `pyproject.toml` files        |
| `make tag`             | Create annotated git release tag `v$(VERSION)`                                    |
| `make publish-dry-run` | Test PyPI package publishing in dry-run mode                                      |
| `make release`         | Complete end-to-end release pipeline (checks, tests, build, dry-run publish)      |

## 14. Contributing

Contributions are welcome.

Areas of contribution include:

- Scheduling primitives.
- Constraint implementations.
- Optimization strategies.
- Domain-specific models.
- Performance improvements.
- Benchmarks and datasets.
- Documentation and examples.
- Testing and evaluation.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 15. License

Ojas Ops is licensed under the Apache License, Version 2.0.

Copyright © 2026 CHITRAM.AI PRIVATE LIMITED.

See [LICENSE](LICENSE) for the complete licence text and [LICENCE.md](LICENCE.md) for licensing and intellectual property information.

## 16. Maintainers & Ownership

**Project:** Ojas Ops

**Legal owner:** CHITRAM.AI PRIVATE LIMITED

**Engineering and maintenance:** CHITRAM.AI

**Ecosystem:** Ojas.VC

Website: https://ojas.vc

Engineering: https://chitram.ai

GitHub: https://github.com/ojas-vc/ojas-ops

Ojas Ops is developed as shared open-source optimization infrastructure for applications across the CHITRAM.AI and Ojas.VC ecosystems.

---

**Ojas Ops — Model. Schedule. Optimize. Execute.**
