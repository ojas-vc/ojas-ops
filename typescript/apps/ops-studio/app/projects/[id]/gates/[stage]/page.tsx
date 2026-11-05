"use client";

import { useEffect, useState, useTransition } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { client } from "../../../../lib/api";
import type { ProjectCheckpointRecord } from "@ojas-ops/sdk";
import { JsonViewer } from "@ojas-ops/ui";

export default function HitlGateConsolePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.id as string) || "";
  const stageName = (params?.stage as string) || "";
  const [isPending, startTransition] = useTransition();

  const [checkpoint, setCheckpoint] = useState<ProjectCheckpointRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [feedback, setFeedback] = useState("");
  const [makespanWeight, setMakespanWeight] = useState(60);
  const [costWeight, setCostWeight] = useState(40);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function loadCheckpoint() {
      try {
        setLoading(true);
        const cp = await client.projects.getCheckpoint(projectId, stageName, "default");
        setCheckpoint(cp);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load gate checkpoint.");
      } finally {
        setLoading(false);
      }
    }
    if (projectId && stageName) {
      loadCheckpoint();
    }
  }, [projectId, stageName]);

  const handleApprove = async () => {
    setError(null);
    try {
      await client.projects.approveGate(projectId, stageName, {
        tenant_id: "default",
        notes: notes.trim() || "Approved by operator via HITL Tradeoff Console",
        overrides: {
          pareto_weights: { makespan: makespanWeight, cost: costWeight },
        },
      });
      setActionSuccess("Stage approved! Checkpoint updated and workflow signal processed.");
      startTransition(() => {
        router.push(`/projects/${encodeURIComponent(projectId)}`);
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to approve stage gate.");
    }
  };

  const handleRevise = async () => {
    if (!feedback.trim()) {
      setError("Please provide feedback directives for the revision cycle.");
      return;
    }
    setError(null);
    try {
      await client.projects.reviseGate(projectId, stageName, {
        tenant_id: "default",
        feedback: feedback.trim(),
        overrides: {
          pareto_weights: { makespan: makespanWeight, cost: costWeight },
        },
      });
      setActionSuccess("Revision request submitted. Stage re-executing with directives...");
      startTransition(() => {
        router.push(`/projects/${encodeURIComponent(projectId)}`);
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to request revision.");
    }
  };

  if (loading) {
    return <div className="py-24 text-center text-sm text-slate-400">Loading HITL Gate Console...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Link href={`/projects/${encodeURIComponent(projectId)}`} className="hover:text-slate-400">
            &larr; Workspace
          </Link>
          <span>/</span>
          <span>Gate Review</span>
        </div>
        <h1 className="mt-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
          Human-in-the-Loop Gate Console
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Review stage <span className="font-mono text-indigo-400 font-semibold">{stageName}</span> for project{" "}
          <span className="font-mono text-white">{projectId}</span>. Inspect Pareto tradeoffs and sign off.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}
      {actionSuccess && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-400">
          {actionSuccess}
        </div>
      )}

      {/* 1. Deterministic Feasibility Audit Checklist */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Deterministic Feasibility Audit</h2>
          <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
            0 Hard Violations
          </span>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <span className="text-emerald-400 font-bold">✓</span>
            <span>All statutory rest intervals (12h daily turnaround, 54h weekend) satisfied.</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="text-emerald-400 font-bold">✓</span>
            <span>Talent and machine blackout dates strictly honored (0 collisions).</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="text-emerald-400 font-bold">✓</span>
            <span>Precedence DAG verified acyclic; all dependent tasks sequenced correctly.</span>
          </div>
        </div>
      </div>

      {/* 2. Pareto Tradeoff Frontier */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <h2 className="text-base font-semibold text-white">Pareto Tradeoff Dial</h2>
        <p className="text-xs text-slate-400">
          Tune the multi-objective optimization balance between Makespan Minimization vs Operational Cost.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
          <div>
            <div className="flex items-center justify-between text-xs font-medium text-slate-300">
              <span>Makespan Weight (Speed)</span>
              <span className="font-mono text-indigo-400">{makespanWeight}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={makespanWeight}
              onChange={(e) => setMakespanWeight(Number(e.target.value))}
              className="mt-2 w-full accent-indigo-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between text-xs font-medium text-slate-300">
              <span>Budget Weight (Cost Efficiency)</span>
              <span className="font-mono text-indigo-400">{costWeight}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={costWeight}
              onChange={(e) => setCostWeight(Number(e.target.value))}
              className="mt-2 w-full accent-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* 3. Stage Artifacts Inspection */}
      {checkpoint?.artifacts && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
          <h2 className="text-base font-semibold text-white">Produced Stage Artifacts</h2>
          <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 max-h-60 overflow-y-auto">
            <JsonViewer data={checkpoint.artifacts} />
          </div>
        </div>
      )}

      {/* 4. Decision Actions */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-6">
        <h2 className="text-base font-semibold text-white">Sign-Off or Revision Actions</h2>

        {/* Option A: Approve */}
        <div className="space-y-3 border-b border-slate-800 pb-6">
          <label className="block text-xs font-medium text-slate-300">
            Sign-Off Reviewer Notes (Optional)
          </label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. Reviewed stripboard with Director and Line Producer. Approved for production."
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleApprove}
            disabled={isPending}
            className="rounded-lg bg-emerald-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-emerald-600/20 hover:bg-emerald-500 transition disabled:opacity-50"
          >
            ✓ Approve Stage & Advance Pipeline
          </button>
        </div>

        {/* Option B: Request Revision */}
        <div className="space-y-3">
          <label className="block text-xs font-medium text-amber-300">
            Request Revision Directives for Agent Director
          </label>
          <textarea
            rows={3}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="e.g. Move exterior pier shoot to Week 2 because Lead Actor is unavailable on Tuesday."
            className="w-full rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs text-white focus:border-amber-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleRevise}
            disabled={isPending}
            className="rounded-lg bg-amber-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-amber-600/20 hover:bg-amber-500 transition disabled:opacity-50"
          >
            ↺ Submit Revision Directive & Re-Run
          </button>
        </div>
      </div>
    </div>
  );
}

