"use client";

import type { Resource, ScheduleSolution } from "@ojas-ops/sdk";
import { GanttChart, MetricCard } from "@ojas-ops/ui";
import { useState } from "react";

const HOSPITAL_RESOURCES: Resource[] = [
  { id: "nurse_alice", name: "Alice (ICU Specialist)" },
  { id: "nurse_bob", name: "Bob (Senior RN)" },
  { id: "nurse_carol", name: "Carol (Junior RN)" },
  { id: "nurse_david", name: "David (Nurse Practitioner)" },
];

const HOSPITAL_SOLUTION: ScheduleSolution = {
  status: "OPTIMAL",
  makespan: 24,
  objective_value: 24,
  assignments: [
    {
      task_id: "icu_triage",
      start_time: 0,
      end_time: 8,
      duration: 8,
      assigned_resources: ["nurse_alice"],
    },
    {
      task_id: "icu_night_shift",
      start_time: 8,
      end_time: 16,
      duration: 8,
      assigned_resources: ["nurse_alice"],
    },
    {
      task_id: "ward_day_shift",
      start_time: 0,
      end_time: 8,
      duration: 8,
      assigned_resources: ["nurse_bob"],
    },
    {
      task_id: "ward_evening_shift",
      start_time: 8,
      end_time: 16,
      duration: 8,
      assigned_resources: ["nurse_carol"],
    },
    {
      task_id: "trauma_oncall",
      start_time: 12,
      end_time: 20,
      duration: 8,
      assigned_resources: ["nurse_david"],
    },
  ],
  metrics: {
    wall_time: 0.025,
    objective_value: 24,
  },
};

export default function GanttPage() {
  const [timeScale, setTimeScale] = useState(20);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Gantt & Timeline Inspector
          </h1>
          <p className="text-xs text-slate-400">
            Multi-resource allocation view with timeline zoom and assignment inspection.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">Zoom Level:</span>
          <div className="flex items-center rounded-lg border border-slate-800 bg-slate-900 p-1">
            <button
              type="button"
              onClick={() => setTimeScale((prev) => Math.max(prev - 5, 10))}
              className="rounded px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              -
            </button>
            <span className="px-2 text-xs font-mono text-slate-400">{timeScale}px/u</span>
            <button
              type="button"
              onClick={() => setTimeScale((prev) => Math.min(prev + 5, 40))}
              className="rounded px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              +
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard
          label="Scenario Mode"
          value="Hospital 24h Shift"
          subValue="Nurse Rostering"
          variant="default"
        />
        <MetricCard
          label="Total Horizon"
          value="24 Hours"
          subValue="3 Rotational Shifts"
          variant="default"
        />
        <MetricCard
          label="Active Personnel"
          value="4 Nurses"
          subValue="Zero Overlap Conflicts"
          variant="success"
        />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">Roster Schedule Grid</h2>
          {selectedTask && (
            <div className="text-xs text-indigo-400">
              Inspecting task: <span className="font-mono font-semibold">{selectedTask}</span>
            </div>
          )}
        </div>

        <GanttChart
          solution={HOSPITAL_SOLUTION}
          resources={HOSPITAL_RESOURCES}
          timeScale={timeScale}
          onTaskClick={(id) => setSelectedTask(id)}
        />
      </div>
    </div>
  );
}
