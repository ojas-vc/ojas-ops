"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { client } from "../../lib/api";
import type { PipelineManifestSummary, RulesetSummary } from "@ojas-ops/sdk";

export default function NewProjectWizardPage() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  const [pipelines, setPipelines] = useState<PipelineManifestSummary[]>([]);
  const [rulesets, setRulesets] = useState<RulesetSummary[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [selectedPipeline, setSelectedPipeline] = useState<string>("film-crossboarding");
  const [selectedRuleset, setSelectedRuleset] = useState<string>("sag-aftra-theatrical");
  const [projectId, setProjectId] = useState<string>(`proj-${Date.now().toString().slice(-6)}`);
  const [title, setTitle] = useState<string>("Indie Feature Shoot (October 2026)");
  const [initialJson, setInitialJson] = useState<string>(
    JSON.stringify(
      {
        dataset_dict: {
          scenes: [
            { id: "S1", name: "Int. Warehouse", duration_days: 2, cast_ids: ["A1", "A2"], location_id: "LOC1" },
            { id: "S2", name: "Ext. Pier Sunset", duration_days: 1, cast_ids: ["A1"], location_id: "LOC2" },
            { id: "S3", name: "Int. Safehouse", duration_days: 3, cast_ids: ["A2", "A3"], location_id: "LOC1" },
          ],
          cast: [
            { id: "A1", name: "Lead Detective", daily_rate: 3500 },
            { id: "A2", name: "Informant", daily_rate: 2200 },
            { id: "A3", name: "Captain", daily_rate: 1800 },
          ],
          locations: [
            { id: "LOC1", name: "Industrial Warehouse Stage", daily_rate: 5000 },
            { id: "LOC2", name: "Harbor Pier", daily_rate: 2500 },
          ],
        },
      },
      null,
      2
    )
  );
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [pipeRes, ruleRes] = await Promise.all([
          client.pipelines.list().catch(() => []),
          client.rulesets.list().catch(() => []),
        ]);
        setPipelines(pipeRes);
        setRulesets(ruleRes);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load options");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handlePipelineSelect = (name: string) => {
    setSelectedPipeline(name);
    // Auto-update sensible defaults based on pipeline
    if (name === "job-shop-flow") {
      setTitle("Machining Work Centre Run");
      setSelectedRuleset("automotive-oem");
      setInitialJson(
        JSON.stringify(
          {
            operations: [
              { id: "OP10", part_id: "Shaft-A", machine: "CNC-MILL-1", duration: 45 },
              { id: "OP20", part_id: "Shaft-A", machine: "LATHE-2", duration: 30 },
              { id: "OP30", part_id: "Shaft-B", machine: "CNC-MILL-1", duration: 60 },
            ],
            machines: [
              { id: "CNC-MILL-1", capacity: 1 },
              { id: "LATHE-2", capacity: 1 },
            ],
          },
          null,
          2
        )
      );
    } else if (name === "clinical-shift-rostering") {
      setTitle("ICU Acute Care 28-Day Roster");
      setSelectedRuleset("icu-acuity-california");
      setInitialJson(
        JSON.stringify(
          {
            census: { icu_patients: 12, telemetry_patients: 24 },
            shifts: ["DAY_0700_1900", "NIGHT_1900_0700"],
            nurses_count: 18,
          },
          null,
          2
        )
      );
    } else if (name === "muhurat-auspicious-scheduler") {
      setTitle("Feature Film Inauguration Muhurat");
      setSelectedRuleset("vedic-muhurat-standard");
      setInitialJson(
        JSON.stringify(
          {
            city: "Mumbai",
            latitude: 19.076,
            longitude: 72.8777,
            target_dates: ["2026-11-12", "2026-11-13", "2026-11-14"],
            event_type: "Film Muhurat Shot",
          },
          null,
          2
        )
      );
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    let parsedContext: Record<string, unknown> = {};
    try {
      if (initialJson.trim()) {
        parsedContext = JSON.parse(initialJson);
      }
    } catch {
      setError("Initial data must be valid JSON.");
      return;
    }

    try {
      const res = await client.projects.init({
        tenant_id: "default",
        project_id: projectId.trim(),
        title: title.trim(),
        pipeline_type: selectedPipeline,
        ruleset: selectedRuleset || undefined,
        metadata: {
          initial_inputs: parsedContext,
        },
      });

      startTransition(() => {
        router.push(`/projects/${encodeURIComponent(res.project_id)}`);
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create project workspace.");
    }
  };

  const filteredPipelines = pipelines.filter(
    (p) => categoryFilter === "all" || p.category.toLowerCase().includes(categoryFilter.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          Universal Project Generator
        </span>
        <h1 className="mt-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
          Launch New Pipeline Project
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Select an industrial operational pipeline, configure domain policies, and provide initial data.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleCreate} className="space-y-8">
        {/* Step 1: Pipeline Catalog Selection */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-white">1. Select Industrial Pipeline</h2>
              <p className="text-xs text-slate-400">
                Choose from 18 verified operational optimization state machines.
              </p>
            </div>

            <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
              {["all", "media", "manufacturing", "healthcare", "events", "cultural"].map((cat) => (
                <button
                  type="button"
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  className={`rounded-md px-2.5 py-1 capitalize transition ${
                    categoryFilter === cat
                      ? "bg-indigo-600 text-white font-medium"
                      : "bg-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-72 overflow-y-auto pr-1">
            {loading ? (
              <div className="col-span-full py-8 text-center text-xs text-slate-500">
                Loading pipeline catalog...
              </div>
            ) : (
              filteredPipelines.map((pipe) => {
                const isSelected = selectedPipeline === pipe.name;
                return (
                  <button
                    type="button"
                    key={pipe.name}
                    onClick={() => handlePipelineSelect(pipe.name)}
                    className={`text-left p-3 rounded-lg border transition ${
                      isSelected
                        ? "border-indigo-500 bg-indigo-950/40 shadow-sm shadow-indigo-500/20"
                        : "border-slate-800 bg-slate-950/40 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase">
                        {pipe.category}
                      </span>
                      {isSelected && (
                        <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
                      )}
                    </div>
                    <div className="mt-1 font-mono text-xs font-bold text-white">{pipe.name}</div>
                    <p className="mt-1 text-[11px] text-slate-400 line-clamp-2">{pipe.description}</p>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Step 2: Metadata & Policy */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h2 className="text-base font-semibold text-white">2. Project Identity & Governance Ruleset</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300">Project Identifier</label>
              <input
                type="text"
                required
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs font-mono text-white focus:border-indigo-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-500">Unique folder name on disk and DB lookup</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Project Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300">
              Operational Ruleset / Labor Agreement Policy
            </label>
            <select
              value={selectedRuleset}
              onChange={(e) => setSelectedRuleset(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="">-- No specific ruleset (Default Heuristics) --</option>
              {rulesets.map((r) => (
                <option key={r.name} value={r.name}>
                  {r.name} ({r.domain}) — {r.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Step 3: Initial Data Context */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">3. Initial Data Context (JSON)</h2>
            <span className="text-xs text-slate-500">Injected into Stage 1 Director Context</span>
          </div>

          <textarea
            rows={8}
            value={initialJson}
            onChange={(e) => setInitialJson(e.target.value)}
            className="w-full font-mono text-xs rounded-lg border border-slate-800 bg-slate-950 p-3 text-slate-200 focus:border-indigo-500 focus:outline-none"
            placeholder="Paste raw screenplay breakdown, operations list, or nurse census JSON..."
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-lg border border-slate-800 px-4 py-2.5 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-900 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isPending}
            className="rounded-lg bg-indigo-600 px-6 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 transition disabled:opacity-50"
          >
            {isPending ? "Initializing Workspace..." : "Initialize Workspace & Launch &rarr;"}
          </button>
        </div>
      </form>
    </div>
  );
}
