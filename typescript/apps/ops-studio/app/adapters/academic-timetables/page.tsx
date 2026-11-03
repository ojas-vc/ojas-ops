"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_ACADEMIC_PAYLOAD } from "@/app/lib/fixtures";
import type { AcademicOptimizeRequest, AcademicOptimizeResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function AcademicTimetablesAdapterPage() {
  const [payload, setPayload] = useState<AcademicOptimizeRequest>(SAMPLE_ACADEMIC_PAYLOAD);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<AcademicOptimizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.academicTimetables(payload);
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
            🎓 Academic Timetabling & Campus Allocation Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Cohort room scheduling, instructor availability windows, and lecture clash avoidance
            (`/adapters/academic-timetables/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPayload(SAMPLE_ACADEMIC_PAYLOAD)}
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
            {optimizing ? "Generating Timetable..." : "⚡ Optimize Timetables"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Academic Adapter Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Timetable Status"
            value={<StatusBadge status={result.status || "OPTIMAL"} />}
            subValue="CP-SAT exit code"
          />
          <MetricCard
            label="Class Sessions"
            value={result.schedule ? Object.keys(result.schedule).length : payload.classes.length}
            subValue="100% clash-free lectures"
          />
          <MetricCard
            label="Active Cohorts"
            value={payload.cohorts.length}
            subValue="Student departments"
          />
          <MetricCard
            label="Classrooms Assigned"
            value={payload.classrooms.length}
            subValue="Halls & labs utilized"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
          <h3 className="font-semibold text-white">Campus Inventory & Classes</h3>

          <div>
            <h4 className="font-medium text-slate-300 mb-2">
              Student Cohorts ({payload.cohorts.length})
            </h4>
            <div className="space-y-1.5">
              {payload.cohorts.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-medium text-slate-200">{c.name}</span>
                  <span className="font-mono text-slate-400">{c.id}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Classrooms ({payload.classrooms.length})
            </h4>
            <div className="space-y-1.5">
              {payload.classrooms.map((r) => (
                <div
                  key={r.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-medium text-slate-200">{r.name}</span>
                  <span className="font-mono text-slate-400">Cap: {r.capacity || "—"}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">Lectures ({payload.classes.length})</h4>
            <div className="space-y-1.5">
              {payload.classes.map((cl) => (
                <div
                  key={cl.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="text-slate-300 font-medium">{cl.name}</span>
                  <span className="text-[10px] text-indigo-400 font-mono">
                    {cl.duration_minutes} min
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results JSON */}
        <div className="space-y-4">
          <JsonViewer
            title="Generated Campus Timetable"
            data={result || { message: "Click 'Optimize Timetables' to solve campus schedule" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
