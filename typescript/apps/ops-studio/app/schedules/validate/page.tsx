"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_VALIDATE_PAYLOAD } from "@/app/lib/fixtures";
import type { ValidateScheduleResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, ViolationBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function ScheduleValidatorPage() {
  const [payloadText, setPayloadText] = useState(JSON.stringify(SAMPLE_VALIDATE_PAYLOAD, null, 2));
  const [validating, setValidating] = useState(false);
  const [report, setReport] = useState<ValidateScheduleResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    setValidating(true);
    setError(null);
    try {
      const parsed = JSON.parse(payloadText);
      const res = await client.schedules.validate(parsed);
      setReport(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setValidating(false);
    }
  };

  const violations = report?.report?.violations || [];
  const hardViolations = violations.filter((v) => v.severity === "HARD");
  const softViolations = violations.filter((v) => v.severity === "SOFT");

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/schedules"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Solver Workbench
          </Link>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Deterministic Schedule Validator
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Verify temporal feasibility, precedence compliance, and resource capacity limits
            (`/schedules/validate`).
          </p>
        </div>

        <button
          type="button"
          disabled={validating}
          onClick={handleValidate}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
        >
          {validating ? "Validating..." : "✔ Validate Schedule"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Validation Request Failed</div>
          <div>{error}</div>
        </div>
      )}

      {/* Report Summary Banner */}
      {report && (
        <div
          className={`rounded-2xl border p-5 ${
            report.is_valid
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
              : "border-rose-500/40 bg-rose-500/10 text-rose-200"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xl font-bold">
              {report.is_valid
                ? "✓ Schedule Feasible & Valid"
                : "✕ Infeasible: Constraint Violations Detected"}
            </span>
            <span className="font-mono text-xs">Violations: {violations.length}</span>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      {report && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Schedule Verdict"
            value={report.is_valid ? "VALID" : "INVALID"}
            subValue="Overall feasibility"
          />
          <MetricCard
            label="Total Violations"
            value={violations.length}
            subValue="Reported discrepancies"
          />
          <MetricCard
            label="Hard Violations"
            value={hardViolations.length}
            subValue="Infeasible breaches"
          />
          <MetricCard
            label="Soft Warnings"
            value={softViolations.length}
            subValue="Optimization penalties"
          />
        </div>
      )}

      {/* Violations List */}
      {violations.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
          <h2 className="text-base font-bold text-white">Violations Breakdown</h2>
          <div className="space-y-3">
            {violations.map((v, i) => (
              <div
                key={`violation-${v.constraint_type || i}`}
                className="flex items-start justify-between rounded-xl border border-slate-800 bg-slate-950 p-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <ViolationBadge
                      type={v.constraint_type || "CONSTRAINT_BREACH"}
                      severity={v.severity === "HARD" ? "critical" : "warning"}
                    />
                    <span className="font-semibold text-slate-200">
                      {v.message || v.constraint_type}
                    </span>
                  </div>
                  {v.task_ids && v.task_ids.length > 0 && (
                    <div className="text-slate-400 font-mono text-[11px]">
                      Task IDs: {v.task_ids.join(", ")}{" "}
                      {v.resource_ids?.length ? `• Resources: ${v.resource_ids.join(", ")}` : ""}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* JSON Editor & Raw Output */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300">
              Schedule Verification Payload
            </label>
            <button
              type="button"
              onClick={() => setPayloadText(JSON.stringify(SAMPLE_VALIDATE_PAYLOAD, null, 2))}
              className="text-[11px] text-indigo-400 hover:underline"
            >
              Reset to Sample
            </button>
          </div>
          <textarea
            rows={18}
            value={payloadText}
            onChange={(e) => setPayloadText(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300">
            Validation Report Inspector
          </label>
          <JsonViewer
            title="Raw Validation Report"
            data={report || { message: "Click 'Validate Schedule' to evaluate" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
