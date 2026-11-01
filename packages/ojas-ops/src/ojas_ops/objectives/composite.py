"""Weighted composite objective combining multiple optimization goals."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class WeightedCompositeObjective(Objective):
    """Combines multiple objectives with configurable relative weights."""

    def __init__(
        self,
        objectives: list[Objective],
        name: str = "CompositeObjective",
        weight: float = 1.0,
    ) -> None:
        super().__init__(name=name, weight=weight)
        self.objectives = objectives

    def build_expression(self, context: SolverContext) -> Any:
        weighted_terms = []
        for obj in self.objectives:
            expr = obj.build_expression(context)
            # Scale float weights into integers for CP-SAT
            int_weight = int(round(obj.weight * 100))
            if int_weight != 0:
                weighted_terms.append(int_weight * expr)

        return sum(weighted_terms) if weighted_terms else 0

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        total = 0.0
        for obj in self.objectives:
            total += obj.weight * obj.evaluate(tasks, resources)
        return total

