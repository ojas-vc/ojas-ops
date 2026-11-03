"use client";

import { client } from "@/app/lib/api";
import type { ScheduleRunRecord } from "@ojas-ops/sdk";
import { DataTable, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function ScheduleRunsPage() {
  const [runs, setRuns] = useState<ScheduleRunRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [tenantId, setTenantId] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Create Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createTenantId, setCreateTenantId] = useState("org_default");
  const [createScenarioName, setCreateScenarioName] = useState("Production Benchmark");
  const [createStatus, setCreateStatus] = useState("OPTIMAL");
  const [createMakespan, setCreateMakespan] = useState(180);
  const [createObjective, setCreateObjective] = useState(15000);
  const [creating, setCreating] = useState(false);

  const fetchRuns = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.scheduleRuns.list({
        tenant_id: tenantId === "all" ? undefined : tenantId,
        status: statusFilter === "all" ? undefined : statusFilter,
        search: search.trim() ? search.trim() : undefined,
        page,
        page_size: pageSize,
      });
      setRuns(res.items || []);
      setTotal(res.total || 0);
    } catch (err: unknown) {
      console.warn("Failed to fetch schedule runs:", err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [tenantId, statusFilter, search, page]);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  const handleDelete = async (id: number | string) => {
    if (!confirm(`Are you sure you want to delete Schedule Run #${id}?`)) return;
    try {
      await client.scheduleRuns.delete(id);
      fetchRuns();
    } catch (err) {
      alert(`Delete failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await client.scheduleRuns.create({
        tenant_id: createTenantId,
        scenario_name: createScenarioName,
        status: createStatus,
        makespan: Number(createMakespan),
        objective_value: Number(createObjective),
        result_json: {
          tasks_count: 4,
          schedule: { makespan: createMakespan },
        },
        metadata: {
          source: "ops-studio-ui",
          created_by: "operations-engineer",
        },
      });
      setShowCreateModal(false);
      fetchRuns();
    } catch (err) {
      alert(`Create failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      key: "id",
      header: "Run ID",
      render: (r: ScheduleRunRecord) => (
        <Link
          href={`/schedule-runs/${r.id}`}
          className="font-mono text-indigo-400 hover:text-indigo-300 font-semibold"
        >
          #{r.id}
        </Link>
      ),
    },
    {
      key: "scenario_name",
      header: "Scenario Name",
      render: (r: ScheduleRunRecord) => (
        <div className="font-medium text-slate-200">
          {r.scenario_name || "Unnamed Scenario"}
          {r.tenant_id && (
            <span className="ml-2 text-xs text-slate-500 font-mono">({r.tenant_id})</span>
          )}
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (r: ScheduleRunRecord) => <StatusBadge status={r.status || "UNKNOWN"} />,
    },
    {
      key: "makespan",
      header: "Makespan",
      render: (r: ScheduleRunRecord) => (
        <span className="font-mono text-slate-300">
          {r.makespan != null ? `${r.makespan} min` : "—"}
        </span>
      ),
    },
    {
      key: "objective_value",
      header: "Objective Score",
      render: (r: ScheduleRunRecord) => (
        <span className="font-mono text-slate-300">
          {r.objective_value != null ? r.objective_value.toLocaleString() : "—"}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Created At",
      render: (r: ScheduleRunRecord) => (
        <span className="text-xs text-slate-400">
          {r.created_at ? new Date(r.created_at).toLocaleString() : "—"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (r: ScheduleRunRecord) => (
        <div className="flex items-center gap-2">
          <Link
            href={`/schedule-runs/${r.id}`}
            className="rounded bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            Inspect
          </Link>
          <button
            type="button"
            onClick={() => handleDelete(r.id)}
            className="rounded bg-rose-500/10 px-2.5 py-1 text-xs font-medium text-rose-400 hover:bg-rose-500/20 transition"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Schedule Runs Catalog</h1>
          <p className="mt-1 text-sm text-slate-400">
            Historical database records of CP-SAT optimization executions and solver runs.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchRuns}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition"
          >
            + New Schedule Run
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Backend Connection Alert</div>
          <div>{error}</div>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Tenant Filter
          </label>
          <select
            value={tenantId}
            onChange={(e) => {
              setTenantId(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All Tenants</option>
            <option value="org_default">org_default</option>
            <option value="tenant_test">tenant_test</option>
            <option value="chitram_studio">chitram_studio</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="OPTIMAL">OPTIMAL</option>
            <option value="FEASIBLE">FEASIBLE</option>
            <option value="INFEASIBLE">INFEASIBLE</option>
            <option value="TIMEOUT">TIMEOUT</option>
          </select>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Search Scenario Name
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="e.g. Benchmark, Gearbox..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchRuns()}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
            />
            <button
              type="button"
              onClick={fetchRuns}
              className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <DataTable
        columns={columns}
        data={runs}
        isLoading={loading}
        emptyMessage="No schedule runs found matching query. Click '+ New Schedule Run' to insert a record."
      />

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}{" "}
            runs
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded bg-slate-800 px-3 py-1.5 disabled:opacity-40 hover:bg-slate-700 text-slate-200"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={page * pageSize >= total}
              onClick={() => setPage((p) => p + 1)}
              className="rounded bg-slate-800 px-3 py-1.5 disabled:opacity-40 hover:bg-slate-700 text-slate-200"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Modal: Create Run */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white">Create Schedule Run</h2>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleCreate} className="mt-4 space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Tenant ID</label>
                <input
                  type="text"
                  required
                  value={createTenantId}
                  onChange={(e) => setCreateTenantId(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Scenario Name</label>
                <input
                  type="text"
                  required
                  value={createScenarioName}
                  onChange={(e) => setCreateScenarioName(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-medium text-slate-300 mb-1">Status</label>
                  <select
                    value={createStatus}
                    onChange={(e) => setCreateStatus(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="OPTIMAL">OPTIMAL</option>
                    <option value="FEASIBLE">FEASIBLE</option>
                    <option value="INFEASIBLE">INFEASIBLE</option>
                  </select>
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Makespan (min)</label>
                  <input
                    type="number"
                    value={createMakespan}
                    onChange={(e) => setCreateMakespan(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block font-medium text-slate-300 mb-1">Objective Score</label>
                  <input
                    type="number"
                    value={createObjective}
                    onChange={(e) => setCreateObjective(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="rounded-lg bg-slate-800 px-4 py-2 font-medium text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
                >
                  {creating ? "Saving..." : "Save Record"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
