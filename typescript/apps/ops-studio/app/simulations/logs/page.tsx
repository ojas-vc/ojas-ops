"use client";

import { client } from "@/app/lib/api";
import type { DisruptionLogRecord } from "@ojas-ops/sdk";
import { DataTable } from "@ojas-ops/ui";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function DisruptionLogsPage() {
  const [logs, setLogs] = useState<DisruptionLogRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Create Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [scheduleRunId, setScheduleRunId] = useState("run_01");
  const [disruptionType, setDisruptionType] = useState("TASK_DELAY");
  const [magnitudeMinutes, setMagnitudeMinutes] = useState(45);
  const [description, setDescription] = useState("Unscheduled maintenance calibration");
  const [affectedTasksStr, setAffectedTasksStr] = useState("task_roughing, task_turning");
  const [saving, setSaving] = useState(false);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.disruptionLogs.list();
      setLogs(res.items || []);
    } catch (err: unknown) {
      console.warn("Failed to fetch disruption logs:", err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleDelete = async (id: number | string) => {
    if (!confirm(`Delete disruption record #${id}?`)) return;
    try {
      await client.disruptionLogs.delete(id);
      fetchLogs();
    } catch (err) {
      alert(`Delete failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const tasksList = affectedTasksStr
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      await client.disruptionLogs.create({
        schedule_run_id: scheduleRunId,
        disruption_type: disruptionType,
        magnitude_minutes: Number(magnitudeMinutes),
        affected_tasks: tasksList,
        metadata: {
          description,
          reported_by: "plant-supervisor",
          logged_at: new Date().toISOString(),
        },
      });

      setShowCreateModal(false);
      fetchLogs();
    } catch (err) {
      alert(`Create failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    {
      key: "id",
      header: "Log ID",
      render: (l: DisruptionLogRecord) => (
        <span className="font-mono text-xs text-indigo-400 font-semibold">#{l.id}</span>
      ),
    },
    {
      key: "schedule_run_id",
      header: "Schedule Run ID",
      render: (l: DisruptionLogRecord) => (
        <span className="font-mono text-xs text-slate-300">{l.schedule_run_id || "—"}</span>
      ),
    },
    {
      key: "disruption_type",
      header: "Disruption Type",
      render: (l: DisruptionLogRecord) => (
        <span className="inline-block rounded bg-rose-500/10 border border-rose-500/20 px-2.5 py-0.5 text-xs font-semibold text-rose-300">
          {l.disruption_type}
        </span>
      ),
    },
    {
      key: "magnitude_minutes",
      header: "Magnitude",
      render: (l: DisruptionLogRecord) => (
        <span className="font-mono text-xs text-amber-300 font-medium">
          +{l.magnitude_minutes} min
        </span>
      ),
    },
    {
      key: "affected_tasks",
      header: "Affected Tasks",
      render: (l: DisruptionLogRecord) => (
        <div className="flex flex-wrap gap-1 max-w-xs">
          {l.affected_tasks && l.affected_tasks.length > 0 ? (
            l.affected_tasks.map((t) => (
              <span
                key={t}
                className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-300"
              >
                {t}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-500">—</span>
          )}
        </div>
      ),
    },
    {
      key: "created_at",
      header: "Logged At",
      render: (l: DisruptionLogRecord) => (
        <span className="text-xs text-slate-400">
          {l.created_at ? new Date(l.created_at).toLocaleString() : "—"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (l: DisruptionLogRecord) => (
        <button
          type="button"
          onClick={() => handleDelete(l.id)}
          className="rounded bg-rose-500/10 px-2.5 py-1 text-xs font-medium text-rose-400 hover:bg-rose-500/20 transition"
        >
          Delete
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/simulations"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Disruption Simulator
          </Link>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Operational Disruption Audit Logs
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Historical incident log of machine breakdowns, supply shocks, and schedule delays
            (`/disruption-logs/`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchLogs}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition"
          >
            + Log Incident
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Disruption Service Notice</div>
          <div>{error}</div>
        </div>
      )}

      {/* Main Table */}
      <DataTable
        columns={columns}
        data={logs}
        isLoading={loading}
        emptyMessage="No operational disruptions logged yet. Click '+ Log Incident' to record an event."
      />

      {/* Modal: Create Disruption Record */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white">Record Operational Incident</h2>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Schedule Run Reference ID
                </label>
                <input
                  type="text"
                  required
                  value={scheduleRunId}
                  onChange={(e) => setScheduleRunId(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Disruption Type</label>
                  <select
                    value={disruptionType}
                    onChange={(e) => setDisruptionType(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="TASK_DELAY">TASK_DELAY</option>
                    <option value="MACHINE_BREAKDOWN">MACHINE_BREAKDOWN</option>
                    <option value="STAFF_ABSENCE">STAFF_ABSENCE</option>
                    <option value="WEATHER_EVENT">WEATHER_EVENT</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Delay Magnitude (Minutes)
                  </label>
                  <input
                    type="number"
                    required
                    value={magnitudeMinutes}
                    onChange={(e) => setMagnitudeMinutes(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Incident Description
                </label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Spindle bearing overheating on CNC unit"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Affected Task IDs (comma separated)
                </label>
                <input
                  type="text"
                  value={affectedTasksStr}
                  onChange={(e) => setAffectedTasksStr(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none font-mono"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="rounded-lg bg-slate-800 px-4 py-2 font-medium text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
                >
                  {saving ? "Logging..." : "Save Disruption Log"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
