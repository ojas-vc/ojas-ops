"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_SCHEDULE_PAYLOAD } from "@/app/lib/fixtures";
import type { OptimizeScheduleRequest, OptimizeScheduleResponse } from "@ojas-ops/sdk";
import { GanttChart, JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function SchedulesPage() {
  const [payload, setPayload] = useState<OptimizeScheduleRequest>(SAMPLE_SCHEDULE_PAYLOAD);
  const [solving, setSolving] = useState(false);
  const [result, setResult] = useState<OptimizeScheduleResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSolve = async () => {
    setSolving(true);
    setError(null);
    try {
      const res = await client.schedules.optimize(payload);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSolving(false);
    }
  };

  // Convert result tasks into Gantt-compatible items
  const ganttTasks = result?.tasks
    ? Object.entries(result.tasks).map(([taskId, t]) => ({
        id: taskId,
        name: taskId,
        start: t.start,
        end: t.end,
        resource: t.assigned_resources?.[0] || "R1",
      }))
    : [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">CP-SAT Solver Workbench</h1>
          <p className="mt-1 text-sm text-slate-400">
            Synchronous constraint programming optimization engine (`/schedules/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/schedules/validate"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            Schedule Validator ✔
          </Link>
          <button
            type="button"
            onClick={() => setPayload(SAMPLE_SCHEDULE_PAYLOAD)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
          >
            Reset Fixture
          </button>
          <button
            type="button"
            disabled={solving}
            onClick={handleSolve}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            {solving ? "Solving..." : "⚡ Execute Solve"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Solver Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* Solver KPIs */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Solver Status"
            value={<StatusBadge status={result.status || "UNKNOWN"} />}
            subValue="CP-SAT exit code"
          />
          <MetricCard
            label="Makespan"
            value={result.makespan != null ? `${result.makespan} min` : "—"}
            subValue="Final project completion time"
          />
          <MetricCard
            label="Scheduled Tasks"
            value={`${result.tasks_scheduled_count || 0} / ${payload.tasks.length}`}
            subValue="Assigned operations"
          />
          <MetricCard
            label="Solve Time"
            value={
              result.metrics?.solve_time_seconds != null
                ? `${result.metrics.solve_time_seconds.toFixed(3)}s`
                : result.metrics?.wall_time != null
                  ? `${result.metrics.wall_time.toFixed(3)}s`
                  : "—"
            }
            subValue="Wall clock execution"
          />
        </div>
      )}

      {/* Visual Gantt Chart of Solution */}
      {ganttTasks.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
          <h2 className="text-base font-bold text-white">Solution Gantt Timeline</h2>
          <GanttChart
            tasks={ganttTasks}
            horizonStart={payload.horizon.start}
            horizonEnd={payload.horizon.end}
          />
        </div>
      )}

      {/* Interactive Controls & JSON Payload */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Workbench Parameters */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 space-y-5">
          <h3 className="text-sm font-semibold text-white">Solver Parameters</h3>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Tenant ID</label>
              <input
                type="text"
                value={payload.tenant_id}
                onChange={(e) => setPayload({ ...payload, tenant_id: e.target.value })}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Project ID</label>
              <input
                type="text"
                value={payload.project_id}
                onChange={(e) => setPayload({ ...payload, project_id: e.target.value })}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Horizon Start</label>
              <input
                type="number"
                value={payload.horizon.start}
                onChange={(e) =>
                  setPayload({
                    ...payload,
                    horizon: { ...payload.horizon, start: Number(e.target.value) },
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Horizon End</label>
              <input
                type="number"
                value={payload.horizon.end}
                onChange={(e) =>
                  setPayload({
                    ...payload,
                    horizon: { ...payload.horizon, end: Number(e.target.value) },
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Strategy</label>
              <select
                value={payload.strategy || "balanced"}
                onChange={(e) =>
                  setPayload({
                    ...payload,
                    strategy: e.target.value as "fast" | "balanced" | "deep_optimal",
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
              >
                <option value="fast">Fast Heuristic</option>
                <option value="balanced">Balanced</option>
                <option value="deep_optimal">Deep Optimal</option>
              </select>
            </div>
          </div>

          <div className="text-xs">
            <div className="flex justify-between mb-1">
              <label className="text-slate-400">Max Time Limit</label>
              <span className="font-mono text-indigo-400">{payload.max_time_seconds || 5}s</span>
            </div>
            <input
              type="range"
              min={1}
              max={30}
              step={1}
              value={payload.max_time_seconds || 5}
              onChange={(e) => setPayload({ ...payload, max_time_seconds: Number(e.target.value) })}
              className="w-full"
            />
          </div>

          <div className="border-t border-slate-800 pt-4 text-xs">
            <div className="font-medium text-slate-300 mb-2">
              Configured Resources ({payload.resources.length})
            </div>
            <div className="space-y-1.5">
              {payload.resources.map((r) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-mono text-slate-300">{r.id}</span>
                  <span className="text-slate-400">{r.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">Cap: {r.capacity}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-4 text-xs">
            <div className="font-medium text-slate-300 mb-2">
              Configured Tasks ({payload.tasks.length})
            </div>
            <div className="space-y-1.5">
              {payload.tasks.map((t) => (
                <div
                  key={t.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-mono text-slate-300">{t.id}</span>
                  <span className="text-slate-400">{t.name}</span>
                  <span className="text-[10px] text-indigo-400 font-mono">{t.duration} min</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Raw JSON Inspector */}
        <div className="space-y-4">
          <JsonViewer title="Active Solve Request Payload" data={payload} initialExpanded={false} />
          <JsonViewer
            title="Solver Response Payload"
            data={result || { message: "Solve has not been executed yet" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
