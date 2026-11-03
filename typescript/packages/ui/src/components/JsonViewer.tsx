"use client";

import { type FC, useState } from "react";

export interface JsonViewerProps {
  data: unknown;
  title?: string;
  initialCollapsed?: boolean;
  initialExpanded?: boolean;
}

export const JsonViewer: FC<JsonViewerProps> = ({
  data,
  title = "Payload JSON",
  initialCollapsed,
  initialExpanded,
}) => {
  const [collapsed, setCollapsed] = useState(
    initialCollapsed ?? (initialExpanded !== undefined ? !initialExpanded : false),
  );
  const [copied, setCopied] = useState(false);

  const jsonStr = JSON.stringify(data, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonStr);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 font-mono text-xs shadow-inner">
      <div className="flex items-center justify-between border-b border-slate-800/80 bg-slate-900/60 px-4 py-2">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="text-slate-400 hover:text-slate-200 transition"
          >
            {collapsed ? "▶" : "▼"}
          </button>
          <span className="font-semibold text-slate-300">{title}</span>
          <span className="text-[10px] text-slate-500">
            ({typeof data === "object" && data !== null ? Object.keys(data as object).length : 1}{" "}
            keys)
          </span>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="rounded px-2 py-0.5 text-[10px] font-sans font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
        >
          {copied ? "Copied!" : "Copy JSON"}
        </button>
      </div>

      {!collapsed && (
        <pre className="max-h-96 overflow-auto p-4 text-slate-300 leading-relaxed scrollbar-thin scrollbar-thumb-slate-800">
          <code>{jsonStr}</code>
        </pre>
      )}
    </div>
  );
};
