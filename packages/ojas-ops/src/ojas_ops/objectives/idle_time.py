"""Resource idle time minimization objective."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MinimizeIdleTimeObjective(Objective):
    """Minimizes idle / dead time between tasks on specified resources."""

    def __init__(
        self,
        resource_ids: list[str] | None = None,
        name: str = "MinimizeIdleTime",
        weight: float = 1.0,
    ) -> None:
        super().__init__(name=name, weight=weight)
        self.resource_ids = resource_ids

    def build_expression(self, context: SolverContext) -> Any:
        target_rids = self.resource_ids or list(context.resources.keys())
        span_terms = []

        for rid in target_rids:
            relevant_tvs = [
                context.task_vars[tid]
                for tid, task in context.tasks.items()
                if rid in task.required_resources and tid in context.task_vars
            ]
            if len(relevant_tvs) > 1:
                res_max = context.model.new_int_var(0, context.horizon.end, f"res_max_{rid}")
                res_min = context.model.new_int_var(0, context.horizon.end, f"res_min_{rid}")
                for tv in relevant_tvs:
                    context.model.add(res_max >= tv.end)
                    context.model.add(res_min <= tv.start)
                span_terms.append(res_max - res_min)

        return sum(span_terms) if span_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total_idle = 0
        target_rids = self.resource_ids or list(resources.keys())
        for rid in target_rids:
            assignment = resources.get(rid)
            if assignment:
                total_idle += assignment.idle_time
        return float(total_idle)

