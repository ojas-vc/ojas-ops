"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_SCENARIO_PAYLOAD } from "@/app/lib/fixtures";
import type { ScenarioRecordDTO } from "@ojas-ops/sdk";
import { DataTable } from "@ojas-ops/ui";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioRecordDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Create Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [tenantId, setTenantId] = useState("org_default");
  const [name, setName] = useState("Automated_Gearbox_Production");
  const [domain, setDomain] = useState("manufacturing");
  const [scale, setScale] = useState("small");
  const [definitionJson, setDefinitionJson] = useState(
    JSON.stringify(SAMPLE_SCENARIO_PAYLOAD, null, 2),
  );
  const [saving, setSaving] = useState(false);

  const fetchScenarios = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.scenarios.list();
      setScenarios(res.items || []);
    } catch (err: unknown) {
      console.warn("Failed to fetch scenarios:", err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchScenarios();
  }, [fetchScenarios]);

  const handleDelete = async (id: number | string) => {
    if (!confirm(`Are you sure you want to delete Scenario #${id}?`)) return;
    try {
      await client.scenarios.delete(id);
      fetchScenarios();
    } catch (err) {
      alert(`Delete failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      let parsedDef = {};
      try {
        parsedDef = JSON.parse(definitionJson);
      } catch {
        alert("Invalid JSON in scenario definition");
        setSaving(false);
        return;
      }

      await client.scenarios.create({
        tenant_id: tenantId,
        name,
        domain,
        scale,
        definition_json: parsedDef,
      });

      setShowCreateModal(false);
      fetchScenarios();
    } catch (err) {
      alert(`Create failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    {
      key: "id",
      header: "Scenario ID",
      render: (s: ScenarioRecordDTO) => (
        <span className="font-mono text-xs text-indigo-400 font-semibold">#{s.id}</span>
      ),
    },
    {
      key: "name",
      header: "Scenario Name",
      render: (s: ScenarioRecordDTO) => (
        <div className="font-medium text-slate-200">
          {s.name}
          {s.tenant_id && (
            <span className="ml-2 text-xs text-slate-500 font-mono">({s.tenant_id})</span>
          )}
        </div>
      ),
    },
    {
      key: "domain",
      header: "Domain",
      render: (s: ScenarioRecordDTO) => (
        <span className="inline-block rounded-full bg-slate-800 border border-slate-700 px-2.5 py-0.5 text-xs text-slate-300 capitalize">
          {s.domain || "general"}
        </span>
      ),
    },
    {
      key: "scale",
      header: "Scale",
      render: (s: ScenarioRecordDTO) => (
        <span className="text-xs font-mono text-slate-400 uppercase">{s.scale || "medium"}</span>
      ),
    },
    {
      key: "created_at",
      header: "Created At",
      render: (s: ScenarioRecordDTO) => (
        <span className="text-xs text-slate-400">
          {s.created_at ? new Date(s.created_at).toLocaleString() : "—"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (s: ScenarioRecordDTO) => (
        <div className="flex items-center gap-2">
          <Link
            href="/scenarios/runner"
            className="rounded bg-indigo-600/20 border border-indigo-500/30 px-2.5 py-1 text-xs font-semibold text-indigo-300 hover:bg-indigo-600/30 transition"
          >
            Run & Verify
          </Link>
          <button
            type="button"
            onClick={() => handleDelete(s.id)}
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
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Scenarios & Benchmark Library
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Declarative test scenarios, golden assertions, and synthetic benchmark instances.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/scenarios/generator"
            className="rounded-lg border border-purple-500/40 bg-purple-500/10 px-3.5 py-1.5 text-xs font-semibold text-purple-300 hover:bg-purple-500/20 transition"
          >
            ⚡ Synthetic Generator
          </Link>
          <Link
            href="/scenarios/runner"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            ▶ Declarative Runner
          </Link>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white shadow hover:bg-indigo-500 transition"
          >
            + New Scenario
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Scenario Service Notice</div>
          <div>{error}</div>
        </div>
      )}

      {/* Main Table */}
      <DataTable
        columns={columns}
        data={scenarios}
        isLoading={loading}
        emptyMessage="No scenarios recorded in library. Click '+ New Scenario' or use the Synthetic Generator."
      />

      {/* Modal: Create Scenario */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white">Add New Scenario Definition</h2>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div className="grid grid-cols-4 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Tenant ID</label>
                  <input
                    type="text"
                    required
                    value={tenantId}
                    onChange={(e) => setTenantId(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Scenario Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Domain</label>
                  <select
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="manufacturing">manufacturing</option>
                    <option value="film">film</option>
                    <option value="workforce">workforce</option>
                    <option value="academic">academic</option>
                    <option value="logistics">logistics</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Scale</label>
                  <select
                    value={scale}
                    onChange={(e) => setScale(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="small">small</option>
                    <option value="medium">medium</option>
                    <option value="large">large</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Definition JSON (Resources, Tasks, Golden Assertions)
                </label>
                <textarea
                  rows={10}
                  value={definitionJson}
                  onChange={(e) => setDefinitionJson(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 font-mono text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
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
                  {saving ? "Saving..." : "Save to Catalog"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
