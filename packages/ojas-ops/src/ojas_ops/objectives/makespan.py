"""Makespan minimization objective."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ojas_ops.objectives.base import Objective

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MinimizeMakespanObjective(Objective):
    """Minimizes the overall schedule completion time: max(task.end)."""

    def __init__(
        self,
        name: str = "MinimizeMakespan",
        weight: float = 1.0,
        is_maximize: bool = False,
    ) -> None:
        super().__init__(name=name, weight=weight, is_maximize=is_maximize)

    def build_expression(self, context: SolverContext) -> Any:
        if not context.task_vars:
            return 0

        makespan = context.model.new_int_var(0, context.horizon.end, f"{self.name}_var")
        for tv in context.task_vars.values():
            context.model.add(makespan >= tv.end)

        return makespan

    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        if not tasks:
            return 0.0
        return float(max(t.end for t in tasks.values()))
