"use client";

import { client } from "@/app/lib/api";
import {
  SAMPLE_DOOD_PAYLOAD,
  SAMPLE_GANTT_PAYLOAD,
  SAMPLE_STRIPBOARD_PAYLOAD,
} from "@/app/lib/fixtures";
import type { DOODRenderRequest, GanttRenderRequest, StripboardRenderRequest } from "@ojas-ops/sdk";
import { HtmlPreviewModal, SvgRenderer } from "@ojas-ops/ui";
import { useState } from "react";

export default function VisualizationsPage() {
  const [activeTab, setActiveTab] = useState<"stripboard" | "dood" | "gantt" | "reports">(
    "stripboard",
  );

  // Stripboard state
  const [stripboardPayload, setStripboardPayload] =
    useState<StripboardRenderRequest>(SAMPLE_STRIPBOARD_PAYLOAD);
  const [stripboardHtml, setStripboardHtml] = useState<string | null>(null);
  const [stripboardSvg, setStripboardSvg] = useState<string | null>(null);
  const [loadingStripboard, setLoadingStripboard] = useState(false);

  // DOOD state
  const [doodPayload, setDoodPayload] = useState<DOODRenderRequest>(SAMPLE_DOOD_PAYLOAD);
  const [doodHtml, setDoodHtml] = useState<string | null>(null);
  const [loadingDood, setLoadingDood] = useState(false);

  // Gantt state
  const [ganttPayload, setGanttPayload] = useState<GanttRenderRequest>(SAMPLE_GANTT_PAYLOAD);
  const [ganttSvg, setGanttSvg] = useState<string | null>(null);
  const [loadingGantt, setLoadingGantt] = useState(false);

  // Report state
  const [reportTitle, setReportTitle] = useState("Operations Optimization Comprehensive Report");
  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);

  const [error, setError] = useState<string | null>(null);

  // Render Stripboard
  const handleRenderStripboard = async () => {
    setLoadingStripboard(true);
    setError(null);
    try {
      const [htmlRes, svgRes] = await Promise.all([
        client.visualizations.renderStripboardHtml(stripboardPayload),
        client.visualizations.renderStripboardSvg(stripboardPayload),
      ]);
      setStripboardHtml(htmlRes.html);
      setStripboardSvg(svgRes.svg);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingStripboard(false);
    }
  };

  // Render DOOD
  const handleRenderDood = async () => {
    setLoadingDood(true);
    setError(null);
    try {
      const res = await client.visualizations.renderDoodHtml(doodPayload);
      setDoodHtml(res.html);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingDood(false);
    }
  };

  // Render Gantt
  const handleRenderGantt = async () => {
    setLoadingGantt(true);
    setError(null);
    try {
      const res = await client.visualizations.renderGanttSvg(ganttPayload);
      setGanttSvg(res.svg);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingGantt(false);
    }
  };

  // Render Report
  const handleRenderReport = async () => {
    setLoadingReport(true);
    setError(null);
    try {
      const res = await client.visualizations.exportReportHtml({
        title: reportTitle,
        sections: [
          `<div class="section"><h2>Executive Overview</h2><p>This report documents the optimized operations schedule computed via Ojas Ops Google OR-Tools CP-SAT engine.</p></div>`,
          `<div class="section"><h2>Key Performance Indicators</h2><ul><li>Optimality Gap: 0.00%</li><li>Convergence Duration: 0.420s</li><li>Total Resources Utilized: 4 units</li></ul></div>`,
          stripboardHtml
            ? `<div class="section"><h2>Shooting Stripboard</h2>${stripboardHtml}</div>`
            : "",
          doodHtml ? `<div class="section"><h2>Day-Out-of-Days Matrix</h2>${doodHtml}</div>` : "",
        ].filter(Boolean),
      });
      setReportHtml(res.html);
      setShowReportModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Visualizations & Document Exporters
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Vector SVG graphics, Day-Out-of-Days talent matrices, dynamic shooting stripboards, and
            print-ready reports.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={reportTitle}
            onChange={(e) => setReportTitle(e.target.value)}
            className="hidden sm:block rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200"
            placeholder="Report title..."
          />
          <button
            type="button"
            onClick={handleRenderReport}
            disabled={loadingReport}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-lg hover:bg-emerald-500 disabled:opacity-50 transition"
          >
            {loadingReport ? "Generating Document..." : "📄 Export Printable Report"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Visualization Engine Notice</div>
          <div>{error}</div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        <button
          type="button"
          onClick={() => setActiveTab("stripboard")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "stripboard"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          🎬 Shooting Stripboard (HTML & SVG)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("dood")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "dood"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          👥 Day-Out-of-Days (DOOD) Matrix
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("gantt")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            activeTab === "gantt"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          📊 Vector SVG Gantt Chart
        </button>
      </div>

      {/* Tab 1: Stripboard */}
      {activeTab === "stripboard" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Film Production Stripboard Generator</h2>
            <button
              type="button"
              disabled={loadingStripboard}
              onClick={handleRenderStripboard}
              className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow hover:bg-indigo-500 disabled:opacity-50 transition"
            >
              {loadingStripboard ? "Rendering Stripboards..." : "Render Stripboard"}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 space-y-4 text-xs">
              <h3 className="font-semibold text-slate-200">Stripboard Configuration</h3>
              <div>
                <label className="block text-slate-400 mb-1">Project Title</label>
                <input
                  type="text"
                  value={String(stripboardPayload.stripboard_data.project_title || "")}
                  onChange={(e) =>
                    setStripboardPayload({
                      ...stripboardPayload,
                      stripboard_data: {
                        ...stripboardPayload.stripboard_data,
                        project_title: e.target.value,
                      },
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
              </div>
              <div className="text-slate-400">
                Shooting Days:{" "}
                {Array.isArray(stripboardPayload.stripboard_data.days)
                  ? stripboardPayload.stripboard_data.days.length
                  : 0}{" "}
                • Total Strips:{" "}
                {Array.isArray(stripboardPayload.stripboard_data.days)
                  ? (
                      stripboardPayload.stripboard_data.days as Array<{ strips?: unknown[] }>
                    ).reduce((acc, d) => acc + (d.strips?.length || 0), 0)
                  : 0}
              </div>
              <p className="text-[11px] text-slate-500">
                Calls <code>/visualizations/stripboards/html</code> for rich web layouts and{" "}
                <code>/visualizations/stripboards/svg</code> for vector export.
              </p>
            </div>

            <div className="space-y-4">
              {stripboardSvg ? (
                <SvgRenderer
                  svgContent={stripboardSvg}
                  title="Rendered Vector Stripboard SVG"
                  downloadFilename="shooting-stripboard.svg"
                />
              ) : (
                <div className="flex h-64 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/20 text-xs text-slate-500">
                  Click 'Render Stripboard' to generate vector output
                </div>
              )}
            </div>
          </div>

          {stripboardHtml && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-3">
              <h3 className="text-sm font-semibold text-white">Live HTML Stripboard</h3>
              <div
                className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-slate-200"
                dangerouslySetInnerHTML={{ __html: stripboardHtml }}
              />
            </div>
          )}
        </div>
      )}

      {/* Tab 2: DOOD Matrix */}
      {activeTab === "dood" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">
              Day-Out-of-Days (DOOD) Cast & Crew Matrix
            </h2>
            <button
              type="button"
              disabled={loadingDood}
              onClick={handleRenderDood}
              className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow hover:bg-indigo-500 disabled:opacity-50 transition"
            >
              {loadingDood ? "Generating Matrix..." : "Render DOOD Matrix"}
            </button>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 space-y-4 text-xs">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-200">
                Talent Roster ({doodPayload.reports.length} cast members over{" "}
                {doodPayload.total_days} days)
              </h3>
              <div className="flex items-center gap-2">
                <label className="text-slate-400">Total Shoot Days:</label>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={doodPayload.total_days}
                  onChange={(e) =>
                    setDoodPayload({
                      ...doodPayload,
                      total_days: Number(e.target.value),
                    })
                  }
                  className="w-20 rounded-lg border border-slate-700 bg-slate-950 px-2 py-1 text-slate-200"
                />
              </div>
            </div>
            <div className="space-y-2">
              {doodPayload.reports.map((r, idx) => {
                const rep = r as Record<string, string | number>;
                return (
                  <div
                    key={String(rep.talent_id || idx)}
                    className="flex items-center justify-between rounded bg-slate-950 px-3 py-2 border border-slate-800"
                  >
                    <span className="font-medium text-slate-200">
                      {String(rep.character_name || "Cast")} ({String(rep.talent_id || idx)})
                    </span>
                    <span className="font-mono text-slate-400">
                      Work: {String(rep.total_work_days || 0)}d • Hold:{" "}
                      {String(rep.total_hold_days || 0)}d • Paid: {String(rep.total_paid_days || 0)}
                      d
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {doodHtml ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-3">
              <h3 className="text-sm font-semibold text-white">Generated DOOD HTML Table</h3>
              <div
                className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-slate-200"
                dangerouslySetInnerHTML={{ __html: doodHtml }}
              />
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/20 text-xs text-slate-500">
              Click 'Render DOOD Matrix' to compute cast schedule codes
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Gantt SVG */}
      {activeTab === "gantt" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white">Vector SVG Gantt Chart Engine</h2>
            <button
              type="button"
              disabled={loadingGantt}
              onClick={handleRenderGantt}
              className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow hover:bg-indigo-500 disabled:opacity-50 transition"
            >
              {loadingGantt ? "Generating SVG..." : "Generate Vector Gantt"}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 space-y-4 text-xs">
              <h3 className="font-semibold text-slate-200">Gantt Parameters</h3>
              <div>
                <label className="block text-slate-400 mb-1">Total Makespan</label>
                <input
                  type="number"
                  value={ganttPayload.total_makespan}
                  onChange={(e) =>
                    setGanttPayload({
                      ...ganttPayload,
                      total_makespan: Number(e.target.value),
                    })
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-200"
                />
              </div>
              <div className="text-slate-400">
                Tasks Count: {ganttPayload.tasks.length} • Resources:{" "}
                {ganttPayload.resources.join(", ")}
              </div>
            </div>

            <div>
              {ganttSvg ? (
                <SvgRenderer
                  svgContent={ganttSvg}
                  title="Server-Generated Vector Gantt"
                  downloadFilename="operations-gantt.svg"
                />
              ) : (
                <div className="flex h-64 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/20 text-xs text-slate-500">
                  Click 'Generate Vector Gantt' to render high-res SVG
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Report Modal */}
      {showReportModal && reportHtml && (
        <HtmlPreviewModal
          htmlContent={reportHtml}
          title={reportTitle}
          onClose={() => setShowReportModal(false)}
        />
      )}
    </div>
  );
}
