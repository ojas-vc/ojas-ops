"""Tardiness / deadline lateness minimization objective."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MinimizeTardinessObjective(Objective):
    """Minimizes total tardiness: sum(max(0, task.end - deadline))."""

    def __init__(
        self,
        deadlines: dict[str, int] | None = None,
        name: str = "MinimizeTardiness",
        weight: float = 1.0,
        is_maximize: bool = False,
    ) -> None:
        super().__init__(name=name, weight=weight, is_maximize=is_maximize)
        self.deadlines = deadlines or {}

    def build_expression(self, context: SolverContext) -> Any:
        lateness_terms = []
        for tid, tv in context.task_vars.items():
            task = context.tasks.get(tid)
            # Deadline can come from objective config or task time_window
            deadline = self.deadlines.get(tid)
            if deadline is None and task and task.time_window and task.time_window.deadline:
                deadline = task.time_window.deadline

            if deadline is not None:
                lateness = context.model.new_int_var(0, context.horizon.end, f"late_{tid}")
                context.model.add(lateness >= tv.end - deadline)
                lateness_terms.append(lateness)

        return sum(lateness_terms) if lateness_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total_lateness = 0
        for tid, task in tasks.items():
            deadline = self.deadlines.get(tid)
            if deadline is not None and task.end > deadline:
                total_lateness += task.end - deadline
        return float(total_lateness)
