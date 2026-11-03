"use client";

import { client } from "@/app/lib/api";
import { SAMPLE_CULTURAL_PAYLOAD, SAMPLE_STANDARD_BLACKOUTS_PAYLOAD } from "@/app/lib/fixtures";
import type { CulturalIntervalsResponse, StandardBlackoutsResponse } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard } from "@ojas-ops/ui";
import { useState } from "react";

export default function CalendarsPage() {
  const [activeTab, setActiveTab] = useState<"cultural" | "standard">("cultural");

  // Cultural state
  const [culturalPayload, setCulturalPayload] = useState(SAMPLE_CULTURAL_PAYLOAD);
  const [loadingCultural, setLoadingCultural] = useState(false);
  const [culturalResult, setCulturalResult] = useState<CulturalIntervalsResponse | null>(null);

  // Standard state
  const [standardPayload, setStandardPayload] = useState(SAMPLE_STANDARD_BLACKOUTS_PAYLOAD);
  const [loadingStandard, setLoadingStandard] = useState(false);
  const [standardResult, setStandardResult] = useState<StandardBlackoutsResponse | null>(null);

  const [error, setError] = useState<string | null>(null);

  const handleComputeCultural = async () => {
    setLoadingCultural(true);
    setError(null);
    try {
      const res = await client.calendars.culturalIntervals(culturalPayload);
      setCulturalResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingCultural(false);
    }
  };

  const handleComputeStandard = async () => {
    setLoadingStandard(true);
    setError(null);
    try {
      const res = await client.calendars.standardBlackouts(standardPayload);
      setStandardResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingStandard(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Operational & Cultural Calendars Engine
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Calculate Vedic inauspicious astrological blackouts (Rahu Kalam, Yamagandam) and
            standard industrial shift operating hours.
          </p>
        </div>

        <button
          type="button"
          onClick={activeTab === "cultural" ? handleComputeCultural : handleComputeStandard}
          disabled={loadingCultural || loadingStandard}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
        >
          {loadingCultural || loadingStandard ? "Calculating..." : "🗓 Compute Blackout Windows"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Calendar Calculation Error</div>
          <div>{error}</div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-3 border-b border-slate-800 pb-3">
        <button
          type="button"
          onClick={() => setActiveTab("cultural")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "cultural"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          🕉 Vedic & Cultural Astrological Panchang (`/calendars/cultural/intervals`)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("standard")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "standard"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          ⏰ Standard Industrial Shift & Weekend Hours (`/calendars/standard/blackouts`)
        </button>
      </div>

      {/* Tab 1: Cultural Panchang */}
      {activeTab === "cultural" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
            <h3 className="font-semibold text-white">Astrological Horizon & Blackout Flags</h3>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div>
                <label className="block text-slate-400 mb-1">Horizon (Days)</label>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={culturalPayload.horizon_days}
                  onChange={(e) =>
                    setCulturalPayload({
                      ...culturalPayload,
                      horizon_days: Number(e.target.value),
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
              </div>

              <div className="flex items-center gap-2 pt-5">
                <label className="flex items-center gap-2 cursor-pointer text-slate-200">
                  <input
                    type="checkbox"
                    checked={culturalPayload.enable_rahu_kalam}
                    onChange={(e) =>
                      setCulturalPayload({
                        ...culturalPayload,
                        enable_rahu_kalam: e.target.checked,
                      })
                    }
                    className="rounded text-indigo-600"
                  />
                  <span>Rahu Kalam Blackout</span>
                </label>
              </div>

              <div className="flex items-center gap-2 pt-5">
                <label className="flex items-center gap-2 cursor-pointer text-slate-200">
                  <input
                    type="checkbox"
                    checked={culturalPayload.enable_yamagandam}
                    onChange={(e) =>
                      setCulturalPayload({
                        ...culturalPayload,
                        enable_yamagandam: e.target.checked,
                      })
                    }
                    className="rounded text-indigo-600"
                  />
                  <span>Yamagandam Blackout</span>
                </label>
              </div>
            </div>
          </div>

          {culturalResult && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <MetricCard
                  label="Blackout Intervals"
                  value={culturalResult.blackout_windows?.length || 0}
                  subValue="Calculated prohibited windows"
                />
                <MetricCard
                  label="Horizon Span"
                  value={`${culturalPayload.horizon_days || 7} Days`}
                  subValue="Total evaluation scope"
                />
                <MetricCard
                  label="Muhurat Engine"
                  value="Vedic Panchang"
                  subValue="Solar day proportional system"
                />
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
                <h3 className="text-sm font-semibold text-white">Computed Blackout Windows</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {culturalResult.blackout_windows?.map((w, idx) => (
                    <div
                      key={`window-${w.start || idx}`}
                      className="rounded-xl border border-rose-500/20 bg-rose-950/20 p-3.5 text-xs text-rose-200 space-y-1"
                    >
                      <div className="flex items-center justify-between font-semibold">
                        <span>{w.label || "Inauspicious Window"}</span>
                        <span className="font-mono text-[11px] text-rose-400">
                          Day {Math.floor((w.start || 0) / 1440) + 1}
                        </span>
                      </div>
                      <div className="font-mono text-[11px] text-slate-300">
                        {w.start}m → {w.end}m ({w.end - w.start} min)
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <JsonViewer
                title="Cultural Intervals Raw Response"
                data={culturalResult}
                initialExpanded={false}
              />
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Standard Shift Hours */}
      {activeTab === "standard" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4 text-xs">
            <h3 className="font-semibold text-white">Standard Shift Parameters</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-slate-400 mb-1">Horizon (Days)</label>
                <input
                  type="number"
                  value={standardPayload.horizon_days}
                  onChange={(e) =>
                    setStandardPayload({
                      ...standardPayload,
                      horizon_days: Number(e.target.value),
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Shift Start (Minute of Day)</label>
                <input
                  type="number"
                  value={standardPayload.working_day_start_minute}
                  onChange={(e) =>
                    setStandardPayload({
                      ...standardPayload,
                      working_day_start_minute: Number(e.target.value),
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
                <span className="text-[10px] text-slate-500">480 = 08:00 AM (8h * 60)</span>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Shift End (Minute of Day)</label>
                <input
                  type="number"
                  value={standardPayload.working_day_end_minute}
                  onChange={(e) =>
                    setStandardPayload({
                      ...standardPayload,
                      working_day_end_minute: Number(e.target.value),
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
                <span className="text-[10px] text-slate-500">1020 = 05:00 PM (17h * 60)</span>
              </div>
            </div>
          </div>

          {standardResult && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <MetricCard
                  label="Off-Shift Blackout Blocks"
                  value={standardResult.blackout_windows?.length || 0}
                  subValue="Night & weekend blocks"
                />
                <MetricCard
                  label="Daily Working Hours"
                  value={`${((standardPayload.working_day_end_minute || 1020) - (standardPayload.working_day_start_minute || 480)) / 60} Hours`}
                  subValue="Productive shift duration"
                />
                <MetricCard
                  label="Weekend Off"
                  value="Sat & Sun"
                  subValue="Non-working calendar days"
                />
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 space-y-4">
                <h3 className="text-sm font-semibold text-white">Generated Blackout Blocks</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {standardResult.blackout_windows?.map((w, idx) => (
                    <div
                      key={`std-window-${w.start || idx}`}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-3.5 text-xs text-slate-300 space-y-1"
                    >
                      <div className="flex items-center justify-between font-semibold">
                        <span className="text-amber-400">{w.label || "Non-Working Period"}</span>
                        <span className="font-mono text-[11px] text-slate-500">
                          Day {Math.floor((w.start || 0) / 1440) + 1}
                        </span>
                      </div>
                      <div className="font-mono text-[11px] text-slate-400">
                        {w.start}m → {w.end}m ({w.end - w.start} min)
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <JsonViewer
                title="Standard Blackouts Raw Response"
                data={standardResult}
                initialExpanded={false}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
