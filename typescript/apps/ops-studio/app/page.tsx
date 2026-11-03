import Link from "next/link";
import { MetricCard } from "@ojas-ops/ui";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="rounded-2xl border border-indigo-900/40 bg-gradient-to-br from-indigo-950/40 via-slate-900/50 to-slate-950 p-8 shadow-xl">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-1.5 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-300">
            Operations Research & Optimization Engine
          </span>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ojas Ops Interactive Studio
          </h1>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Constraint Programming (CP-SAT), Mixed-Integer Linear Programming, and real-time scheduling
            benchmarks across production domains including Film Shooting, Nurse Rostering, and Job Shop Manufacturing.
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              href="/workbench"
              className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
            >
              Open Solver Workbench →
            </Link>
            <Link
              href="/gantt"
              className="inline-flex items-center justify-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-semibold text-slate-200 hover:bg-slate-800 transition"
            >
              View Sample Gantt
            </Link>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Active Solvers"
          value="CP-SAT & MIP"
          subValue="Google OR-Tools 9.15"
          variant="default"
        />
        <MetricCard
          label="Domain Adapters"
          value="6 Built-in"
          subValue="Film, Medical, Manufacturing, etc."
          variant="default"
        />
        <MetricCard
          label="Temporal Workflows"
          value="Available"
          subValue="Async & Human-in-the-Loop"
          variant="success"
        />
        <MetricCard
          label="Bolt Engine Status"
          value="100% Ready"
          subValue="Port 8000 (0ms latency)"
          variant="success"
        />
      </div>

      {/* Domain Quick Launch Cards */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200">Domain Scenario Quick Launch</h2>
        <p className="text-xs text-slate-400">Pre-configured golden scenarios ready for solver execution</p>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition">
            <div className="text-xs font-semibold uppercase text-indigo-400">Entertainment</div>
            <h3 className="mt-1 font-semibold text-white">Film Production Call Sheet</h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Cast availability, SAG-AFTRA 10-day drop-and-pickup, minor labor rules, and golden hour scheduling.
            </p>
            <div className="mt-4">
              <Link
                href="/workbench?domain=film_production"
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300"
              >
                Launch in Workbench →
              </Link>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition">
            <div className="text-xs font-semibold uppercase text-indigo-400">Healthcare</div>
            <h3 className="mt-1 font-semibold text-white">Nurse & Workforce Rostering</h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Hospital shift rotations, consecutive day limits, minimum rest windows, and skill balancing.
            </p>
            <div className="mt-4">
              <Link
                href="/workbench?domain=nurse_rostering"
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300"
              >
                Launch in Workbench →
              </Link>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition">
            <div className="text-xs font-semibold uppercase text-indigo-400">Industry</div>
            <h3 className="mt-1 font-semibold text-white">Job Shop Manufacturing</h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Machine precedence, cumulative capacity constraints, tool changeover transition matrices.
            </p>
            <div className="mt-4">
              <Link
                href="/workbench?domain=manufacturing"
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300"
              >
                Launch in Workbench →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
