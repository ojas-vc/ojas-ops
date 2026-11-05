# Ojas Ops — Agent Operating Guide

Start here. This is the complete operating guide and agent contract for Ojas Ops.
For system architecture, key files, and technical conventions see [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).

---

## 1. First Interaction — Onboarding

When the user's first message is exploratory or asks about capabilities ("what can you do?", "help me schedule my production", "I need to optimize my factory"), read the onboarding skill **before** taking action:

**Read:** `skills/meta/onboarding.md`

This skill guides you through:
1. Identifying the user's operational domain (Media, Manufacturing, Healthcare, Events, Growth, Cultural).
2. Selecting the appropriate industrial pipeline from the 18 catalog definitions.
3. Suggesting compatible rulesets (SAG-AFTRA, FWICE, California Title 22, Automotive OEM, ISO 9001).
4. Launching a project workspace under `projects/<tenant_id>/<project_id>/`.

---

## 2. Rule Zero — All Optimization Goes Through a Pipeline

**Every operational scheduling or production problem MUST execute through the pipeline system. No exceptions.**

When the user asks to schedule, balance, sequence, roster, or recover any production or operational workflow:

1. **Identify the pipeline.** Match the request to one of the 18 pipelines in `pipeline_defs/`.
2. **Read the pipeline manifest.** `pipeline_defs/<pipeline>.yaml` — review stages, tools, and gated checkpoints.
3. **Run preflight & initialize project.** Call `init_project` creating `projects/<tenant_id>/<project_id>/` and `ProjectWorkspace` DB record.
4. **Execute stage by stage.** For EACH stage, read the stage director skill (`skills/pipelines/<pipeline>/<stage>-director.md`) BEFORE doing any work.
5. **Verify feasibility.** Execute `verify_schedule_feasibility` or `ScheduleValidator`. Zero hard constraint violations are required before recording stage completion.
6. **Enforce Human-in-the-Loop gates.** If a stage has `human_approval_default: true`, stop and present the tradeoff frontier. Never mark a gated stage `completed` without explicit operator sign-off.

---

## 3. The 18 Industrial Pipelines Catalogue

```
├── 1. Entertainment & Media Production Operations
│   ├── film-crossboarding             (Macro Stripboard, Stage Lease, Cast DOOD)
│   ├── daily-call-sheet-sequencer     (Micro Setup SDST, Solar Azimuth, Meal Breaks)
│   └── production-disruption-recovery (Reactive Incident Triage & Rescheduling)
├── 2. Manufacturing & Industrial Operations
│   ├── job-shop-flow                  (Disjunctive CNC Spindles, Tooling SDST)
│   ├── flow-shop-batching             (Continuous Flow, Clean-in-Place Holding)
│   ├── jit-assembly-balancing         (Takt Time Balancing, Sub-Assembly Buffers)
│   └── supply-chain-replenishment     (Multi-Echelon Buffer Waves, Lead Times)
├── 3. Healthcare & High-Stakes Workforce Operations
│   ├── clinical-shift-rostering       (Title 22 Nurse Acuity Ratios, Gini Equity)
│   ├── surgical-suite-allocator       (OR Suite Bin-Packing, Sterilization Lags)
│   └── workforce-fatigue-compliance   (Labor Union Rest Auditing, Shift Repair)
├── 4. Experiential, Events & Hospitality Operations
│   ├── conference-multi-track-curator (Keynote Anchors, Speaker Transit Buffers)
│   ├── wedding-occasion-runsheet      (Multi-Day Ceremonies, Muhurat Anchors)
│   └── exhibition-booth-allocator     (Spatial Foot Traffic Gravity, Competitor Disjunction)
├── 5. Growth, Marketing & Field Logistics Operations
│   ├── campaign-cadence-flighting     (Omnichannel Spend Pacing, CRM Lead Smoothing)
│   ├── field-service-dispatch         (Vehicle Routing Problem with Time Windows - VRPTW)
│   └── academic-semester-timetabler   (Course-Room-Cohort Disjunctive Mapping)
└── 6. Cultural, Lunar & Astrological Operations
    ├── muhurat-auspicious-scheduler   (Panchang Ephemeris, Rahu Kalam Exclusions)
    └── festival-workforce-rebalance   (Regional Lunar Festival Leave & Safety Manning)
```

---

## 4. Dual-Persistence Seam

Every state transition and artifact is persisted in two synchronized locations:

1. **File-Backed Local Store**:
   - `projects/<tenant_id>/<project_id>/project.json`: Project identity and metadata.
   - `projects/<tenant_id>/<project_id>/checkpoint_<stage>.json`: Atomic stage checkpoint.
   - `projects/<tenant_id>/<project_id>/artifacts/`: Canonical JSON and rendered SVG/HTML.
   - `projects/<tenant_id>/<project_id>/history/`: Superseded checkpoint backups.
   - `projects/<tenant_id>/<project_id>/logs/events.jsonl`: Real-time audit event stream.

2. **Database-Backed Multi-Tenant ORM**:
   - `ProjectWorkspace`: Tracks `status`, `current_stage`, `completed_stages`, and ruleset.
   - `ScheduleRun`: Records `makespan`, `solve_time_seconds`, and solver status.
   - `OptimizationJob`: Manages Temporal workflow correlation IDs.

---

## 5. Checkpoint & Gating Protocol

When recording progress:
- **`status: "completed"`**: Permitted ONLY when all stage criteria are met. If `human_approval_required: true`, requires `human_approved: true`.
- **`status: "awaiting_human"`**: Required for all gated stages until operator signs off.
- **`CheckpointValidationError`**: Raised immediately if code attempts to mark a gated stage `completed` without approval.

**Read:** `skills/meta/checkpoint-protocol.md` and `skills/meta/validator-reviewer.md`.
