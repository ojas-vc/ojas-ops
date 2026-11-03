# Ojas Ops — Python Workspace

Polyglot Python workspace for **Ojas Ops**: an open-source constraint-based scheduling, resource allocation, and operations research framework built on [Google OR-Tools](https://developers.google.com/optimization) CP-SAT and [Django-Bolt](https://github.com/hyperbolt/django-bolt).

---

## 1. Structure

```text
python/
├── pyproject.toml             # uv workspace root definition
├── uv.lock                    # Locked dependency resolution
├── Makefile                   # Backend test, lint, and format automation
├── packages/
│   └── ojas-ops/              # Core operations research framework & Bolt API
│       ├── pyproject.toml
│       ├── src/ojas_ops/      # Core models, solvers, validation, simulation, adapters
│       └── tests/             # Comprehensive pytest test suite
├── apps/
│   └── sandbox/               # Django + Django-Bolt runner hosting API endpoints
│       ├── manage.py
│       ├── config/            # Django settings, URLs, ASGI
│       └── sandbox/           # Temporal worker configurations and local runners
├── examples/                  # 8 domain-specific runnable scheduling scripts
└── scripts/                   # Verification runners & benchmarks
```

---

## 2. Requirements & Setup

- **Python**: `>=3.12, <3.15` (Python 3.14 recommended)
- **Tooling**: [uv](https://docs.astral.sh/uv/) package manager

```bash
cd python

# Pin Python version
uv python pin 3.14

# Synchronize virtual environment
uv sync
```

---

## 3. Running Backend Services

### Development Server (Django-Bolt API)

The sandbox provides high-performance asynchronous HTTP and WebSocket endpoints powered by Django-Bolt:

```bash
cd python/apps/sandbox
uv run python manage.py runserver 0.0.0.0:8000
```

Verify service health:
```bash
curl http://127.0.0.1:8000/healthz
# {"status": "ok", "service": "ojas-ops-api", "version": "0.1.0"}

curl http://127.0.0.1:8000/readyz
# {"ready": "true", "engine": "Google OR-Tools CP-SAT"}
```

---

## 4. Testing & Code Quality

All quality checks can be run via the local `python/Makefile` or the root monorepo `Makefile`:

```bash
# Run unit and integration tests
make -C python test

# Fast pytest execution without coverage
make -C python test-fast

# Ruff linting & formatting checks
make -C python lint

# Format code with Ruff
make -C python fmt

# Type-checking with mypy
make -C python typecheck

# Full check suite (test + lint + mypy)
make -C python check
```

---

## 5. Architecture & API Endpoints

The core framework exposes 24 production endpoints in `ojas_ops.api`:

- **Health Probes**: `/healthz`, `/readyz`
- **Model CRUD**: `/schedule-runs`, `/optimization-jobs`, `/scenarios`, `/disruption-logs`
- **Temporal Flows & HITL**:
  - `/temporal/dispatch/schedule-optimization` (dispatch asynchronous workflow)
  - `/temporal/status/{id}` (query live progress basis points and objective bounds)
  - `/temporal/approval-state/{id}` (human-in-the-loop inspection)
  - `/temporal/signal/{id}/approve` (signal supervisor approval or rejection)
- **CP-SAT Solver Core**: `/schedules/optimize`, `/schedules/validate`
- **Scenarios Studio**: `/scenarios/run`, `/scenarios/generate`
- **Simulation & Disruption**: `/simulations/disruption-impact`
- **Multi-Format Visualizers**:
  - `/visualizations/stripboard.html`
  - `/visualizations/stripboard.svg`
  - `/visualizations/dood-matrix.json`
  - `/visualizations/gantt.svg`
  - `/visualizations/report.html`
- **Calendar Engines**:
  - `/calendars/astrological/blackouts` (Vedic Panchang Rahu Kalam & Yamagandam)
  - `/calendars/shift/operational-hours` (Industrial shifts, lunch/maintenance windows)
- **Domain Adapters**:
  - `/adapters/film-production/optimize` (Macro Level 1 cross-boarding with DOOD & SAG-AFTRA drop-and-pickup)
  - `/adapters/film-production/reschedule` (Rolling-horizon disruption handler with completed day preservation and cover set substitution)
  - `/adapters/film-production/intraday` (Micro Level 2 stripboard shot sequencing with setup turnaround & union meals)
  - `/adapters/film-production/call-sheet` (Official daily call sheet with staggered HMU salon chair waves)
  - `/adapters/manufacturing/solve`
  - `/adapters/workforce/solve`
  - `/adapters/marketing-flighting/solve`
  - `/adapters/academic-timetables/solve`
  - `/adapters/event-run-sheets/solve`

