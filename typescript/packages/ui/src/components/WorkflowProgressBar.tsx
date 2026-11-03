import type { FC } from "react";

export interface WorkflowProgressBarProps {
  progressBasisPoints?: number; // 0 to 10,000 (100.00%)
  basisPoints?: number;
  incumbentObjective?: number | null;
  bestBound?: number | null;
  status?: string;
}

export const WorkflowProgressBar: FC<WorkflowProgressBarProps> = ({
  progressBasisPoints,
  basisPoints,
  incumbentObjective,
  bestBound,
  status = "RUNNING",
}) => {
  const activeBasisPoints = basisPoints ?? progressBasisPoints ?? 0;
  const percent = Math.min(Math.max(activeBasisPoints / 100, 0), 100);

  const gap =
    incumbentObjective !== undefined &&
    incumbentObjective !== null &&
    bestBound !== undefined &&
    bestBound !== null &&
    incumbentObjective > 0
      ? (((incumbentObjective - bestBound) / incumbentObjective) * 100).toFixed(2)
      : null;

  return (
    <div className="w-full space-y-2 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-200">Solve Progress</span>
          <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-[10px] font-mono font-medium text-indigo-300">
            {percent.toFixed(1)}%
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
          {incumbentObjective !== undefined && incumbentObjective !== null && (
            <span>
              Incumbent: <strong className="text-emerald-400">{incumbentObjective}</strong>
            </span>
          )}
          {bestBound !== undefined && bestBound !== null && (
            <span>
              Bound: <strong className="text-blue-400">{bestBound}</strong>
            </span>
          )}
          {gap !== null && (
            <span>
              Gap: <strong className="text-amber-400">{gap}%</strong>
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar Track */}
      <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full transition-all duration-500 ${
            status === "COMPLETED" || status === "APPROVED"
              ? "bg-emerald-500"
              : status === "FAILED" || status === "REJECTED"
                ? "bg-rose-500"
                : "bg-indigo-500 animate-pulse"
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};
