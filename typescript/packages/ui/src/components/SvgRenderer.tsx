"use client";

import { type FC, useState } from "react";

export interface SvgRendererProps {
  svgContent: string;
  title?: string;
  filename?: string;
  downloadFilename?: string;
}

export const SvgRenderer: FC<SvgRendererProps> = ({
  svgContent,
  title = "Vector Visualization",
  filename = "visualization.svg",
  downloadFilename,
}) => {
  const [zoom, setZoom] = useState(1.0);
  const activeFilename = downloadFilename || filename;

  const handleDownload = () => {
    const blob = new Blob([svgContent], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = activeFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 shadow-md">
      <div className="flex items-center justify-between border-b border-slate-800/80 bg-slate-900/60 px-4 py-2.5">
        <span className="text-xs font-semibold text-slate-300">{title}</span>

        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-lg border border-slate-800 bg-slate-900 p-0.5">
            <button
              type="button"
              onClick={() => setZoom((prev) => Math.max(prev - 0.2, 0.4))}
              className="rounded px-2 py-0.5 text-xs text-slate-300 hover:bg-slate-800"
            >
              -
            </button>
            <span className="px-2 text-xs font-mono text-slate-400">{Math.round(zoom * 100)}%</span>
            <button
              type="button"
              onClick={() => setZoom((prev) => Math.min(prev + 0.2, 2.5))}
              className="rounded px-2 py-0.5 text-xs text-slate-300 hover:bg-slate-800"
            >
              +
            </button>
          </div>

          <button
            type="button"
            onClick={handleDownload}
            className="rounded-lg bg-indigo-600/80 hover:bg-indigo-600 px-3 py-1 text-xs font-semibold text-white transition shadow-sm"
          >
            Download SVG
          </button>
        </div>
      </div>

      <div className="overflow-auto p-4 flex justify-center items-center min-h-[300px]">
        <div
          style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
          className="transition-transform duration-150"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      </div>
    </div>
  );
};
