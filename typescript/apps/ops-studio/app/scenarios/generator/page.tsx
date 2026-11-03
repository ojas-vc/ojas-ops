"use client";

import { client } from "@/app/lib/api";
import type { GeneratedScenarioSummary } from "@ojas-ops/sdk";
import { JsonViewer, MetricCard } from "@ojas-ops/ui";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function ScenarioGeneratorPage() {
  const router = useRouter();
  const [domain, setDomain] = useState<"jobshop" | "workforce" | "film">("jobshop");

  // Job shop parameters
  const [numJobs, setNumJobs] = useState(6);
  const [numMachines, setNumMachines] = useState(4);

  // Workforce parameters
  const [numStaff, setNumStaff] = useState(12);
  const [numShifts, setNumShifts] = useState(18);

  // Film parameters
  const [numScenes, setNumScenes] = useState(15);
  const [numCast, setNumCast] = useState(8);
  const [numLocations, setNumLocations] = useState(3);

  const [seed, setSeed] = useState(42);

  // State
  const [generating, setGenerating] = useState(false);
  const [summary, setSummary] = useState<GeneratedScenarioSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setSaveSuccess(false);
    try {
      const payload: Record<string, unknown> = {
        scenario_type: domain,
        seed: Number(seed),
      };

      if (domain === "jobshop") {
        payload.num_jobs = Number(numJobs);
        payload.num_machines = Number(numMachines);
      } else if (domain === "workforce") {
        payload.num_staff = Number(numStaff);
        payload.num_shifts = Number(numShifts);
      } else if (domain === "film") {
        payload.num_scenes = Number(numScenes);
        payload.num_cast = Number(numCast);
        payload.num_locations = Number(numLocations);
      }

      const res = await client.scenarios.generate(
        payload as unknown as import("@ojas-ops/sdk").GenerateScenarioRequest,
      );
      setSummary(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveToLibrary = async () => {
    if (!summary) return;
    setSaving(true);
    try {
      await client.scenarios.create({
        tenant_id: "org_default",
        name: `Synthetic_${domain.toUpperCase()}_Seed${seed}`,
        domain,
        scale: "medium",
        definition_json: summary as unknown as Record<string, unknown>,
      });
      setSaveSuccess(true);
      setTimeout(() => {
        router.push("/scenarios");
      }, 1200);
    } catch (err) {
      alert(`Save failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <Link
            href="/scenarios"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Back to Scenarios Catalog
          </Link>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">
            Synthetic Scenario Generator Studio
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Generate synthetic benchmarks and test instances across Manufacturing, Healthcare, and
            Film Production.
          </p>
        </div>

        <button
          type="button"
          disabled={generating}
          onClick={handleGenerate}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-indigo-500 disabled:opacity-50 transition"
        >
          {generating ? "Generating..." : "⚡ Generate Synthetic Instance"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <div className="font-semibold">Generation Failed</div>
          <div>{error}</div>
        </div>
      )}

      {saveSuccess && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
          ✓ Scenario saved to library successfully! Redirecting to catalog...
        </div>
      )}

      {/* Domain Selection Tabs */}
      <div className="flex gap-3 border-b border-slate-800 pb-3">
        <button
          type="button"
          onClick={() => setDomain("jobshop")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            domain === "jobshop"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          Manufacturing Job Shop
        </button>
        <button
          type="button"
          onClick={() => setDomain("workforce")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            domain === "workforce"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          Healthcare Workforce
        </button>
        <button
          type="button"
          onClick={() => setDomain("film")}
          className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
            domain === "film"
              ? "bg-indigo-600 text-white"
              : "bg-slate-900 text-slate-400 hover:text-white"
          }`}
        >
          Film Shoot Call Sheet
        </button>
      </div>

      {/* Parameter Sliders Box */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-6">
        <h3 className="text-sm font-semibold text-white">Generator Parameters</h3>

        {domain === "jobshop" && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Number of Jobs</label>
                <span className="font-mono text-indigo-400">{numJobs}</span>
              </div>
              <input
                type="range"
                min={2}
                max={30}
                value={numJobs}
                onChange={(e) => setNumJobs(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Number of Machines</label>
                <span className="font-mono text-indigo-400">{numMachines}</span>
              </div>
              <input
                type="range"
                min={2}
                max={15}
                value={numMachines}
                onChange={(e) => setNumMachines(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Random Seed</label>
                <span className="font-mono text-indigo-400">{seed}</span>
              </div>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-200"
              />
            </div>
          </div>
        )}

        {domain === "workforce" && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Staff Members</label>
                <span className="font-mono text-indigo-400">{numStaff}</span>
              </div>
              <input
                type="range"
                min={4}
                max={50}
                value={numStaff}
                onChange={(e) => setNumStaff(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Shift Slots</label>
                <span className="font-mono text-indigo-400">{numShifts}</span>
              </div>
              <input
                type="range"
                min={6}
                max={40}
                value={numShifts}
                onChange={(e) => setNumShifts(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Random Seed</label>
                <span className="font-mono text-indigo-400">{seed}</span>
              </div>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-200"
              />
            </div>
          </div>
        )}

        {domain === "film" && (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Scenes Count</label>
                <span className="font-mono text-indigo-400">{numScenes}</span>
              </div>
              <input
                type="range"
                min={5}
                max={40}
                value={numScenes}
                onChange={(e) => setNumScenes(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Cast Members</label>
                <span className="font-mono text-indigo-400">{numCast}</span>
              </div>
              <input
                type="range"
                min={3}
                max={20}
                value={numCast}
                onChange={(e) => setNumCast(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Locations</label>
                <span className="font-mono text-indigo-400">{numLocations}</span>
              </div>
              <input
                type="range"
                min={1}
                max={8}
                value={numLocations}
                onChange={(e) => setNumLocations(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-slate-300 font-medium">Random Seed</label>
                <span className="font-mono text-indigo-400">{seed}</span>
              </div>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-200"
              />
            </div>
          </div>
        )}
      </div>

      {/* Output Summary & 1-Click Save */}
      {summary && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 flex-1">
              <MetricCard
                label="Generated Domain"
                value={summary.scenario_type.toUpperCase()}
                subValue="Specification type"
              />
              <MetricCard
                label="Tasks Count"
                value={summary.tasks_count}
                subValue="Operations generated"
              />
              <MetricCard
                label="Resources Count"
                value={summary.resources_count}
                subValue="Machines / Staff / Stages"
              />
              <MetricCard label="Random Seed" value={seed} subValue="Deterministic seed" />
            </div>
            <button
              type="button"
              disabled={saving}
              onClick={handleSaveToLibrary}
              className="rounded-xl bg-emerald-600 px-6 py-3 text-xs font-bold text-white shadow-lg hover:bg-emerald-500 disabled:opacity-50 transition"
            >
              {saving ? "Saving..." : "💾 Save to Scenario Library"}
            </button>
          </div>

          <JsonViewer title="Generated Scenario Payload" data={summary} initialExpanded={true} />
        </div>
      )}
    </div>
  );
}
