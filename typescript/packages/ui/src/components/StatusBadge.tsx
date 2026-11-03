import type { FC } from "react";

export interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export const StatusBadge: FC<StatusBadgeProps> = ({ status, size = "md" }) => {
  const norm = (status || "UNKNOWN").toUpperCase();

  const styles: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    OPTIMAL: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      dot: "bg-emerald-400",
    },
    FEASIBLE: {
      bg: "bg-blue-500/10",
      text: "text-blue-400",
      border: "border-blue-500/30",
      dot: "bg-blue-400",
    },
    COMPLETED: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      dot: "bg-emerald-400",
    },
    RUNNING: {
      bg: "bg-indigo-500/10",
      text: "text-indigo-400",
      border: "border-indigo-500/30",
      dot: "bg-indigo-400 animate-ping",
    },
    AWAITING_APPROVAL: {
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/30",
      dot: "bg-amber-400",
    },
    AWAITING_HUMAN_APPROVAL: {
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/30",
      dot: "bg-amber-400",
    },
    APPROVED: {
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      dot: "bg-emerald-400",
    },
    REJECTED: {
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/30",
      dot: "bg-rose-400",
    },
    INFEASIBLE: {
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/30",
      dot: "bg-rose-400",
    },
    FAILED: {
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/30",
      dot: "bg-rose-400",
    },
  };

  const style = styles[norm] || {
    bg: "bg-slate-500/10",
    text: "text-slate-400",
    border: "border-slate-500/30",
    dot: "bg-slate-400",
  };

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold tracking-wide uppercase ${style.bg} ${style.text} ${style.border} ${sizeClasses}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {norm}
    </span>
  );
};
