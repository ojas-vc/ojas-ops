"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_SCENARIO_PAYLOAD } from "@/app/lib/fixtures";
import type { ScenarioExecutionResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function ScenarioRunnerPage() {
  const [payloadText, setPayloadText] = useState(JSON.stringify(SAMPLE_SCENARIO_PAYLOAD, null, 2));
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ScenarioExecutionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      const parsed = JSON.parse(payloadText);
      const res = await client.scenarios.execute(parsed);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/scenarios"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Scenarios Catalog
          </Link>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Declarative Scenario Runner & Golden Verifier
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Execute full scenario JSON specifications against the CP-SAT engine and verify golden
            assertions.
          </p>
        </div>

        <button
          type="button"
          disabled={running}
          onClick={handleRun}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
        >
          {running ? "Solving & Verifying..." : "▶ Execute Scenario"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Execution Failed</div>
          <div>{error}</div>
        </div>
      )}

      {/* Results Header Banner */}
      {result && (
        <div
          className={`rounded-2xl border p-5 ${
            result.is_success
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
              : "border-rose-500/40 bg-rose-500/10 text-rose-200"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xl font-bold">
                {result.is_success ? "✓ Golden Assertions Passed" : "✕ Verification Failed"}
              </span>
              <StatusBadge status={result.status || "UNKNOWN"} />
            </div>
            <span className="font-mono text-xs">Makespan: {result.makespan ?? "—"} min</span>
          </div>
          {result.verification_failures && result.verification_failures.length > 0 && (
            <div className="mt-3 space-y-1 text-xs text-rose-300">
              {result.verification_failures.map((vf, i) => (
                <div key={`failure-${i}`} className="flex items-center gap-2 font-mono">
                  <span>✘</span>
                  <span>{vf}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard label="Result Status" value={result.status} subValue="CP-SAT engine result" />
          <MetricCard
            label="Makespan"
            value={result.makespan != null ? `${result.makespan} min` : "—"}
            subValue="Computed timeline span"
          />
          <MetricCard
            label="Assertions Passed"
            value={result.is_success ? "100%" : "Failed"}
            subValue="Golden criteria check"
          />
        </div>
      )}

      {/* JSON Editor & Raw Output */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300">Scenario Definition JSON</label>
            <button
              type="button"
              onClick={() => setPayloadText(JSON.stringify(SAMPLE_SCENARIO_PAYLOAD, null, 2))}
              className="text-[11px] text-indigo-400 hover:underline"
            >
              Reset to Sample
            </button>
          </div>
          <textarea
            rows={22}
            value={payloadText}
            onChange={(e) => setPayloadText(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300">Execution Result Inspector</label>
          <JsonViewer
            title="Raw Response (/scenarios/execute)"
            data={result || { message: "Click 'Execute Scenario' to view response" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
