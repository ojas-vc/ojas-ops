"""Schedule stability and disruption impact metrics."""

from __future__ import annotations

import msgspec

from ojas_ops.models.schedule import ScheduleResult


class ScheduleStabilityMetrics(msgspec.Struct, kw_only=True):
    """Quantitative comparison between an approved baseline schedule and a revised schedule."""

    tasks_moved_count: int = 0
    total_tasks_count: int = 0
    preserved_ratio: float = 1.0
    total_displacement: int = 0
    max_displacement: int = 0
    makespan_delta: int = 0
    cost_delta: float = 0.0
    displaced_tasks: list[str] = msgspec.field(default_factory=list)


def calculate_stability_metrics(
    baseline: ScheduleResult,
    rescheduled: ScheduleResult,
) -> ScheduleStabilityMetrics:
    """Compute mathematical metrics measuring deviation from the baseline schedule."""
    if not baseline.is_feasible or not rescheduled.is_feasible:
        return ScheduleStabilityMetrics()

    total_tasks = len(baseline.tasks)
    if total_tasks == 0:
        return ScheduleStabilityMetrics()

    moved_tasks: list[str] = []
    total_disp = 0
    max_disp = 0

    for tid, b_task in baseline.tasks.items():
        r_task = rescheduled.tasks.get(tid)
        if not r_task:
            moved_tasks.append(tid)
            continue

        disp = abs(r_task.start - b_task.start)
        if disp > 0:
            moved_tasks.append(tid)
            total_disp += disp
            max_disp = max(max_disp, disp)

    preserved_count = total_tasks - len(moved_tasks)
    preserved_ratio = float(preserved_count / total_tasks)
    makespan_delta = rescheduled.makespan - baseline.makespan
    cost_delta = rescheduled.objective_value - baseline.objective_value

    return ScheduleStabilityMetrics(
        tasks_moved_count=len(moved_tasks),
        total_tasks_count=total_tasks,
        preserved_ratio=preserved_ratio,
        total_displacement=total_disp,
        max_displacement=max_disp,
        makespan_delta=makespan_delta,
        cost_delta=cost_delta,
        displaced_tasks=moved_tasks,
    )

