"""Cost minimization objective covering resource hourly rates, overtime, and task costs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ojas_ops.objectives.base import Objective

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

if TYPE_CHECKING:
    from ortools.sat.python import cp_model

    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MinimizeCostObjective(Objective):
    """Minimizes financial costs: resource usage rates, overtime, and task execution costs."""

    def __init__(
        self,
        name: str = "MinimizeCost",
        weight: float = 1.0,
        is_maximize: bool = False,
        resource_rates: dict[str, float] | None = None,
        task_costs: dict[str, float] | None = None,
    ) -> None:
        super().__init__(name=name, weight=weight, is_maximize=is_maximize)
        self._resource_rates = dict(resource_rates or {})
        self._task_costs = dict(task_costs or {})

    def build_expression(self, context: SolverContext) -> cp_model.LinearExpr | int:
        for rid, res in context.resources.items():
            if rid not in self._resource_rates:
                self._resource_rates[rid] = res.cost_per_time_unit
        for tid, task in context.tasks.items():
            if tid not in self._task_costs:
                self._task_costs[tid] = task.cost

        cost_terms: list[cp_model.LinearExpr | int] = []
        for _tid, task in context.tasks.items():
            if task.cost > 0:
                cost_terms.append(int(round(task.cost)))

        for tid, task in context.tasks.items():
            tv = context.task_vars.get(tid)
            if not tv:
                continue
            for rid, res in context.resources.items():
                if res.cost_per_time_unit <= 0:
                    continue
                unit_cost = int(round(task.duration * res.cost_per_time_unit))
                if rid in tv.resource_intervals:
                    _, pres = tv.resource_intervals[rid]
                    cost_terms.append(pres * unit_cost)
                elif rid in task.required_resources:
                    cost_terms.append(unit_cost)

        return sum(cost_terms) if cost_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total = 0.0
        for tid, st in tasks.items():
            cost_val = self._task_costs.get(tid, 0.0)
            if cost_val == 0.0 and "cost" in st.metadata:
                try:
                    cost_val = float(st.metadata["cost"])
                except ValueError:
                    pass
            total += cost_val

        for rid, ra in resources.items():
            rate = self._resource_rates.get(rid, 0.0)
            total += ra.total_utilized_time * rate

        return float(total)
