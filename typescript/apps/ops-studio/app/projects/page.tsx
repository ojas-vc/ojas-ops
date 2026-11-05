"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { client } from "../lib/api";
import type { PipelineManifestSummary, ProjectWorkspaceRecord } from "@ojas-ops/sdk";
import { StatusBadge, MetricCard } from "@ojas-ops/ui";

export default function ProjectsIndexPage() {
  const [projects, setProjects] = useState<ProjectWorkspaceRecord[]>([]);
  const [pipelines, setPipelines] = useState<PipelineManifestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [projRes, pipeRes] = await Promise.all([
          client.projects.list("default").catch(() => ({ results: [] })),
          client.pipelines.list().catch(() => []),
        ]);
        setProjects(projRes.results || []);
        setPipelines(pipeRes || []);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load projects");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalProjects = projects.length;
  const inProgress = projects.filter((p) => p.status === "IN_PROGRESS" || p.status === "RUNNING").length;
  const awaitingGate = projects.filter((p) => p.status.includes("AWAITING") || p.status.includes("GATE")).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              Agent State Machine
            </span>
            <span className="text-xs text-slate-500">Dual-Persistence Enabled</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Instruction-Driven Operational Pipelines
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Composable, agent-directed combinatorial optimization with durable Temporal execution and Human-in-the-Loop review gates.
          </p>
        </div>

        <Link
          href="/projects/new"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition"
        >
          <span className="text-lg leading-none">+</span> New Project Workspace
        </Link>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Active Projects" value={totalProjects} subValue="Total registered workspaces" />
        <MetricCard label="In Execution" value={inProgress} subValue="Currently solving / running stages" />
        <MetricCard
          label="Awaiting Human Gate"
          value={awaitingGate}
          subValue="Action required in Tradeoff Console"
        />
        <MetricCard label="Catalog Pipelines" value={pipelines.length || 18} subValue="Domain industrial pipelines" />
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Projects Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Project Workspaces</h2>
          <span className="text-xs text-slate-400">Tenant: default</span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-sm text-slate-400">Loading project workspaces...</div>
        ) : projects.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-sm text-slate-400">No project workspaces created yet.</p>
            <Link
              href="/projects/new"
              className="mt-3 inline-block text-xs font-semibold text-indigo-400 hover:text-indigo-300"
            >
              Launch your first pipeline project &rarr;
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-800 text-xs font-semibold uppercase text-slate-400">
                <tr>
                  <th className="py-3 px-4">Project ID</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Pipeline</th>
                  <th className="py-3 px-4">Current Stage</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {projects.map((p) => (
                  <tr key={p.project_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-mono text-xs text-indigo-300">
                      <Link href={`/projects/${p.project_id}`} className="hover:underline">
                        {p.project_id}
                      </Link>
                    </td>
                    <td className="py-3 px-4 font-medium text-white">{p.title}</td>
                    <td className="py-3 px-4">
                      <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300 font-mono">
                        {p.pipeline_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-xs text-slate-300">{p.current_stage || "Intake"}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={p.status} />
                    </td>
                    <td className="py-3 px-4 text-xs">
                      <Link
                        href={`/projects/${p.project_id}`}
                        className="rounded bg-slate-800 px-2.5 py-1 text-slate-300 hover:bg-indigo-600 hover:text-white transition"
                      >
                        Inspect &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pipelines Catalog */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Installed Industrial Pipelines</h2>
            <p className="text-xs text-slate-400">
              18 production-ready declarative state machine pipelines ready for execution
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {pipelines.map((pipe) => (
            <div
              key={pipe.name}
              className="flex flex-col justify-between rounded-lg border border-slate-800 bg-slate-950/40 p-4 hover:border-indigo-500/50 transition"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 uppercase tracking-wider">
                    {pipe.category}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">v{pipe.version}</span>
                </div>
                <h3 className="mt-2 text-sm font-bold text-white font-mono">{pipe.name}</h3>
                <p className="mt-1 text-xs text-slate-400 line-clamp-2">{pipe.description}</p>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs">
                <span className="text-slate-500">{pipe.stages_count} stages</span>
                <Link
                  href={`/projects/new?pipeline=${encodeURIComponent(pipe.name)}`}
                  className="font-medium text-indigo-400 hover:text-indigo-300"
                >
                  Create &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
