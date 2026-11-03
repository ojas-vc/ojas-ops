import type { FC } from "react";
import type { Violation } from "@ojas-ops/sdk";

export interface ViolationBadgeProps {
  violation: Violation;
}

export const ViolationBadge: FC<ViolationBadgeProps> = ({ violation }) => {
  const isHard = violation.severity === "HARD";

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-lg px-2.5 py-1 text-xs font-medium border ${
        isHard
          ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
          : "border-amber-500/40 bg-amber-500/10 text-amber-300"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${isHard ? "bg-rose-400" : "bg-amber-400"}`}
      />
      <span className="font-semibold uppercase tracking-wide">
        [{violation.severity}]
      </span>
      <span>{violation.constraint_type}:</span>
      <span className="text-slate-300">{violation.message}</span>
    </div>
  );
};
