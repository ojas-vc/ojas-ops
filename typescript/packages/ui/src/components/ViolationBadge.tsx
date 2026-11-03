import type { Violation } from "@ojas-ops/sdk";
import type { FC } from "react";

export interface ViolationBadgeProps {
  violation?: Violation;
  type?: string;
  severity?: "HARD" | "SOFT" | "critical" | "warning" | string;
  message?: string;
}

export const ViolationBadge: FC<ViolationBadgeProps> = ({ violation, type, severity, message }) => {
  const actualSeverity = violation?.severity || severity || "HARD";
  const isHard =
    actualSeverity === "HARD" || actualSeverity === "critical" || actualSeverity === "CRITICAL";
  const actualType = violation?.constraint_type || type || "CONSTRAINT_BREACH";
  const actualMsg = violation?.message || message;

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-lg px-2.5 py-1 text-xs font-medium border ${
        isHard
          ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
          : "border-amber-500/40 bg-amber-500/10 text-amber-300"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${isHard ? "bg-rose-400" : "bg-amber-400"}`} />
      <span className="font-semibold uppercase tracking-wide">[{actualSeverity}]</span>
      <span>{actualType}:</span>
      {actualMsg && <span className="text-slate-300">{actualMsg}</span>}
    </div>
  );
};
