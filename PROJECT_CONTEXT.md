# Ojas Ops — Project Context & Architecture

## System Architecture

Ojas Ops is an enterprise-grade combinatorial operations research, scheduling, and simulation operating system.

### Key Directory Layout

```
ojas-ops/
├── pipeline_defs/       # 18 Declarative pipeline YAML manifests
├── rulesets/            # 8 Domain labor agreements and operational policy YAMLs
├── schemas/             # JSON Schemas (pipelines, checkpoints, rulesets, artifacts)
│   ├── artifacts/       # Canonical output schemas (stripboard, DOOD, job shop, etc.)
│   ├── checkpoints/     # Checkpoint validation schema
│   ├── pipelines/       # Pipeline manifest schema
│   └── rulesets/        # Ruleset policy schema
├── skills/              # Markdown stage director and meta skills
│   ├── meta/            # Onboarding, checkpoint protocol, validator reviewer
│   └── pipelines/       # 49 Stage director skills across 18 pipelines
├── python/              # Python monorepo workspace
│   └── packages/ojas-ops/
│       ├── src/ojas_ops/
│       │   ├── agents/          # ToolRegistry, AgentTool, Claude Messages API
│       │   ├── api/             # Django-Bolt API ViewSets (/pipelines, /projects, etc.)
│       │   ├── models/          # Multi-tenant Django ORM models (ProjectWorkspace, etc.)
│       │   ├── observability/   # Structured JSON logger, OpenTelemetry tracing, SSE events
│       │   ├── pipelines/       # Manifest loader, checkpoint writer, dual persistence
│       │   ├── services/        # CP-SAT solver and deterministic validator services
│       │   └── temporal/        # Durable workflows (PipelineExecutionWorkflow) & activities
│       └── tests/               # Pytest suite (105 unit and full-stack integration tests)
└── typescript/          # Frontend Turborepo workspace
    ├── apps/ops-studio/ # Next.js 16 App Router Studio (/projects/new, [id], gates, simulations)
    └── packages/
        ├── sdk/         # @ojas-ops/sdk typed client with 1:1 boundary parity
        └── ui/          # @ojas-ops/ui shared component library (Gantt, SvgRenderer, etc.)
```

## Developer Commands

```bash
# Backend development server (Django-Bolt on http://127.0.0.1:8000)
make dev-backend

# Frontend Ops Studio (Next.js on http://localhost:5900)
make dev-frontend

# Run full Python test suite
make test

# Run TypeScript type gates
make gates
```
