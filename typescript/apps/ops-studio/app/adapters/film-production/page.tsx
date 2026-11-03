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
  const [rescheduling, setRescheduling] = useState(false);
  const [result, setResult] = useState<FilmScheduleResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "stripboard" | "dood" | "callsheet" | "reschedule" | "json"
  >("stripboard");
  const [selectedCallSheetDay, setSelectedCallSheetDay] = useState<number>(1);

  // Reschedule simulation state
  const [completedDays, setCompletedDays] = useState<number[]>([1]);
  const [disruptedDay, setDisruptedDay] = useState<number>(2);
  const [disruptionWeather, setDisruptionWeather] = useState<string>("RAIN");
  const [activateCoverSets, setActivateCoverSets] = useState<boolean>(true);

  // Solver feature flags
  const [enableSoundstageLeases, setEnableSoundstageLeases] = useState(true);
  const [enableHazardDeferral, setEnableHazardDeferral] = useState(true);
  const [enableDropPickup, setEnableDropPickup] = useState(true);

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const res = await client.adapters.filmProduction.optimize({
        dataset,
        enable_soundstage_lease_tracking: enableSoundstageLeases,
        enable_hazard_deferral: enableHazardDeferral,
        enable_drop_pickup: enableDropPickup,
        max_time_in_seconds: 15.0,
      });
      setResult(res);
      if (res.call_sheets && Object.keys(res.call_sheets).length > 0) {
        const firstDay = Number(Object.keys(res.call_sheets)[0]);
        setSelectedCallSheetDay(firstDay);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setOptimizing(false);
    }
  };

  const handleReschedule = async () => {
    setRescheduling(true);
    setError(null);
    try {
      const weatherMap: Record<number, string> = {};
      if (disruptedDay > 0) {
        weatherMap[disruptedDay] = disruptionWeather;
      }

      const res = await client.adapters.filmProduction.reschedule({
        dataset,
        completed_days: completedDays,
        weather_disruptions: weatherMap,
        activate_cover_sets: activateCoverSets,
        max_time_in_seconds: 15.0,
      });
      setResult(res);
      setActiveTab("stripboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRescheduling(false);
    }
  };

  // Color tokens for stripboard strips
  const getStripColorClass = (color: string) => {
    switch (color) {
      case "WHITE":
        return "bg-slate-100 text-slate-900 border-l-4 border-l-slate-400";
      case "YELLOW":
        return "bg-amber-300 text-amber-950 border-l-4 border-l-amber-600";
      case "GREEN":
        return "bg-emerald-800 text-emerald-50 border-l-4 border-l-emerald-400";
      case "BLUE":
        return "bg-sky-800 text-sky-50 border-l-4 border-l-sky-400";
      default:
        return "bg-slate-800 text-slate-200 border-l-4 border-l-indigo-500";
    }
  };

  const getDoodBadgeClass = (code: string) => {
    switch (code) {
      case "SW":
        return "bg-indigo-500/20 text-indigo-300 border-indigo-500/40";
      case "W":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      case "H":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold";
      case "WF":
        return "bg-purple-500/20 text-purple-300 border-purple-500/40";
      case "SWF":
        return "bg-cyan-500/20 text-cyan-300 border-cyan-500/40";
      case "DROP":
        return "bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold";
      default:
        return "text-slate-600";
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
            🎬 Film Shooting Schedule Optimization Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Two-Level Hierarchical Decomposition: Cross-Boarding (CP-SAT MILP) & Intra-Day
            Stripboard (TSP-SDST).
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
            disabled={optimizing || rescheduling}
            onClick={handleOptimize}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            {optimizing ? "Solving CP-SAT..." : "⚡ Optimize Shoot"}
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
            label="Solver Status"
            value={<StatusBadge status={result.status || "OPTIMAL"} />}
            subValue={`Solve Time: ${result.solve_time_seconds?.toFixed(3) || "0.035"}s`}
          />
          <MetricCard
            label="Total Shoot Days"
            value={result.stripboard?.total_shoot_days ?? result.total_shooting_days ?? 2}
            subValue={`Calendar Horizon: ${result.stripboard?.total_calendar_days || dataset.max_shooting_days || 10} days`}
          />
          <MetricCard
            label="Objective Cost"
            value={`$${(result.objective_cost || 0).toLocaleString()}`}
            subValue="Talent holds + moves + leases"
          />
          <MetricCard
            label="Cast Members"
            value={dataset.talents?.length || dataset.cast?.length || 0}
            subValue={`${dataset.scenes?.length || 0} Scenes Scheduled`}
          />
        </div>
      )}

      {/* Solver Configuration Drawer */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-xs flex flex-wrap items-center justify-between gap-4">
        <span className="font-semibold text-slate-300">Active Solver Constraints:</span>
        <div className="flex flex-wrap items-center gap-6 text-slate-300">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={enableSoundstageLeases}
              onChange={(e) => setEnableSoundstageLeases(e.target.checked)}
              className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
            />
            Continuous Soundstage Leases
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={enableHazardDeferral}
              onChange={(e) => setEnableHazardDeferral(e.target.checked)}
              className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
            />
            Bond Stunt Deferral (&ge;75%)
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={enableDropPickup}
              onChange={(e) => setEnableDropPickup(e.target.checked)}
              className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
            />
            SAG-AFTRA 10-Day Drop & Pickup
          </label>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 text-xs font-semibold">
        <button
          type="button"
          onClick={() => setActiveTab("stripboard")}
          className={`px-4 py-2.5 border-b-2 transition ${
            activeTab === "stripboard"
              ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          📋 Master Stripboard
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("dood")}
          className={`px-4 py-2.5 border-b-2 transition ${
            activeTab === "dood"
              ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          👥 Day-Out-of-Days (DOOD) Matrix
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("callsheet")}
          className={`px-4 py-2.5 border-b-2 transition ${
            activeTab === "callsheet"
              ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          📜 Daily Call Sheets
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("reschedule")}
          className={`px-4 py-2.5 border-b-2 transition ${
            activeTab === "reschedule"
              ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          ⚡ Reschedule & Disruption Simulator
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("json")}
          className={`px-4 py-2.5 border-b-2 transition ${
            activeTab === "json"
              ? "border-indigo-500 text-indigo-400 bg-indigo-500/10"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          JSON Payload & Results
        </button>
      </div>

      {/* TAB 1: MASTER STRIPBOARD */}
      {activeTab === "stripboard" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Industry Color Codes:{" "}
              <span className="bg-slate-100 text-slate-900 px-2 py-0.5 rounded font-bold mr-1">
                INT. DAY
              </span>
              <span className="bg-amber-300 text-amber-950 px-2 py-0.5 rounded font-bold mr-1">
                EXT. DAY
              </span>
              <span className="bg-emerald-800 text-emerald-100 px-2 py-0.5 rounded font-bold mr-1">
                INT. NIGHT
              </span>
              <span className="bg-sky-800 text-sky-100 px-2 py-0.5 rounded font-bold">
                EXT. NIGHT
              </span>
            </span>
            <span>
              Total Strips:{" "}
              {result?.stripboard
                ? result.stripboard.days.reduce((acc, d) => acc + d.strips.length, 0)
                : dataset.scenes.length}
            </span>
          </div>

          {result?.stripboard ? (
            <div className="space-y-6">
              {result.stripboard.days.map((day) => (
                <div
                  key={day.day_number}
                  className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden shadow-md"
                >
                  {/* Day Header Banner */}
                  <div
                    className={`px-4 py-2 text-xs flex items-center justify-between border-b border-slate-800 ${
                      day.is_rest_day
                        ? "bg-slate-900/90 text-amber-400 font-semibold"
                        : "bg-slate-900 text-slate-200 font-bold"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span>DAY {day.day_number}</span>
                      <span className="text-slate-400 font-normal">({day.calendar_date})</span>
                      {day.is_rest_day && (
                        <span className="rounded bg-amber-500/20 text-amber-300 px-2 py-0.5 border border-amber-500/30 text-[10px]">
                          REST DAY / INAUSPICIOUS BLACKOUT
                        </span>
                      )}
                    </div>
                    {!day.is_rest_day && (
                      <div className="text-slate-400 font-mono text-[11px]">
                        {day.strips.length} Strips • {day.total_duration_minutes} mins •{" "}
                        {day.total_page_eighths}/8 Pages
                      </div>
                    )}
                  </div>

                  {/* Scene Strips */}
                  {day.strips.length > 0 ? (
                    <div className="divide-y divide-slate-800">
                      {day.strips.map((strip) => (
                        <div
                          key={strip.scene_id}
                          className={`p-3 text-xs flex items-center justify-between shadow-sm transition hover:brightness-105 ${getStripColorClass(
                            strip.strip_color,
                          )}`}
                        >
                          <div className="flex items-center gap-4">
                            <span className="w-14 font-mono font-bold text-sm">
                              {strip.scene_number}
                            </span>
                            <div>
                              <div className="font-semibold text-xs">
                                {strip.setting} {strip.time_of_day} • {strip.location_name}
                              </div>
                              <div className="text-[11px] opacity-80 mt-0.5">
                                Part {strip.part} • {strip.page_eighths}/8 pgs • Cast IDs: [
                                {strip.cast_ids?.join(", ")}]
                              </div>
                            </div>
                          </div>

                          <div className="text-right font-mono text-xs font-semibold">
                            <div>{strip.duration_minutes} min</div>
                            {strip.is_second_unit && (
                              <span className="rounded bg-rose-600 text-white px-1.5 py-0.2 text-[9px] font-bold">
                                2ND UNIT
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    !day.is_rest_day && (
                      <div className="p-4 text-xs text-center text-slate-600 italic">
                        No scenes scheduled on this calendar day.
                      </div>
                    )
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center text-slate-500 text-sm">
              Click &quot;⚡ Optimize Shoot&quot; above to compute the master stripboard.
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DAY-OUT-OF-DAYS (DOOD) CAST MATRIX */}
      {activeTab === "dood" && (
        <div className="space-y-4">
          <div className="text-xs text-slate-400">
            SAG-AFTRA Consecutive Employment Tracking & 10-Day Drop-and-Pickup (DPU) Compliance
          </div>

          {result?.dood_reports && result.dood_reports.length > 0 ? (
            <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                  <tr>
                    <th className="p-3">Character</th>
                    <th className="p-3">Performer</th>
                    {Array.from({
                      length:
                        result.stripboard?.total_calendar_days || dataset.max_shooting_days || 10,
                    }).map((_, i) => (
                      <th key={i + 1} className="p-2 text-center font-mono">
                        D{i + 1}
                      </th>
                    ))}
                    <th className="p-3 text-center">Work</th>
                    <th className="p-3 text-center">Hold</th>
                    <th className="p-3 text-center font-bold">Total Paid</th>
                    <th className="p-3 text-right">Est. Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-mono">
                  {result.dood_reports.map((report) => (
                    <tr key={report.talent_id} className="hover:bg-slate-900/40">
                      <td className="p-3 font-sans font-semibold text-white">
                        {report.character_name}
                      </td>
                      <td className="p-3 font-sans text-slate-300">{report.talent_name}</td>
                      {Array.from({
                        length:
                          result.stripboard?.total_calendar_days || dataset.max_shooting_days || 10,
                      }).map((_, i) => {
                        const dayNum = i + 1;
                        const code = report.daily_codes[dayNum] || ".";
                        return (
                          <td key={dayNum} className="p-2 text-center">
                            <span
                              className={`inline-block w-8 py-0.5 text-center text-[10px] rounded border ${getDoodBadgeClass(code)}`}
                            >
                              {code}
                            </span>
                          </td>
                        );
                      })}
                      <td className="p-3 text-center text-emerald-400">
                        {report.total_work_days}d
                      </td>
                      <td className="p-3 text-center text-amber-400">{report.total_hold_days}d</td>
                      <td className="p-3 text-center font-bold text-white bg-slate-900/60">
                        {report.total_paid_days}d
                      </td>
                      <td className="p-3 text-right font-sans font-semibold text-slate-200">
                        ${report.estimated_cost?.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center text-slate-500 text-sm">
              DOOD matrix will appear once optimization is executed.
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DAILY CALL SHEETS */}
      {activeTab === "callsheet" && (
        <div className="space-y-6">
          {result?.call_sheets && Object.keys(result.call_sheets).length > 0 ? (
            <div>
              {/* Day Selector */}
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-semibold text-slate-400">Select Production Day:</span>
                <div className="flex items-center gap-1.5 overflow-x-auto">
                  {Object.keys(result.call_sheets).map((dayKey) => {
                    const dNum = Number(dayKey);
                    return (
                      <button
                        type="button"
                        key={dNum}
                        onClick={() => setSelectedCallSheetDay(dNum)}
                        className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                          selectedCallSheetDay === dNum
                            ? "bg-indigo-600 text-white"
                            : "bg-slate-900 text-slate-400 border border-slate-800 hover:bg-slate-800"
                        }`}
                      >
                        Day {dNum}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Active Call Sheet */}
              {result.call_sheets[selectedCallSheetDay] && (
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6 space-y-6 text-xs">
                  {/* Call Sheet Header */}
                  <div className="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div>
                      <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                        Official Production Call Sheet
                      </div>
                      <h2 className="text-xl font-bold text-white mt-1">
                        {result.call_sheets[selectedCallSheetDay].project_title}
                      </h2>
                      <div className="text-slate-400 mt-0.5">
                        Day {result.call_sheets[selectedCallSheetDay].day_number} •{" "}
                        {result.call_sheets[selectedCallSheetDay].calendar_date} • Weather:{" "}
                        {result.call_sheets[selectedCallSheetDay].expected_weather}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-center font-mono">
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Crew Call</div>
                        <div className="text-sm font-bold text-white">
                          {result.call_sheets[selectedCallSheetDay].general_crew_call}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Shooting Call</div>
                        <div className="text-sm font-bold text-indigo-400">
                          {result.call_sheets[selectedCallSheetDay].shooting_call}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">First Meal</div>
                        <div className="text-sm font-bold text-amber-400">
                          {result.call_sheets[selectedCallSheetDay].first_meal_due}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Sunset</div>
                        <div className="text-sm font-bold text-slate-300">
                          {result.call_sheets[selectedCallSheetDay].sunset_time}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Scene Shooting Schedule */}
                  <div>
                    <h3 className="font-bold text-white mb-3">Intra-Day Shooting Schedule</h3>
                    <div className="overflow-x-auto rounded-xl border border-slate-800">
                      <table className="w-full text-left">
                        <thead className="bg-slate-900 text-slate-400 font-semibold">
                          <tr>
                            <th className="p-2.5">Time</th>
                            <th className="p-2.5">Scene #</th>
                            <th className="p-2.5">Setting & Time</th>
                            <th className="p-2.5">Location</th>
                            <th className="p-2.5">Cast IDs</th>
                            <th className="p-2.5 text-right">Pages</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono">
                          {result.call_sheets[selectedCallSheetDay].scene_entries?.map((s, idx) => (
                            <tr key={idx} className="hover:bg-slate-900/30">
                              <td className="p-2.5 text-indigo-300 font-bold">
                                {s.start_time} - {s.end_time}
                              </td>
                              <td className="p-2.5 font-bold text-white font-sans">
                                {s.scene_number}
                              </td>
                              <td className="p-2.5 text-slate-300 font-sans">{s.setting}</td>
                              <td className="p-2.5 text-slate-400 font-sans">{s.location_name}</td>
                              <td className="p-2.5 text-amber-300">[{s.cast_ids?.join(", ")}]</td>
                              <td className="p-2.5 text-right font-sans">{s.page_eighths}/8</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Backward-Calculated Actor Call Times */}
                  <div>
                    <h3 className="font-bold text-white mb-3">
                      Talent Arrival & Staggered HMU Matrix
                    </h3>
                    <div className="overflow-x-auto rounded-xl border border-slate-800">
                      <table className="w-full text-left">
                        <thead className="bg-slate-900 text-slate-400 font-semibold">
                          <tr>
                            <th className="p-2.5">Character</th>
                            <th className="p-2.5">Performer</th>
                            <th className="p-2.5 text-indigo-300">Pickup Call</th>
                            <th className="p-2.5 text-purple-300">HMU Call</th>
                            <th className="p-2.5 text-amber-300">Wardrobe</th>
                            <th className="p-2.5 text-emerald-400 font-bold">On Set</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono">
                          {result.call_sheets[selectedCallSheetDay].character_calls?.map((c) => (
                            <tr key={c.talent_id} className="hover:bg-slate-900/30">
                              <td className="p-2.5 font-sans font-bold text-white">
                                {c.character_name}
                              </td>
                              <td className="p-2.5 font-sans text-slate-300">{c.actor_name}</td>
                              <td className="p-2.5 text-indigo-300">{c.pickup_call}</td>
                              <td className="p-2.5 text-purple-300">{c.hmu_call}</td>
                              <td className="p-2.5 text-amber-300">{c.wardrobe_call}</td>
                              <td className="p-2.5 text-emerald-400 font-bold bg-slate-900/60">
                                {c.set_call}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Hospital Emergency Info */}
                  <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 text-slate-400 flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-rose-400">
                        Emergency Medical Center:{" "}
                      </span>
                      {result.call_sheets[selectedCallSheetDay].hospital_info}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center text-slate-500 text-sm">
              Call sheets will be generated once optimization runs.
            </div>
          )}
        </div>
      )}

      {/* TAB 4: RESCHEDULE & DISRUPTION SIMULATOR */}
      {activeTab === "reschedule" && (
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6 space-y-6 text-xs">
          <div>
            <h2 className="text-base font-bold text-white">
              Dynamic Rolling-Horizon Rescheduling Console
            </h2>
            <p className="text-slate-400 mt-1">
              Simulate operational disruptions (e.g. unexpected monsoon rain on exterior dune set),
              preserve past completed days, and dynamically activate interior cover sets.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-y border-slate-800 py-4">
            <div>
              <label className="block text-slate-400 mb-1">Completed Production Days</label>
              <div className="flex items-center gap-2">
                {[1, 2, 3].map((d) => (
                  <button
                    type="button"
                    key={d}
                    onClick={() => {
                      if (completedDays.includes(d)) {
                        setCompletedDays(completedDays.filter((x) => x !== d));
                      } else {
                        setCompletedDays([...completedDays, d]);
                      }
                    }}
                    className={`rounded px-3 py-1 text-xs font-mono transition ${
                      completedDays.includes(d)
                        ? "bg-emerald-600 text-white font-bold"
                        : "bg-slate-900 text-slate-400 border border-slate-800"
                    }`}
                  >
                    Day {d} {completedDays.includes(d) ? "✔" : ""}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">
                Simulate Weather Disruption on Day
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={1}
                  max={dataset.max_shooting_days || 10}
                  value={disruptedDay}
                  onChange={(e) => setDisruptedDay(Number(e.target.value))}
                  className="w-20 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-white"
                />
                <select
                  value={disruptionWeather}
                  onChange={(e) => setDisruptionWeather(e.target.value)}
                  className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-white"
                >
                  <option value="RAIN">Rain (Exterior Disrupt)</option>
                  <option value="MONSOON">Monsoon Torrent</option>
                  <option value="OVERCAST">Overcast</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Cover Set Policy</label>
              <label className="flex items-center gap-2 cursor-pointer mt-2 text-slate-300">
                <input
                  type="checkbox"
                  checked={activateCoverSets}
                  onChange={(e) => setActivateCoverSets(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0"
                />
                Activate Interior Cover Sets (Scene 25_COVER)
              </label>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-slate-400">
              When triggered, elapsed days 1..{Math.max(...completedDays, 0)} will be locked,
              disrupted exterior scenes deferred, and cover sets substituted into interior
              soundstages.
            </div>
            <button
              type="button"
              disabled={rescheduling}
              onClick={handleReschedule}
              className="rounded-lg bg-amber-600 px-5 py-2 font-bold text-white shadow-lg hover:bg-amber-500 disabled:opacity-50 transition"
            >
              {rescheduling ? "Re-optimizing..." : "⚡ Execute Reschedule"}
            </button>
          </div>
        </div>
      )}

      {/* TAB 5: JSON VIEW */}
      {activeTab === "json" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <JsonViewer
            title="Production Dataset (Input Fixture)"
            data={dataset}
            initialExpanded={true}
          />
          <JsonViewer
            title="Optimized Solution (Output Response)"
            data={result || { message: "Click 'Optimize Shoot' to compute shooting schedule" }}
            initialExpanded={true}
          />
        </div>
      )}
    </div>
  );
}
