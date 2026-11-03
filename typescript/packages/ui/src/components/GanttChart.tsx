import type { Resource, ScheduleSolution, ScheduledTask } from "@ojas-ops/sdk";
import type { FC } from "react";

export interface GanttTaskItem {
  id: string;
  name: string;
  start: number;
  end: number;
  resource?: string;
}

export interface GanttChartProps {
  solution?: ScheduleSolution;
  tasks?: GanttTaskItem[];
  horizonStart?: number;
  horizonEnd?: number;
  resources?: Resource[];
  timeScale?: number; // pixels per time unit
  onTaskClick?: (taskId: string) => void;
}

export const GanttChart: FC<GanttChartProps> = ({
  solution,
  tasks,
  horizonStart = 0,
  horizonEnd,
  resources = [],
  timeScale = 15,
  onTaskClick,
}) => {
  // Normalize tasks into assignments list
  const assignments: ScheduledTask[] =
    solution?.assignments && solution.assignments.length > 0
      ? solution.assignments
      : tasks && tasks.length > 0
        ? tasks.map((t) => ({
            task_id: t.id,
            start_time: t.start,
            end_time: t.end,
            duration: Math.max(t.end - t.start, 1),
            assigned_resources: t.resource ? [t.resource] : ["R1"],
          }))
        : [];

  if (assignments.length === 0) {
    return (
      <div className="flex h-48 w-full items-center justify-center rounded-xl border border-dashed border-slate-800 bg-slate-900/40 text-sm text-slate-500">
        No schedule assignments available
      </div>
    );
  }

  const maxTime = Math.max(
    solution?.makespan || 0,
    horizonEnd || 0,
    ...assignments.map((a) => a.end_time),
    20,
  );

  // Group assignments by primary resource or unassigned lane
  const resourceLanes = new Map<string, ScheduledTask[]>();
  for (const res of resources) {
    resourceLanes.set(res.id, []);
  }

  for (const assign of assignments) {
    const primaryRes = assign.assigned_resources[0] || "unassigned";
    if (!resourceLanes.has(primaryRes)) {
      resourceLanes.set(primaryRes, []);
    }
    resourceLanes.get(primaryRes)!.push(assign);
  }

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4">
      {/* Time Header Ruler */}
      <div className="flex border-b border-slate-800 pb-2 pl-40 text-xs font-mono text-slate-500">
        {Array.from({ length: Math.ceil((maxTime - horizonStart) / 5) + 1 }).map((_, i) => {
          const t = horizonStart + i * 5;
          return (
            <div
              key={`tick-${t}`}
              style={{ width: `${5 * timeScale}px` }}
              className="border-l border-slate-800 pl-1"
            >
              T+{t}
            </div>
          );
        })}
      </div>

      {/* Lanes */}
      <div className="mt-2 space-y-2">
        {Array.from(resourceLanes.entries()).map(([resId, laneTasks]) => {
          const resObj = resources.find((r) => r.id === resId);
          const laneLabel = resObj ? resObj.name : resId;

          return (
            <div key={`lane-${resId}`} className="flex items-center group">
              <div className="w-40 shrink-0 truncate pr-4 text-xs font-medium text-slate-300">
                {laneLabel}
              </div>
              <div
                className="relative h-9 flex-1 rounded-lg bg-slate-900/60 border border-slate-800/80"
                style={{ width: `${maxTime * timeScale}px` }}
              >
                {laneTasks.map((task) => {
                  const left = task.start_time * timeScale;
                  const width = Math.max(task.duration * timeScale, 24);

                  return (
                    <button
                      type="button"
                      key={`task-${task.task_id}`}
                      onClick={() => onTaskClick?.(task.task_id)}
                      style={{ left: `${left}px`, width: `${width}px` }}
                      className="absolute top-1 bottom-1 truncate rounded-md bg-indigo-600/80 hover:bg-indigo-500 border border-indigo-400/40 px-2 text-left text-xs font-medium text-white shadow-sm transition"
                      title={`${task.task_id}: [${task.start_time} - ${task.end_time}] (${task.duration}u)`}
                    >
                      {task.task_id}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
