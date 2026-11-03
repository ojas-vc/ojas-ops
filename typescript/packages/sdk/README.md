# @ojas-ops/sdk — Ojas Ops TypeScript SDK

Strongly typed client library for the **Ojas Ops** optimization and constraint scheduling framework. Provides 100% API coverage for all 24 Django-Bolt routes, Temporal workflow dispatches, and domain adapters.

---

## 1. Installation

```bash
# In pnpm workspace
pnpm add @ojas-ops/sdk --filter @ojas-ops/studio

# Or via npm/yarn
npm install @ojas-ops/sdk
```

---

## 2. Quick Start

```typescript
import { OjasOpsClient } from "@ojas-ops/sdk";

const client = new OjasOpsClient({
  baseUrl: process.env.NEXT_PUBLIC_OJAS_OPS_API_URL || "http://127.0.0.1:8000",
});

// Check system health
const health = await client.getHealth();
console.log("Status:", health.status);

// Solve a CP-SAT schedule
const solution = await client.schedules.optimize({
  tenant_id: "acme-corp",
  horizon: { start: 0, end: 480 },
  tasks: [
    { id: "T1", duration: 60, required_resources: ["M1"] },
    { id: "T2", duration: 90, required_resources: ["M1"] },
  ],
  resources: [
    { id: "M1", name: "CNC Milling Machine" },
  ],
  precedences: [
    { predecessor_id: "T1", successor_id: "T2" },
  ],
  strategy: "MINIMIZE_MAKESPAN",
});

console.log("Makespan:", solution.makespan);
```

---

## 3. Client Capabilities

### Model CRUD
- `client.scheduleRuns`: `list()`, `get()`, `update()`, `delete()`
- `client.optimizationJobs`: `list()`, `get()`
- `client.scenarios`: `list()`, `get()`, `create()`, `run()`, `generate()`
- `client.disruptionLogs`: `list()`, `get()`, `create()`

### Temporal Workflows & HITL
- `client.temporal.dispatch(payload)`: Dispatch async optimization workflow.
- `client.temporal.getStatus(workflowId)`: Poll progress basis points and objective bounds.
- `client.temporal.getApprovalState(workflowId)`: Query supervisor review state.
- `client.temporal.sendApprovalSignal(workflowId, { decision, notes })`: Signal approval or rejection.

### Solver Core & Simulation
- `client.schedules.optimize(payload)`: Synchronous CP-SAT optimization.
- `client.schedules.validate(payload)`: Deterministic constraint validation.
- `client.simulations.simulateDisruption(payload)`: Disruption impact analysis and reactive rescheduling.

### Visualizers & Calendars
- `client.visualizations.getStripboardHtml(payload)`
- `client.visualizations.getStripboardSvg(payload)`
- `client.visualizations.getDoodMatrix(payload)`
- `client.visualizations.getGanttSvg(payload)`
- `client.visualizations.getProductionReport(payload)`
- `client.calendars.getAstrologicalBlackouts(payload)`
- `client.calendars.getShiftOperationalHours(payload)`

### Domain Adapters
- `client.adapters.filmProduction(payload)`
- `client.adapters.manufacturing(payload)`
- `client.adapters.workforce(payload)`
- `client.adapters.marketingFlighting(payload)`
- `client.adapters.academicTimetables(payload)`
- `client.adapters.eventRunSheets(payload)`
