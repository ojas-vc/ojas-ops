"""Schedule stability objective for disruption management and rescheduling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class ScheduleStabilityObjective(Objective):
    """Minimizes deviation from an existing baseline schedule: sum(|start - baseline_start|)."""

    def __init__(
        self,
        baseline_starts: dict[str, int],
        name: str = "ScheduleStability",
        weight: float = 1.0,
    ) -> None:
        super().__init__(name=name, weight=weight)
        self.baseline_starts = baseline_starts

    def build_expression(self, context: SolverContext) -> Any:
        abs_diff_terms = []
        for tid, base_start in self.baseline_starts.items():
            if tid in context.task_vars:
                tv = context.task_vars[tid]
                diff = context.model.new_int_var(
                    -context.horizon.end, context.horizon.end, f"diff_{tid}"
                )
                context.model.add(diff == tv.start - base_start)
                abs_diff = context.model.new_int_var(0, context.horizon.end, f"abs_diff_{tid}")
                context.model.add_abs_equality(abs_diff, diff)
                abs_diff_terms.append(abs_diff)

        return sum(abs_diff_terms) if abs_diff_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total_disp = 0
        for tid, base_start in self.baseline_starts.items():
            if tid in tasks:
                total_disp += abs(tasks[tid].start - base_start)
        return float(total_disp)
