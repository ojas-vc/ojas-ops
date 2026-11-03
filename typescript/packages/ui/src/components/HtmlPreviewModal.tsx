"use client";

import type { FC } from "react";

export interface HtmlPreviewModalProps {
  isOpen?: boolean;
  onClose: () => void;
  title: string;
  htmlContent: string;
}

export const HtmlPreviewModal: FC<HtmlPreviewModalProps> = ({
  isOpen = true,
  onClose,
  title,
  htmlContent,
}) => {
  if (isOpen === false) return null;

  const handlePrint = () => {
    const iframe = document.getElementById("html-preview-iframe") as HTMLIFrameElement;
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="flex h-[90vh] w-[95vw] max-w-6xl flex-col rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <h2 className="text-base font-semibold text-white">{title}</h2>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handlePrint}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition"
            >
              Print / Save PDF
            </button>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg bg-slate-800 p-1.5 text-slate-400 hover:bg-slate-700 hover:text-white transition"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex-1 p-4 bg-slate-900/40">
          <iframe
            id="html-preview-iframe"
            title="Preview"
            srcDoc={htmlContent}
            sandbox="allow-same-origin allow-modals allow-popups"
            className="h-full w-full rounded-xl border border-slate-800 bg-white"
          />
        </div>
      </div>
    </div>
  );
};
