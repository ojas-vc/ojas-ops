# @ojas-ops/studio — Operations Research & Scheduling Studio

Interactive Next.js 16 operations research studio for **Ojas Ops**. Enables operational planners, engineers, and supervisors to model, schedule, optimize, simulate, and inspect constraint-based schedules.

---

## 1. Features & Route Directory

### Central Dashboard
- **`/`**: System overview with live backend health probes (`/healthz`, `/readyz`), resource counters, and quick navigation.

### Model-Based CRUD Operations
- **`/schedule-runs`**: Historical schedule runs data table with search, tenant filtering, and metadata inspection drawer.
- **`/schedule-runs/[id]`**: Deep inspector for a specific schedule run, including full JSON payloads, metrics, and re-solve actions.
- **`/optimization-jobs`**: Monitoring dashboard for Temporal background optimization jobs with live polling (3s cadence) and async dispatch.
- **`/optimization-jobs/hitl/[workflowId]`**: Human-in-the-Loop approval console for supervisors to review incumbent objectives, bounds, and approve/reject with operational notes.
- **`/scenarios`**: Declarative scenario definition catalog and upload modal.
- **`/simulations/logs`**: Disruption incident audit logs with modal for recording new operational incidents.

### Core Optimization Engines
- **`/schedules`** (aliased to `/workbench`): Synchronous CP-SAT solver workbench with horizon configuration, task/resource tables, strategy selector, and interactive Gantt chart.
- **`/schedules/validate`**: Deterministic schedule validator with hard vs. soft constraint violation breakdowns.
- **`/scenarios/runner`**: Automated scenario execution verifying outcomes against golden expected solutions.
- **`/scenarios/generator`**: Synthetic benchmark scenario generator with domain sliders (Job Shop, Workforce, Film) and 1-click library saving.
- **`/simulations`**: Disruption impact simulator and reactive rescheduler with stability penalty tuning.

### Visualizers & Calendars
- **`/visualizations`**: Multi-format visualizer studio with 1-click generation and modal previews for:
  - HTML Call Sheet Stripboard
  - Vector SVG Stripboard
  - Day-Out-of-Days (DOOD) Cast/Resource Matrix
  - High-resolution SVG Gantt Chart
  - Consolidated Printable Production Report
- **`/calendars`**: Operational calendar engine for computing:
  - Vedic Panchang Rahu Kalam and Yamagandam inauspicious blackout windows.
  - Multi-shift operational hours and lunch/maintenance blackout intervals.

### Domain-Specific Scheduling Studios
- **`/adapters/film-production`**: Call sheet optimization, SAG-AFTRA 10-day drop rules, soundstage turnover, and scene shooting sequences.
- **`/adapters/manufacturing`**: Job-shop machine scheduling and sequence-dependent setup matrix minimization.
- **`/adapters/workforce`**: Healthcare and plant shift rostering with qualification matching and mandatory rest intervals.
- **`/adapters/marketing-flighting`**: Multi-channel media ad spend pacing and flighting schedule optimization.
- **`/adapters/academic-timetables`**: Classroom and cohort clash-free university lecture scheduling.
- **`/adapters/event-run-sheets`**: Multi-track conference run sheet optimization and speaker conflict avoidance.

---

## 2. Configuration & Environment Variables

Create a `.env.local` file in `typescript/apps/ops-studio/`:

```env
# URL to Django-Bolt backend API (defaults to http://127.0.0.1:8000)
NEXT_PUBLIC_OJAS_OPS_API_URL=http://127.0.0.1:8000
```

---

## 3. Development & Production Commands

```bash
# Start Next.js development server on port 5900
pnpm dev

# Build production bundle
pnpm build

# Start production server on port 5900
pnpm start

# Type check
pnpm check-types

# Biome lint check
pnpm lint
```
