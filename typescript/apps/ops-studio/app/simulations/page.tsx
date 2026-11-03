"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_RESCHEDULE_PAYLOAD, SAMPLE_SIMULATION_PAYLOAD } from "@/app/lib/fixtures";
import type { RescheduleResponse, SimulateDisruptionResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function SimulationsPage() {
  const [activeTab, setActiveTab] = useState<"disruption" | "reschedule">("disruption");

  // Disruption simulation state
  const [disruptionPayload, setDisruptionPayload] = useState(
    JSON.stringify(SAMPLE_SIMULATION_PAYLOAD, null, 2),
  );
  const [simulating, setSimulating] = useState(false);
  const [disruptionResult, setDisruptionResult] = useState<SimulateDisruptionResponse | null>(null);
  const [disruptionError, setDisruptionError] = useState<string | null>(null);

  // Rescheduling state
  const [reschedulePayload, setReschedulePayload] = useState(
    JSON.stringify(SAMPLE_RESCHEDULE_PAYLOAD, null, 2),
  );
  const [rescheduling, setRescheduling] = useState(false);
  const [rescheduleResult, setRescheduleResult] = useState<RescheduleResponse | null>(null);
  const [rescheduleError, setRescheduleError] = useState<string | null>(null);

  const handleSimulateDisruption = async () => {
    setSimulating(true);
    setDisruptionError(null);
    try {
      const parsed = JSON.parse(disruptionPayload);
      const res = await client.simulations.simulateDisruptions(parsed);
      setDisruptionResult(res);
    } catch (err) {
      setDisruptionError(err instanceof Error ? err.message : String(err));
    } finally {
      setSimulating(false);
    }
  };

  const handleReschedule = async () => {
    setRescheduling(true);
    setRescheduleError(null);
    try {
      const parsed = JSON.parse(reschedulePayload);
      const res = await client.simulations.reschedule(parsed);
      setRescheduleResult(res);
    } catch (err) {
      setRescheduleError(err instanceof Error ? err.message : String(err));
    } finally {
      setRescheduling(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Disruption Simulator & Reactive Rescheduler
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Inject operational anomalies, analyze delay ripple effects, and execute
            stability-penalized warm-start reschedules.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/simulations/logs"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            📋 Disruption Audit Logs
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-3 border-b border-slate-800 pb-3">
        <button
          type="button"
          onClick={() => setActiveTab("disruption")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "disruption"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          1. Disruption Impact Simulator (`/simulations/disruptions`)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("reschedule")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "reschedule"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          2. Reactive Rescheduler (`/simulations/reschedule`)
        </button>
      </div>

      {/* Tab 1: Disruption Simulator */}
      {activeTab === "disruption" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Simulate Operational Disruptions</h2>
            <button
              type="button"
              disabled={simulating}
              onClick={handleSimulateDisruption}
              className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
            >
              {simulating ? "Simulating Ripple Effect..." : "💥 Simulate Disruption"}
            </button>
          </div>

          {disruptionError && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
              <div className="font-semibold">Simulation Error</div>
              <div>{disruptionError}</div>
            </div>
          )}

          {disruptionResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <MetricCard
                  label="Original Makespan"
                  value={
                    disruptionResult.original_makespan != null
                      ? `${disruptionResult.original_makespan} min`
                      : "—"
                  }
                  subValue="Baseline schedule"
                />
                <MetricCard
                  label="New Makespan"
                  value={
                    disruptionResult.new_makespan != null
                      ? `${disruptionResult.new_makespan} min`
                      : "—"
                  }
                  subValue={
                    disruptionResult.new_makespan && disruptionResult.original_makespan
                      ? `+${disruptionResult.new_makespan - disruptionResult.original_makespan} min delay`
                      : "Projected end"
                  }
                />
                <MetricCard
                  label="Affected Tasks"
                  value={disruptionResult.affected_tasks?.length || 0}
                  subValue="Tasks displaced"
                />
                <MetricCard
                  label="Feasibility"
                  value={disruptionResult.is_feasible !== false ? "FEASIBLE" : "INFEASIBLE"}
                  subValue="Post-disruption status"
                />
              </div>

              {disruptionResult.affected_tasks && disruptionResult.affected_tasks.length > 0 && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 text-xs">
                  <div className="font-semibold text-slate-200 mb-2">
                    Displaced / Shifted Tasks:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {disruptionResult.affected_tasks.map((tid) => (
                      <span
                        key={tid}
                        className="rounded bg-amber-500/20 border border-amber-500/30 px-2.5 py-1 font-mono text-amber-300"
                      >
                        {tid}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-300">
                  Simulation Payload JSON
                </label>
                <button
                  type="button"
                  onClick={() =>
                    setDisruptionPayload(JSON.stringify(SAMPLE_SIMULATION_PAYLOAD, null, 2))
                  }
                  className="text-[11px] text-indigo-400 hover:underline"
                >
                  Reset Sample
                </button>
              </div>
              <textarea
                rows={16}
                value={disruptionPayload}
                onChange={(e) => setDisruptionPayload(e.target.value)}
                className="w-full rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Simulation Response</label>
              <JsonViewer
                title="Disruption Simulation Output"
                data={disruptionResult || { message: "Run simulation to see impact data" }}
                initialExpanded={true}
              />
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Reactive Rescheduler */}
      {activeTab === "reschedule" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">
              Reactive Re-Optimization & Schedule Repair
            </h2>
            <button
              type="button"
              disabled={rescheduling}
              onClick={handleReschedule}
              className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
            >
              {rescheduling ? "Re-Optimizing Plan..." : "🔄 Execute Reschedule"}
            </button>
          </div>

          {rescheduleError && (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
              <div className="font-semibold">Reschedule Error</div>
              <div>{rescheduleError}</div>
            </div>
          )}

          {rescheduleResult && (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <MetricCard
                label="Repaired Makespan"
                value={rescheduleResult.makespan != null ? `${rescheduleResult.makespan} min` : "—"}
                subValue="Optimized repaired span"
              />
              <MetricCard
                label="Repair Status"
                value={rescheduleResult.status || "OPTIMAL"}
                subValue="Convergence verdict"
              />
              <MetricCard
                label="Repaired Tasks"
                value={Object.keys(rescheduleResult.result || {}).length}
                subValue="Tasks adjusted"
              />
              <MetricCard
                label="Solve Duration"
                value={
                  rescheduleResult.solve_time_seconds != null
                    ? `${rescheduleResult.solve_time_seconds.toFixed(3)}s`
                    : "—"
                }
                subValue="Repair compute time"
              />
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-300">
                  Reschedule Request JSON (Includes Stability Weight)
                </label>
                <button
                  type="button"
                  onClick={() =>
                    setReschedulePayload(JSON.stringify(SAMPLE_RESCHEDULE_PAYLOAD, null, 2))
                  }
                  className="text-[11px] text-indigo-400 hover:underline"
                >
                  Reset Sample
                </button>
              </div>
              <textarea
                rows={16}
                value={reschedulePayload}
                onChange={(e) => setReschedulePayload(e.target.value)}
                className="w-full rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">
                Repaired Schedule Output
              </label>
              <JsonViewer
                title="Reschedule Response"
                data={
                  rescheduleResult || { message: "Execute reschedule to view repaired schedule" }
                }
                initialExpanded={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
