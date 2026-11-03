import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ojas Ops Studio | Operations Research & Optimization Workbench",
  description: "Interactive solver workbench, visual Gantt timeline, and constraint optimization engine for Ojas Ops.",
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
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2.5 font-bold tracking-tight text-white">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-xs font-black text-white shadow-md shadow-indigo-600/30">
                  Ω
                </span>
                <span className="text-base font-semibold">
                  Ojas <span className="text-indigo-400">Ops</span> Studio
                </span>
              </Link>

              <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
                <Link
                  href="/"
                  className="rounded-lg px-3 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Dashboard
                </Link>
                <Link
                  href="/workbench"
                  className="rounded-lg px-3 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Solver Workbench
                </Link>
                <Link
                  href="/gantt"
                  className="rounded-lg px-3 py-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-900 transition"
                >
                  Gantt Inspector
                </Link>
              </nav>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Bolt Engine Online
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
