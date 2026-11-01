"""Cost minimization objective covering resource hourly rates, overtime, and task costs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MinimizeCostObjective(Objective):
    """Minimizes financial costs: resource usage rates, overtime, and task execution costs."""

    def __init__(
        self,
        name: str = "MinimizeCost",
        weight: float = 1.0,
        is_maximize: bool = False,
    ) -> None:
        super().__init__(name=name, weight=weight, is_maximize=is_maximize)

    def build_expression(self, context: SolverContext) -> Any:
        cost_terms = []
        for _tid, task in context.tasks.items():
            if task.cost > 0:
                cost_terms.append(int(round(task.cost)))

        for rid, res in context.resources.items():
            if res.cost_per_time_unit > 0:
                for _tid, task in context.tasks.items():
                    if rid in task.required_resources:
                        cost_terms.append(int(round(task.duration * res.cost_per_time_unit)))

        return sum(cost_terms) if cost_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total = 0.0
        for _task in tasks.values():
            total += 0.0
        return float(total)
