"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_MARKETING_PAYLOAD } from "@/app/lib/fixtures";
import type { MarketingOptimizeRequest, MarketingOptimizeResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard, StatusBadge } from "@ojas-ops/ui";
import Link from "next/link";
import { useState } from "react";

export default function MarketingFlightingAdapterPage() {
  const [payload, setPayload] = useState<MarketingOptimizeRequest>(SAMPLE_MARKETING_PAYLOAD);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<MarketingOptimizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.marketingFlighting(payload);
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
            📈 Marketing Budget Flighting & Cadence Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Multi-channel media spend pulsing, continuous vs burst flighting, and diminishing return
            curve optimization (`/adapters/marketing-flighting/optimize`).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setPayload(SAMPLE_MARKETING_PAYLOAD)}
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
            {optimizing ? "Solving Media Flights..." : "⚡ Optimize Budget Flights"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Marketing Adapter Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* KPI Cards */}
      {result && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <MetricCard
            label="Flighting Status"
            value={<StatusBadge status={result.status || "OPTIMAL"} />}
            subValue="CP-SAT exit code"
          />
          <MetricCard
            label="Total Allocated Spend"
            value={
              result.total_spend_cents != null
                ? `$${(result.total_spend_cents / 100).toLocaleString()}`
                : "Optimized"
            }
            subValue="Allocated media budget"
          />
          <MetricCard
            label="Channels Utilized"
            value={payload.channels.length}
            subValue="Meta, Search, OTT"
          />
          <MetricCard
            label="Flights Scheduled"
            value={payload.flights.length}
            subValue="Burst media waves"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
          <h3 className="font-semibold text-white">Media Channels & Flights</h3>

          <div>
            <h4 className="font-medium text-slate-300 mb-2">
              Channels ({payload.channels.length})
            </h4>
            <div className="space-y-1.5">
              {payload.channels.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="font-medium text-slate-200">{c.name}</span>
                  <span className="font-mono text-slate-400">
                    Cap: ${((c.daily_budget_cents_cap || 0) / 100).toLocaleString()}/day
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3">
            <h4 className="font-medium text-slate-300 mb-2">
              Media Flights ({payload.flights.length})
            </h4>
            <div className="space-y-1.5">
              {payload.flights.map((f) => (
                <div
                  key={f.id}
                  className="flex items-center justify-between rounded bg-slate-950 px-3 py-1.5 border border-slate-800"
                >
                  <span className="text-slate-300 font-medium">
                    {f.channel_id} ({f.duration_days} days)
                  </span>
                  <span className="text-[10px] text-indigo-400 font-mono">
                    ${((f.daily_budget_cents || 0) / 100).toLocaleString()}/day
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Results JSON */}
        <div className="space-y-4">
          <JsonViewer
            title="Marketing Flighting Schedule"
            data={
              result || { message: "Click 'Optimize Budget Flights' to view media distribution" }
            }
            initialExpanded={true}
          />
        </div>
      </div>
    </div>
  );
}
