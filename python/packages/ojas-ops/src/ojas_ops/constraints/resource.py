"""Resource capacity and disjunctive non-overlapping constraints."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING

from ojas_ops.constraints.base import Constraint, SolverContext
from ojas_ops.validation.report import ConstraintViolation, Severity

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class NoOverlapConstraint(Constraint):
    """Enforces that tasks requiring the same unitary resource (capacity=1) do not overlap."""

    def __init__(self, resource_id: str, name: str = "") -> None:
        super().__init__(name=name or f"NoOverlap_{resource_id}")
        self.resource_id = resource_id

    def apply_to_solver(self, context: SolverContext) -> None:
        intervals = context.resource_intervals.get(self.resource_id, [])
        if len(intervals) > 1:
            context.model.add_no_overlap(intervals)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        assignment = resources.get(self.resource_id)
        if not assignment or len(assignment.task_ids) < 2:
            return violations

        res_tasks = [tasks[tid] for tid in assignment.task_ids if tid in tasks]
        res_tasks.sort(key=lambda t: t.start)

        for i in range(len(res_tasks) - 1):
            t1 = res_tasks[i]
            t2 = res_tasks[i + 1]
            if t1.overlaps(t2):
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        resource_id=self.resource_id,
                        task_id=t2.task_id,
                        message=(
                            f"Resource '{self.resource_id}' collision: task '{t1.task_id}' [{t1.start}, {t1.end}) "
                            f"overlaps with '{t2.task_id}' [{t2.start}, {t2.end})"
                        ),
                        severity=Severity.ERROR,
                    )
                )

        return violations


class CumulativeResourceConstraint(Constraint):
    """Enforces that total demand on a shared resource does not exceed its capacity at any moment."""

    def __init__(
        self,
        resource_id: str,
        capacity: int,
        task_demands: dict[str, int] | None = None,
        name: str = "",
    ) -> None:
        super().__init__(name=name or f"Cumulative_{resource_id}")
        self.resource_id = resource_id
        self.capacity = capacity
        self.task_demands = task_demands or {}

    def apply_to_solver(self, context: SolverContext) -> None:
        demands_list = context.resource_demands.get(self.resource_id, [])
        if not demands_list:
            return

        intervals = [item[0] for item in demands_list]
        demands = [item[1] for item in demands_list]
        context.model.add_cumulative(intervals, demands, self.capacity)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        assignment = resources.get(self.resource_id)
        if not assignment:
            return violations

        # Time-point event sweep to check capacity
        events: list[tuple[int, int, str]] = []  # (time, demand_change, task_id)
        for tid in assignment.task_ids:
            if tid in tasks:
                t = tasks[tid]
                demand = self.task_demands.get(tid, 1)
                events.append((t.start, demand, tid))
                events.append((t.end, -demand, tid))

        # Sort events: if same time, end (negative delta) precedes start (positive delta)
        events.sort(key=lambda x: (x[0], x[1]))

        current_usage = 0
        for time_pt, delta, tid in events:
            current_usage += delta
            if current_usage > self.capacity:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        resource_id=self.resource_id,
                        task_id=tid,
                        message=(
                            f"Resource '{self.resource_id}' capacity exceeded: {current_usage} > {self.capacity} "
                            f"at time {time_pt} (involving task '{tid}')"
                        ),
                        severity=Severity.ERROR,
                    )
                )
                break  # Record one violation per peak to keep reports concise

        return violations
