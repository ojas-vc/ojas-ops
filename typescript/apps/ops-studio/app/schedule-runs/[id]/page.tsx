"use client";

import { client } from "@/app/lib/api";
import type { ScheduleRunRecord } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ScheduleRunDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [run, setRun] = useState<ScheduleRunRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit metadata form
  const [editing, setEditing] = useState(false);
  const [scenarioName, setScenarioName] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    client.scheduleRuns
      .get(id)
      .then((data) => {
        setRun(data);
        setScenarioName(data.scenario_name || "");
        setNotes((data.metadata?.notes as string) || "");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await client.scheduleRuns.update(id, {
        scenario_name: scenarioName,
        metadata: {
          ...(run?.metadata || {}),
          notes,
          updated_at: new Date().toISOString(),
        },
      });
      setRun(updated);
      setEditing(false);
    } catch (err) {
      alert(`Update failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to permanently delete Run #${id}?`)) return;
    try {
      await client.scheduleRuns.delete(id);
      router.push("/schedule-runs");
    } catch (err) {
      alert(`Delete failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400">
        <span className="animate-pulse">Loading schedule run #{id}...</span>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="space-y-4">
        <Link
          href="/schedule-runs"
          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
        >
          ← Back to Schedule Runs
        </Link>
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-6 text-sm text-rose-300">
          <h2 className="font-bold">Error loading record #{id}</h2>
          <p className="mt-1">{error || "Schedule run not found"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/schedule-runs"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Catalog
          </Link>
          <div className="mt-2 flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Schedule Run #{run.id}</h1>
            <StatusBadge status={run.status || "UNKNOWN"} />
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Tenant: <span className="font-mono text-slate-300">{run.tenant_id || "default"}</span> •
            Created: {run.created_at ? new Date(run.created_at).toLocaleString() : "—"}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setEditing(!editing)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            {editing ? "Cancel Editing" : "Edit Metadata"}
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="rounded-lg bg-rose-500/10 border border-rose-500/30 px-3 py-1.5 text-xs font-medium text-rose-400 hover:bg-rose-500/20 transition"
          >
            Delete Run
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <MetricCard
          label="Makespan"
          value={run.makespan != null ? `${run.makespan} min` : "—"}
          subValue="Total schedule duration"
        />
        <MetricCard
          label="Objective Value"
          value={run.objective_value != null ? run.objective_value.toLocaleString() : "—"}
          subValue="Cost / Penalty scalar"
        />
        <MetricCard
          label="Status"
          value={run.status || "UNKNOWN"}
          subValue="CP-SAT solver verdict"
        />
        <MetricCard
          label="Tenant ID"
          value={run.tenant_id || "default"}
          subValue="Partition namespace"
        />
      </div>

      {/* Edit Metadata Drawer */}
      {editing && (
        <form
          onSubmit={handleUpdate}
          className="rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-5 space-y-4"
        >
          <h3 className="text-sm font-semibold text-white">Edit Schedule Metadata</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Scenario Name</label>
              <input
                type="text"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Operational Notes</label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add reviewer notes or tag..."
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="rounded-lg bg-slate-800 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      )}

      {/* Result Inspector & Metadata Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <JsonViewer
          title="Optimization Result Payload (result_json)"
          data={run.result_json || { message: "No result_json recorded" }}
          initialExpanded={true}
        />
        <JsonViewer
          title="Execution Metadata & Diagnostics"
          data={run.metadata || { message: "No metadata recorded" }}
          initialExpanded={true}
        />
      </div>
    </div>
  );
}
