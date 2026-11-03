"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_FILM_PAYLOAD } from "@/app/lib/fixtures";
import type { FilmScheduleResult, ProductionDataset } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function FilmProductionAdapterPage() {
  const [dataset, setDataset] = useState<ProductionDataset>(SAMPLE_FILM_PAYLOAD);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<FilmScheduleResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.filmProduction(dataset);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
            <Link href="/" className="hover:underline">
              Dashboard
            </Link>
            <span>/</span>
            <span>Domain Adapters</span>
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            🎬 Film Production Shooting Schedule Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            SAG-AFTRA 10-day drop rules, cast Day-Out-of-Days minimization, and location move
            turnaround optimization (`/adapters/film-production/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setDataset(SAMPLE_FILM_PAYLOAD)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
          >
            Reset Fixture
          </button>
          <button
            type="button"
            disabled={optimizing}
            onClick={handleOptimize}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            {optimizing ? "Solving Call Sheet..." : "⚡ Optimize Shoot"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Film Adapter Optimization Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Shoot Status"
            value={<StatusBadge status={result.status || "FEASIBLE"} />}
            subValue="CP-SAT feasibility"
          />
          <MetricCard
            label="Total Shoot Days"
            value={result.total_shooting_days ?? 2}
            subValue={`Cap: ${dataset.max_days || 5} days`}
          />
          <MetricCard
            label="Cast Members"
            value={dataset.cast?.length || 0}
            subValue="Actors scheduled"
          />
          <MetricCard
            label="Scenes Sequence"
            value={dataset.scenes?.length || 0}
            subValue="Call sheet strips"
          />
        </div>
      )}

      {/* Configuration & Inputs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
          <h3 className="font-semibold text-white">Production Configuration</h3>
          <div>
            <label className="block text-slate-400 mb-1">Production Title</label>
            <input
              type="text"
              value={dataset.production_title}
              onChange={(e) => setDataset({ ...dataset, production_title: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 mb-1">Max Shooting Days</label>
              <input
                type="number"
                value={dataset.max_days || 5}
                onChange={(e) => setDataset({ ...dataset, max_days: Number(e.target.value) })}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Locations</label>
              <div className="text-slate-300 py-2">
                {dataset.locations.map((l) => l.name).join(", ")}
              </div>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Cast Members ({dataset.cast?.length})
            </h4>
            <div className="space-y-1.5">
              {dataset.cast?.map((t) => (
                <div
                  key={t.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="text-slate-200 font-medium">{t.name}</span>
                  <span className="font-mono text-slate-400">
                    ${((t.day_rate_cents || 0) / 100).toLocaleString()}/day
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Scenes Schedule ({dataset.scenes?.length})
            </h4>
            <div className="space-y-1.5">
              {dataset.scenes?.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-mono text-indigo-400">{s.id}</span>
                  <span className="text-slate-300">
                    {s.name} ({s.duration_minutes} min)
                  </span>
                  <span className="text-[10px] text-slate-500">Cast: {s.cast_ids?.join(", ")}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results / JSON View */}
        <div className="space-y-4">
          <JsonViewer
            title="Optimized Film Production Solution"
            data={result || { message: "Click 'Optimize Shoot' to compute shooting schedule" }}
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
