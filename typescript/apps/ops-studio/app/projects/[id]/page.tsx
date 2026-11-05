"use client";

import { useEffect, useState, useTransition } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { client } from "../../lib/api";
import type {
  PipelineEventItem,
  PipelineManifest,
  ProjectCheckpointRecord,
  ProjectWorkspaceRecord,
} from "@ojas-ops/sdk";
import { JsonViewer, StatusBadge } from "@ojas-ops/ui";

export default function ProjectWorkspaceDetailsPage() {
  const params = useParams();
  const projectId = (params?.id as string) || "";
  const [isPending] = useTransition();

  const [project, setProject] = useState<ProjectWorkspaceRecord | null>(null);
  const [manifest, setManifest] = useState<PipelineManifest | null>(null);
  const [completedStages, setCompletedStages] = useState<string[]>([]);
  const [activeCheckpoint, setActiveCheckpoint] = useState<ProjectCheckpointRecord | null>(null);
  const [events, setEvents] = useState<PipelineEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStage, setSelectedStage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const refreshProjectData = async () => {
    try {
      const [projList, compRes, evtsRes] = await Promise.all([
        client.projects.list("default").catch(() => ({ results: [] })),
        client.projects.getCompletedStages(projectId, "default").catch(() => ({
          project_id: projectId,
          completed_stages: [],
        })),
        client.projects.getEvents(projectId, "default").catch(() => []),
      ]);

      const found = projList.results.find((p) => p.project_id === projectId);
      if (found) {
        setProject(found);
        const pType = found.pipeline_type || "film-crossboarding";
        const m = await client.pipelines.get(pType).catch(() => null);
        if (m) setManifest(m);
      }
      setCompletedStages(compRes.completed_stages || []);
      setEvents(evtsRes || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load project details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProjectData();
    const interval = setInterval(() => {
      client.projects
        .getEvents(projectId, "default")
        .then((evts) => setEvents(evts || []))
        .catch(() => {});
    }, 4000);
    return () => clearInterval(interval);
  }, [projectId]);

  // Determine current active stage
  const stages = manifest?.stages || [];
  const currentStageIndex = stages.findIndex((s) => !completedStages.includes(s.name));
  const currentStage = currentStageIndex >= 0 ? stages[currentStageIndex] : null;
  const isAwaitingGate =
    project?.status?.includes("AWAITING") || project?.status?.includes("GATE");

  // Load selected stage checkpoint
  useEffect(() => {
    const stageToInspect = selectedStage || currentStage?.name || stages[0]?.name;
    if (stageToInspect && projectId) {
      client.projects
        .getCheckpoint(projectId, stageToInspect, "default")
        .then((cp) => setActiveCheckpoint(cp))
        .catch(() => setActiveCheckpoint(null));
    }
  }, [selectedStage, currentStage, projectId, stages]);

  const handleRunCurrentStage = async () => {
    if (!currentStage) return;
    setStatusMessage(`Executing stage '${currentStage.name}'...`);
    setError(null);
    try {
      const res = await client.projects.runStage(projectId, currentStage.name, {
        tenant_id: "default",
        inputs: project?.metadata?.initial_inputs as Record<string, unknown> | undefined,
      });
      setStatusMessage(`Stage '${res.stage}' returned: ${res.status}`);
      await refreshProjectData();
      if (res.checkpoint) {
        setActiveCheckpoint(res.checkpoint);
        setSelectedStage(res.stage);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Stage execution failed.");
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-sm text-slate-400">
        Loading project workspace & state machine...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Workspace Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <Link href="/projects" className="text-xs text-slate-500 hover:text-slate-400">
              &larr; Projects
            </Link>
            <span className="text-slate-600">/</span>
            <span className="font-mono text-xs text-indigo-400">{projectId}</span>
            <StatusBadge status={project?.status || "IN_PROGRESS"} />
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-white sm:text-3xl">
            {project?.title || projectId}
          </h1>
          <div className="mt-1 flex items-center gap-4 text-xs text-slate-400">
            <span>
              Pipeline: <span className="font-mono text-indigo-300">{project?.pipeline_type}</span>
            </span>
            <span>
              Ruleset: <span className="font-mono text-slate-300">{project?.ruleset || "Default"}</span>
            </span>
            <span>Tenant: default</span>
          </div>
        </div>

        {/* Header Action Links */}
        <div className="flex items-center gap-2">
          <Link
            href={`/projects/${encodeURIComponent(projectId)}/simulations`}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            What-If Simulations &rarr;
          </Link>
          <Link
            href={`/projects/${encodeURIComponent(projectId)}/exports`}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 transition"
          >
            Exports Center &rarr;
          </Link>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}
      {statusMessage && (
        <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-3 text-xs text-indigo-300">
          {statusMessage}
        </div>
      )}

      {/* HITL Gate Banner if Awaiting Approval */}
      {isAwaitingGate && currentStage && (
        <div className="flex items-center justify-between rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 text-amber-300">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider">
              Human-in-the-Loop Sign-Off Required
            </div>
            <div className="mt-0.5 text-sm font-medium">
              Stage &apos;{currentStage.name}&apos; generated operational schedule. Feasibility verified.
            </div>
          </div>
          <Link
            href={`/projects/${encodeURIComponent(projectId)}/gates/${encodeURIComponent(currentStage.name)}`}
            className="rounded-lg bg-amber-500 px-4 py-2 text-xs font-bold text-slate-950 shadow-md hover:bg-amber-400 transition"
          >
            Open Tradeoff Console &rarr;
          </Link>
        </div>
      )}

      {/* Stage Stepper */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Pipeline Execution Stepper</h2>
          {currentStage && (
            <button
              onClick={handleRunCurrentStage}
              disabled={isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition disabled:opacity-50"
            >
              Run Stage: {currentStage.name} &rarr;
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {stages.map((stage, idx) => {
            const isCompleted = completedStages.includes(stage.name);
            const isCurrent = currentStage?.name === stage.name;
            const isSelected = (selectedStage || currentStage?.name) === stage.name;

            return (
              <button
                type="button"
                key={stage.name}
                onClick={() => setSelectedStage(stage.name)}
                className={`text-left p-3 rounded-lg border transition ${
                  isSelected
                    ? "border-indigo-500 bg-indigo-950/40 shadow-sm"
                    : isCompleted
                    ? "border-emerald-500/30 bg-emerald-950/20"
                    : isCurrent
                    ? "border-amber-500/40 bg-amber-950/20"
                    : "border-slate-800 bg-slate-950/40"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-slate-500">
                  <span>Stage {idx + 1}</span>
                  {isCompleted ? (
                    <span className="text-emerald-400 font-bold">✓</span>
                  ) : isCurrent ? (
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse" />
                  ) : null}
                </div>
                <div className="mt-1 font-mono text-xs font-bold text-white truncate">
                  {stage.name}
                </div>
                <div className="mt-1 text-[10px] text-slate-400 capitalize">
                  {isCompleted ? "Completed" : isCurrent ? "Active" : "Pending"}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Dual Column: Artifact Inspector & Live Log Terminal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Artifact Inspector */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">
              Artifact Inspector: <span className="font-mono text-indigo-400">{selectedStage || currentStage?.name}</span>
            </h2>
            {activeCheckpoint?.human_approval_required && (
              <span className="rounded bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold text-amber-400 border border-amber-500/20">
                Gated Stage
              </span>
            )}
          </div>

          {activeCheckpoint ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                <div className="rounded bg-slate-950 p-2">
                  <div className="text-[10px] text-slate-500">Status</div>
                  <div className="text-white capitalize">{activeCheckpoint.status}</div>
                </div>
                <div className="rounded bg-slate-950 p-2">
                  <div className="text-[10px] text-slate-500">Approved</div>
                  <div className="text-white">{activeCheckpoint.human_approved ? "Yes" : "No"}</div>
                </div>
                <div className="rounded bg-slate-950 p-2">
                  <div className="text-[10px] text-slate-500">Artifacts</div>
                  <div className="text-white">{Object.keys(activeCheckpoint.artifacts || {}).length} files</div>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 max-h-96 overflow-y-auto">
                <JsonViewer data={activeCheckpoint} />
              </div>
            </div>
          ) : (
            <div className="py-16 text-center text-xs text-slate-500">
              No checkpoint recorded for this stage yet. Click &apos;Run Stage&apos; to execute.
            </div>
          )}
        </div>

        {/* Live SSE Event Log Console */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-white">Live Execution Event Stream</h2>
            <div className="flex items-center gap-1.5 text-xs text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Live Bus
            </div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 font-mono text-xs max-h-96 overflow-y-auto space-y-2">
            {events.length === 0 ? (
              <div className="py-12 text-center text-slate-500">Awaiting stage execution events...</div>
            ) : (
              events.map((evt) => (
                <div key={evt.id} className="border-b border-slate-900 pb-1.5">
                  <div className="flex items-center justify-between text-[10px] text-slate-500">
                    <span className="text-indigo-400 font-semibold">{evt.type}</span>
                    <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="text-slate-300 text-xs mt-0.5">{evt.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
