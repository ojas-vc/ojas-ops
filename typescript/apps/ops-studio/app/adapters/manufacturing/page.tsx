"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_MANUFACTURING_PAYLOAD } from "@/app/lib/fixtures";
import type { ManufacturingOptimizeRequest, ManufacturingOptimizeResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function ManufacturingAdapterPage() {
  const [payload, setPayload] = useState<ManufacturingOptimizeRequest>(
    SAMPLE_MANUFACTURING_PAYLOAD,
  );
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<ManufacturingOptimizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.manufacturing(payload);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
            <Link href="/" className="hover:underline">
              Dashboard
            </Link>
            <span>/</span>
            <span>Domain Adapters</span>
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            ⚙️ Manufacturing Job-Shop & Setup Changeover Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Multi-stage machine routing, sequence-dependent changeovers, and family setup matrix
            minimization (`/adapters/manufacturing/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPayload(SAMPLE_MANUFACTURING_PAYLOAD)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
          >
            Reset Fixture
          </button>
          <button
            type="button"
            disabled={optimizing}
            onClick={handleOptimize}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            {optimizing ? "Solving Shop Floor..." : "⚡ Optimize Job-Shop"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Manufacturing Adapter Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Solver Status"
            value={<StatusBadge status={result.status || "OPTIMAL"} />}
            subValue="CP-SAT exit code"
          />
          <MetricCard
            label="Makespan"
            value={result.makespan != null ? `${result.makespan} min` : "—"}
            subValue="Total factory production time"
          />
          <MetricCard
            label="Solve Duration"
            value={
              result.solve_time_seconds != null
                ? `${result.solve_time_seconds.toFixed(3)}s`
                : "Optimized"
            }
            subValue="CP-SAT compute time"
          />
          <MetricCard
            label="Machine Count"
            value={payload.machines.length}
            subValue="Active workstations"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
          <h3 className="font-semibold text-white">Shop Floor Fleet & Jobs</h3>

          <div>
            <h4 className="font-medium text-slate-300 mb-2">
              Workstations ({payload.machines.length})
            </h4>
            <div className="space-y-1.5">
              {payload.machines.map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-medium text-slate-200">{m.name}</span>
                  <span className="font-mono text-slate-400">Speed: {m.speed_factor || 1.0}x</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Production Jobs ({payload.jobs.length})
            </h4>
            <div className="space-y-2">
              {payload.jobs.map((j) => (
                <div
                  key={j.id}
                  className="rounded bg-slate-950 p-3 border border-slate-800 space-y-1"
                >
                  <div className="flex justify-between font-medium text-slate-200">
                    <span>{j.name}</span>
                    <span className="text-[10px] uppercase text-indigo-400 font-mono">
                      Priority: {j.priority || 1}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {j.operations.length} operations:{" "}
                    {j.operations
                      .map((op) => `${op.required_machine_id} (${op.duration_minutes}m)`)
                      .join(" → ")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results JSON */}
        <div className="space-y-4">
          <JsonViewer
            title="Manufacturing Optimization Solution"
            data={result || { message: "Click 'Optimize Job-Shop' to compute shop schedule" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
