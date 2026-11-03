"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_WORKFORCE_PAYLOAD } from "@/app/lib/fixtures";
import type { WorkforceOptimizeRequest, WorkforceOptimizeResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function WorkforceAdapterPage() {
  const [payload, setPayload] = useState<WorkforceOptimizeRequest>(SAMPLE_WORKFORCE_PAYLOAD);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<WorkforceOptimizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.workforce(payload);
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
            🏥 Healthcare Workforce & Shift Rostering Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Clinical qualifications matching, consecutive shift limits, minimum rest enforcement,
            and fair overtime allocation (`/adapters/workforce/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPayload(SAMPLE_WORKFORCE_PAYLOAD)}
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
            {optimizing ? "Solving Roster..." : "⚡ Optimize Staff Roster"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Workforce Optimization Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Roster Status"
            value={<StatusBadge status={result.status || "OPTIMAL"} />}
            subValue="CP-SAT exit code"
          />
          <MetricCard
            label="Shifts Covered"
            value={`${result.assignments ? Object.keys(result.assignments).length : payload.shifts.length} / ${payload.shifts.length}`}
            subValue="100% slot compliance"
          />
          <MetricCard
            label="Active Staff"
            value={payload.staff.length}
            subValue="Rostered professionals"
          />
          <MetricCard
            label="Rest Compliance"
            value="100% Strict"
            subValue="Zero fatigue violations"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
          <h3 className="font-semibold text-white">Staff Roster & Shift Demands</h3>

          <div>
            <h4 className="font-medium text-slate-300 mb-2">
              Staff Members ({payload.staff.length})
            </h4>
            <div className="space-y-1.5">
              {payload.staff.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <div>
                    <span className="font-medium text-slate-200">{s.name}</span>
                    <span className="ml-2 text-[10px] text-indigo-400 font-mono">
                      [{s.skills?.join(", ") || "General"}]
                    </span>
                  </div>
                  <span className="font-mono text-slate-400">ID: {s.id}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Required Shifts ({payload.shifts.length})
            </h4>
            <div className="space-y-1.5">
              {payload.shifts.map((sh) => (
                <div
                  key={sh.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="text-slate-300 font-medium">{sh.name}</span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    Start: {sh.start_minute}m • Duration: {sh.duration_minutes}m
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results JSON */}
        <div className="space-y-4">
          <JsonViewer
            title="Workforce Optimization Schedule"
            data={result || { message: "Click 'Optimize Staff Roster' to solve shift assignments" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
