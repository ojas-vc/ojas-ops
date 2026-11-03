import type { FC, ReactNode } from "react";

export interface MetricCardProps {
  label: string;
  value: ReactNode;
  subValue?: ReactNode;
  trend?: "up" | "down" | "neutral";
  variant?: "default" | "success" | "warning" | "error";
}

export const MetricCard: FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  variant = "default",
}) => {
  const variantStyles = {
    default: "border-slate-800 bg-slate-900/60 text-slate-100",
    success: "border-emerald-800/60 bg-emerald-950/30 text-emerald-300",
    warning: "border-amber-800/60 bg-amber-950/30 text-amber-300",
    error: "border-rose-800/60 bg-rose-950/30 text-rose-300",
  };

  return (
    <div
      className={`rounded-xl border p-4 backdrop-blur transition-all duration-200 shadow-sm ${variantStyles[variant]}`}
    >
      <div className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</div>
      <div className="mt-1.5 text-2xl font-semibold tracking-tight">{value}</div>
      {subValue && <div className="mt-1 text-xs text-slate-400">{subValue}</div>}
    </div>
  );
};
