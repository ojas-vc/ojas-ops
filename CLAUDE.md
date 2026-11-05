# Ojas Ops — Autonomous Operations Research & Optimization Framework

**MANDATORY: Read [`AGENT_GUIDE.md`](AGENT_GUIDE.md) before responding to ANY user operational request.**

Do not act on the user's scheduling, optimization, or production request until you have reviewed AGENT_GUIDE.md.
It contains routing rules that determine your first action based on what the user asked.

## Core Directives
1. **Rule Zero**: All operational problem solving (film shooting, manufacturing flow, nurse rostering, muhurat calculation) MUST go through a pipeline in `pipeline_defs/`.
2. **Deterministic Solver Core**: Never hallucinate schedules or feasibility. Rely on Google OR-Tools CP-SAT and `ScheduleValidator`.
3. **Dual Persistence**: Always sync file checkpoints in `projects/<tenant_id>/<project_id>/` with Django ORM models.
4. **Boundary Parity**: Maintain 1:1 typing parity with `@ojas-ops/sdk` and `msgspec` structs.
