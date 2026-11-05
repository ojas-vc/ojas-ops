"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { client } from "../../../lib/api";
import { SvgRenderer, HtmlPreviewModal } from "@ojas-ops/ui";

export default function ProjectExportsPage() {
  const params = useParams();
  const projectId = (params?.id as string) || "";

  const [activeTab, setActiveTab] = useState<"stripboard" | "gantt" | "dood" | "callsheet">("stripboard");
  const [stripboardSvg, setStripboardSvg] = useState<string>("");
  const [ganttSvg, setGanttSvg] = useState<string>("");
  const [callSheetHtml, setCallSheetHtml] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [showCallSheetModal, setShowCallSheetModal] = useState<boolean>(false);

  useEffect(() => {
    async function fetchVisualizations() {
      try {
        setLoading(true);

        // 1. Fetch Stripboard SVG
        const stripRes = await client.visualizations.renderStripboardSvg({
          stripboard_data: {
            title: `Stripboard: ${projectId}`,
            days: [
              {
                day: 1,
                date: "2026-11-12",
                location: "Warehouse Stage",
                scenes: [
                  { id: "S1", title: "Int. Warehouse - Day", pages: "2 4/8", cast: "A1, A2" },
                  { id: "S3", title: "Int. Safehouse - Day", pages: "1 2/8", cast: "A2, A3" },
                ],
              },
              {
                day: 2,
                date: "2026-11-13",
                location: "Pier",
                scenes: [{ id: "S2", title: "Ext. Pier - Sunset", pages: "1 0/8", cast: "A1" }],
              },
            ],
          },
        }).catch(() => ({ svg: "<svg><text y='20'>Stripboard</text></svg>" }));
        setStripboardSvg(stripRes.svg);

        // 2. Fetch Gantt SVG
        const ganttRes = await client.visualizations.renderGanttSvg({
          tasks: [
            { id: "Scene 1", resource: "Main Unit", start: 0, end: 12 },
            { id: "Scene 3", resource: "Main Unit", start: 12, end: 24 },
            { id: "Scene 2", resource: "2nd Unit", start: 24, end: 36 },
          ],
          resources: ["Main Unit", "2nd Unit"],
          total_makespan: 36,
        }).catch(() => ({ svg: "<svg><text y='20'>Gantt</text></svg>" }));
        setGanttSvg(ganttRes.svg);

        // 3. Prepare Call Sheet HTML
        setCallSheetHtml(
          `<div style="font-family: monospace; padding: 24px; color: #1e293b; background: white;">
            <h1 style="margin: 0; font-size: 20px;">DAILY CALL SHEET: DAY 1 OF 3</h1>
            <p style="margin: 4px 0 16px; font-size: 12px; color: #64748b;">Project: ${projectId} | Date: Thursday, Nov 12, 2026</p>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 16px;">
              <thead>
                <tr style="background: #f1f5f9; text-align: left;">
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Crew Call</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Shooting Call</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Estimated Wrap</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Meal Break</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">06:00 AM</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">07:00 AM</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">19:00 PM</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">13:00 PM (1h)</td>
                </tr>
              </tbody>
            </table>
            <h3 style="font-size: 14px; margin-bottom: 8px;">SCHEDULED SCENES</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
              <thead>
                <tr style="background: #f8fafc; text-align: left;">
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Scene</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Set & Description</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">D/N</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Pages</th>
                  <th style="padding: 6px; border: 1px solid #cbd5e1;">Cast</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">1</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">INT. WAREHOUSE - Briefing</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">DAY</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">2 4/8</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">A1, A2</td>
                </tr>
                <tr>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">3</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">INT. SAFEHOUSE - Hideout</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">DAY</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">1 2/8</td>
                  <td style="padding: 6px; border: 1px solid #cbd5e1;">A2, A3</td>
                </tr>
              </tbody>
            </table>
          </div>`
        );
      } catch {
        // Fallback
      } finally {
        setLoading(false);
      }
    }

    if (projectId) {
      fetchVisualizations();
    }
  }, [projectId]);

  const handleDownloadSvg = (svgContent: string, filename: string) => {
    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Link href={`/projects/${encodeURIComponent(projectId)}`} className="hover:text-slate-400">
              &larr; Workspace
            </Link>
            <span>/</span>
            <span>Export Center</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            Operational Artifact Visualizer & Export Center
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Production-grade vector SVG stripboards, interactive Gantt charts, and formatted call sheets.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-900 p-1 text-xs">
          {(["stripboard", "gantt", "callsheet"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-md px-3 py-1.5 capitalize font-medium transition ${
                activeTab === tab
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-sm text-slate-400">Rendering visual artifacts...</div>
      ) : (
        <div className="space-y-6">
          {/* Tab 1: Stripboard */}
          {activeTab === "stripboard" && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-white">Vector SVG Stripboard</h2>
                  <p className="text-xs text-slate-400">
                    Color-coded INT/EXT DAY/NIGHT stripboard with talent cross-checks and shoot day dividers.
                  </p>
                </div>
                <button
                  onClick={() => handleDownloadSvg(stripboardSvg, `stripboard-${projectId}.svg`)}
                  className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition"
                >
                  Download SVG &darr;
                </button>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4 overflow-x-auto flex justify-center">
                <SvgRenderer svgContent={stripboardSvg} />
              </div>
            </div>
          )}

          {/* Tab 2: Gantt Chart */}
          {activeTab === "gantt" && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-white">Resource Gantt Chart</h2>
                  <p className="text-xs text-slate-400">
                    Timeline scheduling with machine and camera unit resource tracks.
                  </p>
                </div>
                <button
                  onClick={() => handleDownloadSvg(ganttSvg, `gantt-${projectId}.svg`)}
                  className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition"
                >
                  Download Gantt SVG &darr;
                </button>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4 overflow-x-auto flex justify-center">
                <SvgRenderer svgContent={ganttSvg} />
              </div>
            </div>
          )}

          {/* Tab 3: Call Sheet */}
          {activeTab === "callsheet" && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-white">Daily Call Sheet Docket</h2>
                  <p className="text-xs text-slate-400">
                    Industry standard call sheet preview with scene breakdown and meal intervals.
                  </p>
                </div>
                <button
                  onClick={() => setShowCallSheetModal(true)}
                  className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition"
                >
                  Full-Screen Preview &rarr;
                </button>
              </div>

              <div
                className="rounded-lg border border-slate-800 bg-white p-4 max-h-96 overflow-y-auto"
                dangerouslySetInnerHTML={{ __html: callSheetHtml }}
              />

              <HtmlPreviewModal
                isOpen={showCallSheetModal}
                onClose={() => setShowCallSheetModal(false)}
                htmlContent={callSheetHtml}
                title={`Daily Call Sheet: ${projectId}`}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
