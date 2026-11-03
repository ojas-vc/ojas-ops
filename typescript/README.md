# Ojas Ops — TypeScript Workspace

Polyglot TypeScript workspace for **Ojas Ops**: frontend applications, shared UI primitives, and typed SDK client libraries powered by `pnpm`, [Turborepo](https://turbo.build/), and [Biome](https://biomejs.dev/).

---

## 1. Monorepo Structure

```text
typescript/
├── pnpm-workspace.yaml        # Workspace configuration
├── package.json               # Monorepo scripts and devDependencies
├── turbo.json                 # Turborepo task pipeline definition
├── biome.json                 # Biome formatting and linting rules
├── tsconfig.base.json         # Shared strict TypeScript configuration
├── packages/
│   ├── sdk/                   # @ojas-ops/sdk: Strongly-typed client for Ojas Ops API
│   └── ui/                    # @ojas-ops/ui: Accessible React 19 UI components
└── apps/
    └── ops-studio/            # @ojas-ops/studio: Next.js 16 interactive operations studio
```

---

## 2. Requirements & Setup

- **Node.js**: `>=22.0.0` (Node 22.14 LTS recommended)
- **Package Manager**: [pnpm](https://pnpm.io/) `>=10.0.0`

```bash
cd typescript

# Install dependencies across all packages and apps
pnpm install
```

---

## 3. Available Workspaces

### `@ojas-ops/sdk` (`packages/sdk`)
Strongly typed TypeScript client covering all 24 Ojas Ops backend endpoints with msgspec/JSON serialization parity.
- Models: `ScheduleRunRecord`, `OptimizationJobRecord`, `ScenarioRecordDTO`, `DisruptionLogRecord`
- Solver schemas: `SolveScheduleRequest`, `ScheduleSolution`, `ValidateScheduleRequest`, `ScheduleValidationResult`
- Workflows & HITL: `WorkflowStatusResponse`, `WorkflowSignalRequest`, `ApprovalStateResponse`
- Domain payloads: Film production, manufacturing, workforce rostering, marketing flighting, academic timetabling, and event run sheets.

### `@ojas-ops/ui` (`packages/ui`)
Reusable React 19 and Tailwind CSS UI primitives:
- `GanttChart`: Dynamic multi-lane timeline with customizable timescale.
- `MetricCard`: KPI presentation tile with variance formatting.
- `DataTable`: Generic paginated table with sorting and custom column renderers.
- `JsonViewer`: Collapsible, color-coded interactive JSON explorer with clipboard copy.
- `StatusBadge`: Semantically styled status indicator pills.
- `WorkflowProgressBar`: Animated multi-state progress indicator for long-running workflows.
- `SvgRenderer`: Inline vector rendering with responsive zoom and PNG/SVG download.
- `HtmlPreviewModal`: Safe sandboxed iframe modal preview with dedicated printing.
- `ViolationBadge`: Severity-based badges for constraint validation violations.

### `@ojas-ops/studio` (`apps/ops-studio`)
Interactive Next.js 16 App Router application for operations research engineers, domain planners, and production supervisors.
- Default port: `5900`
- Runs CP-SAT optimization directly against the Django-Bolt backend or local fixtures.

---

## 4. Development & Build Commands

Run tasks across the entire TypeScript workspace using Turborepo:

```bash
# Start Next.js development server
pnpm dev

# Check TypeScript types across all packages (noEmit)
pnpm check-types

# Lint all packages using Biome
pnpm lint

# Automatically format all packages with Biome
pnpm format

# Build all packages and applications for production
pnpm build
```

