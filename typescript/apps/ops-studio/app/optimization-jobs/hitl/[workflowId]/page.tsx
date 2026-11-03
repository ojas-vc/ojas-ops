"use client";

import { client } from "@/app/lib/api";
import type {
  ApprovalStateResponse,
  WorkflowSignalResponse,
  WorkflowStatusResponse,
} from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge, WorkflowProgressBar } from "@ojas-ops/ui";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

export default function HitlReviewPage() {
  const params = useParams();
  const workflowId = params?.workflowId as string;

  const [approvalState, setApprovalState] = useState<ApprovalStateResponse | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reviewer actions
  const [notes, setNotes] = useState("");
  const [reviewerId, setReviewerId] = useState("lead-supervisor");
  const [submitting, setSubmitting] = useState(false);
  const [signalResult, setSignalResult] = useState<WorkflowSignalResponse | null>(null);

  const fetchState = useCallback(async () => {
    if (!workflowId) return;
    setLoading(true);
    setError(null);
    try {
      const [appState, wfStatus] = await Promise.all([
        client.optimizationJobs.getApprovalState(workflowId).catch(() => null),
        client.optimizationJobs.getWorkflowStatus(workflowId).catch(() => null),
      ]);
      setApprovalState(appState);
      setWorkflowStatus(wfStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    fetchState();
  }, [fetchState]);

  const handleDecision = async (signalType: "APPROVE" | "REJECT") => {
    if (!confirm(`Are you sure you want to ${signalType} this schedule proposal?`)) return;
    setSubmitting(true);
    try {
      const res = await client.optimizationJobs.submitApproval(workflowId, {
        decision: signalType === "APPROVE" ? "APPROVED" : "REJECTED",
        notes: notes.trim() || undefined,
      });
      setSignalResult(res);
      fetchState();
    } catch (err) {
      alert(`Approval submission failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400">
        <span className="animate-pulse">Querying Temporal workflow state for {workflowId}...</span>
      </div>
    );
  }

  const effectiveStatus = workflowStatus?.status || approvalState?.status || "UNKNOWN";

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/optimization-jobs"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Optimization Workflows
          </Link>
          <div className="mt-2 flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">HITL Review Console</h1>
            <StatusBadge status={effectiveStatus} />
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Workflow: <span className="font-mono text-slate-300">{workflowId}</span>
          </p>
        </div>

        <button
          type="button"
          onClick={fetchState}
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
        >
          Refresh State
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Workflow Sync Warning</div>
          <div>{error}</div>
        </div>
      )}

      {/* Signal Outcome Alert */}
      {signalResult && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-xs text-emerald-300">
          <div className="font-semibold text-sm">Signal Submitted Successfully</div>
          <div className="mt-1">
            Status: {signalResult.status} • Received At: {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Workflow Status"
          value={effectiveStatus}
          subValue="Current execution stage"
        />
        <MetricCard
          label="Progress"
          value={
            workflowStatus?.progress_basis_points != null
              ? `${(workflowStatus.progress_basis_points / 100).toFixed(1)}%`
              : "100%"
          }
          subValue={
            <WorkflowProgressBar basisPoints={workflowStatus?.progress_basis_points || 10000} />
          }
        />
        <MetricCard
          label="Incumbent Objective"
          value={
            workflowStatus?.incumbent_objective != null
              ? workflowStatus.incumbent_objective.toLocaleString()
              : "Optimal"
          }
          subValue="Current best known cost"
        />
        <MetricCard
          label="Best Bound"
          value={
            workflowStatus?.best_bound != null
              ? workflowStatus.best_bound.toLocaleString()
              : "Converged"
          }
          subValue="Mathematical lower limit"
        />
      </div>

      {/* Supervisor Review Action Box */}
      <div className="rounded-2xl border border-amber-500/30 bg-amber-950/20 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-amber-200">Supervisor Decision Action Bar</h2>
          <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs font-semibold text-amber-400">
            Human-in-the-Loop Sign-off
          </span>
        </div>
        <p className="text-xs text-slate-300">
          Review the proposed schedule solution below. Authorize deployment to active operations, or
          reject with notes to trigger re-optimization.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="block font-medium text-slate-300 mb-1">Reviewer ID / Signature</label>
            <input
              type="text"
              value={reviewerId}
              onChange={(e) => setReviewerId(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-200 focus:border-amber-500 focus:outline-none"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block font-medium text-slate-300 mb-1">
              Decision Notes & Rationales
            </label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Schedule meets shift rest windows; approved for production."
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-200 focus:border-amber-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            type="button"
            disabled={submitting}
            onClick={() => handleDecision("REJECT")}
            className="rounded-lg border border-rose-500/40 bg-rose-500/20 px-5 py-2 text-xs font-bold text-rose-300 hover:bg-rose-500/30 transition disabled:opacity-50"
          >
            ✕ Reject Schedule
          </button>
          <button
            type="button"
            disabled={submitting}
            onClick={() => handleDecision("APPROVE")}
            className="rounded-lg bg-emerald-600 px-6 py-2 text-xs font-bold text-white shadow-lg hover:bg-emerald-500 transition disabled:opacity-50"
          >
            ✓ Approve & Release Schedule
          </button>
        </div>
      </div>

      {/* Proposed Solution & State Inspection */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <JsonViewer
          title="Proposed Schedule Solution"
          data={
            approvalState?.has_solution
              ? {
                  status: approvalState.status,
                  decision: approvalState.decision,
                  notes: approvalState.notes,
                  has_solution: true,
                }
              : {
                  message: "Schedule solution ready for inspection",
                }
          }
          initialExpanded={true}
        />
        <JsonViewer
          title="Temporal Approval State & Audit History"
          data={approvalState || workflowStatus || { message: "No raw state found" }}
          initialExpanded={true}
        />
      </div>
    </div>
  );
}
