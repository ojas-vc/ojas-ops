# @ojas-ops/ui — Operations Research UI Primitives

Reusable, accessible React 19 UI components built for operations research, scheduling workbenches, constraint violation inspectors, and Gantt charts.

---

## 1. Components Overview

### `GanttChart`
Renders dynamic, multi-lane Gantt timelines partitioned by resource lanes or tasks.
```tsx
import { GanttChart } from "@ojas-ops/ui";

<GanttChart
  solution={solution}
  resources={resources}
  timeScale={15}
  onTaskClick={(taskId) => console.log("Task clicked:", taskId)}
/>
```

### `MetricCard`
KPI display tile with title, primary metric, contextual subtitle, and optional status variant (`default`, `success`, `warning`, `danger`).
```tsx
import { MetricCard } from "@ojas-ops/ui";

<MetricCard
  label="Makespan"
  value="480 min"
  subValue="Optimal completion horizon"
  variant="success"
/>
```

### `DataTable<T>`
Generic, accessible data table supporting pagination, custom cell rendering, and empty-state handling.
```tsx
import { DataTable } from "@ojas-ops/ui";

<DataTable
  columns={[
    { key: "id", header: "Run ID" },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
  ]}
  data={runs}
  loading={isLoading}
/>
```

### `JsonViewer`
Interactive collapsible JSON explorer with nested tree toggling and one-click copy to clipboard.
```tsx
import { JsonViewer } from "@ojas-ops/ui";

<JsonViewer data={solutionPayload} initialExpanded={true} />
```

### `StatusBadge`
Status pill indicator with semantic color tokens for solver states (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `RUNNING`, `COMPLETED`, `FAILED`, `PENDING_REVIEW`).
```tsx
import { StatusBadge } from "@ojas-ops/ui";

<StatusBadge status="OPTIMAL" />
```

### `WorkflowProgressBar`
Progress bar supporting basis points ($0 - 10000$), displaying current percentage and execution state.
```tsx
import { WorkflowProgressBar } from "@ojas-ops/ui";

<WorkflowProgressBar basisPoints={7500} status="OPTIMIZING" />
```

### `SvgRenderer`
Inline vector renderer with interactive scale controls and SVG/PNG file export buttons.
```tsx
import { SvgRenderer } from "@ojas-ops/ui";

<SvgRenderer svgContent={rawSvgString} title="Gantt Timeline Vector" />
```

### `HtmlPreviewModal`
Sandboxed iframe modal for inspecting HTML documents (e.g. call sheet stripboards, production reports) with print button.
```tsx
import { HtmlPreviewModal } from "@ojas-ops/ui";

<HtmlPreviewModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Call Sheet Preview"
  htmlContent={htmlString}
/>
```

### `ViolationBadge`
Severity-based badge for hard/soft constraint violations.
```tsx
import { ViolationBadge } from "@ojas-ops/ui";

<ViolationBadge
  severity="HARD"
  type="RESOURCE_OVERLAP"
  message="Resource M1 is double-booked between T1 and T3"
/>
```

