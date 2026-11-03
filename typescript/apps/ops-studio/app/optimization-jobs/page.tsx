"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_SCHEDULE_PAYLOAD } from "@/app/lib/fixtures";
import type { OptimizationJobRecord } from "@ojas-ops/sdk";
import { DataTable, StatusBadge, WorkflowProgressBar } from "@ojas-ops/ui";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function OptimizationJobsPage() {
  const [jobs, setJobs] = useState<OptimizationJobRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dispatch modal
  const [showDispatchModal, setShowDispatchModal] = useState(false);
  const [dispatchType, setDispatchType] = useState<"standard" | "hitl">("standard");
  const [dispatchPayload, setDispatchPayload] = useState(
    JSON.stringify(SAMPLE_SCHEDULE_PAYLOAD, null, 2),
  );
  const [dispatching, setDispatching] = useState(false);
  const [dispatchResult, setDispatchResult] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.optimizationJobs.list();
      setJobs(res.items || []);
      setTotal(res.total || 0);
    } catch (err: unknown) {
      console.warn("Failed to fetch jobs:", err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchJobs();
    }, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchJobs]);

  const handleDispatch = async () => {
    setDispatching(true);
    setDispatchResult(null);
    try {
      const parsed = JSON.parse(dispatchPayload);
      const res =
        dispatchType === "hitl"
          ? await client.optimizationJobs.dispatchHitl(parsed)
          : await client.optimizationJobs.dispatch(parsed);

      setDispatchResult(
        `Dispatched successfully! Workflow ID: ${res.workflow_id} (Status: ${res.status})`,
      );
      fetchJobs();
    } catch (err) {
      alert(`Dispatch failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setDispatching(false);
    }
  };

  const handleDelete = async (id: number | string) => {
    if (!confirm(`Delete job record #${id}?`)) return;
    try {
      await client.optimizationJobs.delete(id);
      fetchJobs();
    } catch (err) {
      alert(`Delete failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const columns = [
    {
      key: "id",
      header: "Job ID",
      render: (j: OptimizationJobRecord) => (
        <span className="font-mono text-xs text-slate-300 font-semibold">#{j.id}</span>
      ),
    },
    {
      key: "temporal_workflow_id",
      header: "Temporal Workflow ID",
      render: (j: OptimizationJobRecord) => (
        <div>
          <span className="font-mono text-xs text-indigo-400 font-medium">
            {j.temporal_workflow_id}
          </span>
          {j.tenant_id && (
            <div className="text-[10px] text-slate-500 font-mono">Tenant: {j.tenant_id}</div>
          )}
        </div>
      ),
    },
    {
      key: "status",
      header: "Workflow Status",
      render: (j: OptimizationJobRecord) => <StatusBadge status={j.status || "UNKNOWN"} />,
    },
    {
      key: "progress",
      header: "Progress",
      render: (j: OptimizationJobRecord) => (
        <div className="w-36">
          <WorkflowProgressBar basisPoints={j.progress_basis_points || 0} />
        </div>
      ),
    },
    {
      key: "incumbent",
      header: "Incumbent / Bound",
      render: (j: OptimizationJobRecord) => (
        <div className="text-xs font-mono text-slate-300">
          <div>Inc: {j.incumbent_objective ?? "—"}</div>
          <div className="text-slate-500 text-[10px]">Bound: {j.best_bound ?? "—"}</div>
        </div>
      ),
    },
    {
      key: "created_at",
      header: "Started",
      render: (j: OptimizationJobRecord) => (
        <span className="text-xs text-slate-400">
          {j.created_at ? new Date(j.created_at).toLocaleTimeString() : "—"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (j: OptimizationJobRecord) => (
        <div className="flex items-center gap-2">
          {j.status === "AWAITING_APPROVAL" || j.status === "PENDING" ? (
            <Link
              href={`/optimization-jobs/hitl/${j.temporal_workflow_id}`}
              className="rounded bg-amber-500/20 border border-amber-500/40 px-2.5 py-1 text-xs font-semibold text-amber-300 hover:bg-amber-500/30 transition"
            >
              Review HITL
            </Link>
          ) : (
            <Link
              href={`/optimization-jobs/hitl/${j.temporal_workflow_id}`}
              className="rounded bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
            >
              Inspect
            </Link>
          )}
          <button
            type="button"
            onClick={() => handleDelete(j.id)}
            className="rounded bg-rose-500/10 px-2 py-1 text-xs font-medium text-rose-400 hover:bg-rose-500/20"
          >
            ✕
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Temporal Optimization Workflows
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Distributed asynchronous CP-SAT solver workflows, bound convergence, and
            Human-in-the-Loop approval queues {total > 0 && `(${total} total tracked)`}.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded text-indigo-600 focus:ring-0"
            />
            Live Polling (3s)
          </label>
          <button
            type="button"
            onClick={fetchJobs}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={() => setShowDispatchModal(true)}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition"
          >
            🚀 Dispatch Async Job
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Workflow Service Notice</div>
          <div>{error}</div>
        </div>
      )}

      {/* Table */}
      <DataTable
        columns={columns}
        data={jobs}
        isLoading={loading}
        emptyMessage="No active or historical optimization workflows recorded. Click 'Dispatch Async Job' to start one."
      />

      {/* Modal: Dispatch Job */}
      {showDispatchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white">Dispatch Temporal Solver Workflow</h2>
              <button
                type="button"
                onClick={() => setShowDispatchModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="flex gap-4 border-b border-slate-800 pb-3 text-xs">
              <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                <input
                  type="radio"
                  name="dispatchType"
                  value="standard"
                  checked={dispatchType === "standard"}
                  onChange={() => setDispatchType("standard")}
                  className="text-indigo-600 focus:ring-0"
                />
                Standard Async Workflow (`/optimization-jobs/dispatch`)
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-amber-400 font-medium">
                <input
                  type="radio"
                  name="dispatchType"
                  value="hitl"
                  checked={dispatchType === "hitl"}
                  onChange={() => setDispatchType("hitl")}
                  className="text-amber-500 focus:ring-0"
                />
                Human-in-the-Loop Approval Workflow (`/optimization-jobs/hitl-dispatch`)
              </label>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium text-slate-300">
                  Optimization Request JSON
                </label>
                <button
                  type="button"
                  onClick={() =>
                    setDispatchPayload(JSON.stringify(SAMPLE_SCHEDULE_PAYLOAD, null, 2))
                  }
                  className="text-[11px] text-indigo-400 hover:underline"
                >
                  Reset to Sample Payload
                </button>
              </div>
              <textarea
                rows={12}
                value={dispatchPayload}
                onChange={(e) => setDispatchPayload(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            {dispatchResult && (
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-300">
                {dispatchResult}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowDispatchModal(false)}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700"
              >
                Close
              </button>
              <button
                type="button"
                disabled={dispatching}
                onClick={handleDispatch}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                {dispatching ? "Submitting to Queue..." : "Confirm & Dispatch"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
