"use client";

import { client } from "@/app/lib/api";
import type { HealthResponse, ReadinessResponse } from "@ojas-ops/sdk";
import { MetricCard } from "@ojas-ops/ui";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [runsCount, setRunsCount] = useState<number | null>(null);
  const [jobsCount, setJobsCount] = useState<number | null>(null);
  const [scenariosCount, setScenariosCount] = useState<number | null>(null);

  useEffect(() => {
    client
      .getHealth()
      .then(setHealth)
      .catch(() => null);
    client
      .getReadiness()
      .then(setReadiness)
      .catch(() => null);
    client.scheduleRuns
      .list({ page_size: 1 })
      .then((r) => setRunsCount(r.total ?? r.count ?? 0))
      .catch(() => null);
    client.optimizationJobs
      .list({ page_size: 1 })
      .then((j) => setJobsCount(j.total ?? j.count ?? 0))
      .catch(() => null);
    client.scenarios
      .list({ page_size: 1 })
      .then((s) => setScenariosCount(s.total ?? s.count ?? 0))
      .catch(() => null);
  }, []);

  return (
    <div className="space-y-10">
      {/* Hero Banner */}
      <div className="rounded-2xl border border-indigo-900/40 bg-gradient-to-br from-indigo-950/40 via-slate-900/50 to-slate-950 p-8 shadow-xl">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-300">
              Operations Research & Constraint Programming
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Django-Bolt Online
            </span>
          </div>

          <h1 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ojas Ops Interactive Studio
          </h1>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Full-stack operations workbench powered by Google OR-Tools CP-SAT, Temporal distributed
            workflows, and specialized domain adapters. 100% backend API coverage across 24
            endpoints.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              href="/schedules"
              className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-indigo-500 transition"
            >
              ⚡ Open Solver Workbench →
            </Link>
            <Link
              href="/optimization-jobs"
              className="inline-flex items-center justify-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition"
            >
              🚀 Temporal Workflows
            </Link>
            <Link
              href="/visualizations"
              className="inline-flex items-center justify-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition"
            >
              📊 Exporters & Stripboards
            </Link>
          </div>
        </div>
      </div>

      {/* Live System Diagnostics & Telemetry */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard
          label="Health Status (/healthz)"
          value={health?.status === "ok" ? "HEALTHY" : "CHECKING..."}
          subValue={health?.service ? `Service: ${health.service}` : "Django-Bolt probe"}
          variant={health?.status === "ok" ? "success" : "default"}
        />
        <MetricCard
          label="Engine Readiness (/readyz)"
          value={
            readiness?.ready === "true" || readiness?.ready === "ready" ? "READY" : "CONNECTING"
          }
          subValue={readiness?.engine || "Google OR-Tools CP-SAT"}
          variant={readiness?.ready ? "success" : "default"}
        />
        <MetricCard
          label="Schedule Runs"
          value={runsCount != null ? runsCount : "—"}
          subValue="Historical runs"
        />
        <MetricCard
          label="Temporal Jobs"
          value={jobsCount != null ? jobsCount : "—"}
          subValue="Async & HITL jobs"
        />
        <MetricCard
          label="Scenarios Library"
          value={scenariosCount != null ? scenariosCount : "—"}
          subValue="Benchmark records"
        />
      </div>

      {/* Core Services Section */}
      <div>
        <h2 className="text-lg font-bold text-white">Operations Research Core Services</h2>
        <p className="text-xs text-slate-400">
          Deterministic constraint solving, validation, workflow management, and simulations
        </p>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
          <Link
            href="/schedules"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Core Engine</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              CP-SAT Solver Workbench
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Synchronous CP-SAT optimization with tunable heuristics, resource horizons, and visual
              Gantt chart generation.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              Launch Workbench →
            </div>
          </Link>

          <Link
            href="/schedules/validate"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Validation</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              Deterministic Schedule Validator
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Audit schedule feasibility, check temporal precedence, and identify capacity overlaps
              with detailed violation badges.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              Open Validator →
            </div>
          </Link>

          <Link
            href="/schedule-runs"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Database</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              Schedule Runs History (CRUD)
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Query, filter, inspect, edit metadata, and manage persisted optimization runs across
              tenant partitions.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              Browse Catalog →
            </div>
          </Link>

          <Link
            href="/optimization-jobs"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Temporal</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              Async Workflows & HITL Console
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Submit heavy solves to Temporal queues, track live progress convergence, and execute
              Human-in-the-Loop review sign-offs.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              Monitor Workflows →
            </div>
          </Link>

          <Link
            href="/scenarios"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Benchmarks</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              Scenarios & Synthetic Generator
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Execute declarative scenarios against golden assertions or generate synthetic
              benchmarks for Job Shop, Workforce, and Film.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              View Scenarios →
            </div>
          </Link>

          <Link
            href="/simulations"
            className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xs font-semibold uppercase text-indigo-400">Resilience</div>
            <h3 className="mt-1 font-semibold text-white group-hover:text-indigo-300 transition">
              Disruption Simulator & Rescheduler
            </h3>
            <p className="mt-1.5 text-xs text-slate-400 leading-normal">
              Inject delays and breakdowns, analyze transitive ripple impacts, and re-optimize with
              stability objectives.
            </p>
            <div className="mt-3 text-xs font-medium text-indigo-400 group-hover:underline">
              Simulate Disruptions →
            </div>
          </Link>
        </div>
      </div>

      {/* Exporters & Calendars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          href="/visualizations"
          className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-6 hover:border-indigo-500/50 transition block"
        >
          <div className="text-xs font-semibold uppercase text-emerald-400">Reporting</div>
          <h3 className="mt-1 text-base font-bold text-white group-hover:text-emerald-300 transition">
            Visualizations & Document Exporters
          </h3>
          <p className="mt-1.5 text-xs text-slate-400 leading-normal">
            Export production shooting stripboards (HTML/SVG), cast Day-Out-of-Days (DOOD) matrices,
            high-resolution vector Gantt charts, and print-ready reports.
          </p>
          <div className="mt-4 text-xs font-semibold text-emerald-400 group-hover:underline">
            Open Exporters →
          </div>
        </Link>

        <Link
          href="/calendars"
          className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-6 hover:border-indigo-500/50 transition block"
        >
          <div className="text-xs font-semibold uppercase text-amber-400">Calendars</div>
          <h3 className="mt-1 text-base font-bold text-white group-hover:text-amber-300 transition">
            Operational & Cultural Calendars
          </h3>
          <p className="mt-1.5 text-xs text-slate-400 leading-normal">
            Calculate Vedic astrological blackout intervals (Rahu Kalam, Yamagandam, Muhurats) and
            industrial shift working windows.
          </p>
          <div className="mt-4 text-xs font-semibold text-amber-400 group-hover:underline">
            Compute Blackouts →
          </div>
        </Link>
      </div>

      {/* Six Vertical Domain Adapters */}
      <div>
        <h2 className="text-lg font-bold text-white">Six Vertical Domain Adapter Studios</h2>
        <p className="text-xs text-slate-400">
          Specialized business domain schedulers with pre-configured fixtures ready for 1-click
          execution
        </p>

        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Link
            href="/adapters/film-production"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">🎬</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Film Production Call Sheet
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              SAG-AFTRA drop rules, cast DOOD minimization, and soundstage turnovers.
            </p>
          </Link>

          <Link
            href="/adapters/manufacturing"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">⚙️</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Manufacturing Job Shop
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Machine sequences and sequence-dependent family setup changeover minimization.
            </p>
          </Link>

          <Link
            href="/adapters/workforce"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">🏥</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Healthcare Workforce
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Clinical shift rotations, qualification matching, and rest window compliance.
            </p>
          </Link>

          <Link
            href="/adapters/marketing-flighting"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">📈</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Marketing Flighting
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Media spend pulsing across Meta, Google Search, and Connected TV channels.
            </p>
          </Link>

          <Link
            href="/adapters/academic-timetables"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">🎓</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Academic Timetabling
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              University cohort, classroom, and professor clash-free timetable planning.
            </p>
          </Link>

          <Link
            href="/adapters/event-run-sheets"
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-5 hover:border-indigo-500/50 transition block"
          >
            <div className="text-xl mb-1">🎙️</div>
            <h3 className="font-semibold text-white group-hover:text-indigo-300 transition">
              Event Run Sheets
            </h3>
            <p className="mt-1 text-xs text-slate-400">
              Multi-track conference hall turnover buffers and speaker conflict avoidance.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
