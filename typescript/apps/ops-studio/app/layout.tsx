import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ojas Ops Studio | Operations Research & Optimization Workbench",
  description:
    "Interactive solver workbench, visual Gantt timeline, and constraint optimization engine for Ojas Ops.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
          <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-6">
              <Link
                href="/"
                className="flex items-center gap-2 font-bold tracking-tight text-white"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-xs font-black text-white shadow-md shadow-indigo-600/30">
                  Ω
                </span>
                <span className="text-base font-semibold">
                  Ojas <span className="text-indigo-400">Ops</span>
                </span>
              </Link>

              <nav className="hidden xl:flex items-center gap-1 text-xs font-medium">
                <Link
                  href="/"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Dashboard
                </Link>
                <Link
                  href="/schedules"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Solver
                </Link>
                <Link
                  href="/schedule-runs"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Runs
                </Link>
                <Link
                  href="/optimization-jobs"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Workflows
                </Link>
                <Link
                  href="/scenarios"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Scenarios
                </Link>
                <Link
                  href="/simulations"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Simulations
                </Link>
                <Link
                  href="/visualizations"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Visuals
                </Link>
                <Link
                  href="/calendars"
                  className="rounded-lg px-2.5 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Calendars
                </Link>
              </nav>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-xs text-slate-300">
                <span className="text-[10px] uppercase font-semibold text-indigo-400">
                  Domain Adapters:
                </span>
                <Link
                  href="/adapters/film-production"
                  className="hover:text-white"
                  title="Film Production"
                >
                  🎬
                </Link>
                <Link
                  href="/adapters/manufacturing"
                  className="hover:text-white"
                  title="Manufacturing"
                >
                  ⚙️
                </Link>
                <Link href="/adapters/workforce" className="hover:text-white" title="Workforce">
                  🏥
                </Link>
                <Link
                  href="/adapters/marketing-flighting"
                  className="hover:text-white"
                  title="Marketing"
                >
                  📈
                </Link>
                <Link
                  href="/adapters/academic-timetables"
                  className="hover:text-white"
                  title="Academic"
                >
                  🎓
                </Link>
                <Link href="/adapters/event-run-sheets" className="hover:text-white" title="Events">
                  🎙️
                </Link>
              </div>

              <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Bolt 8000
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
      </body>
    </html>
  );
}
