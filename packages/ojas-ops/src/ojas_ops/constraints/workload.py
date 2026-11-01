"""Workload and rest constraints for workforce rostering and equipment duty cycles."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING

from ojas_ops.constraints.base import Constraint, SolverContext
from ojas_ops.validation.report import ConstraintViolation, Severity

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class MaxWorkloadConstraint(Constraint):
    """Restricts the maximum cumulative working duration for a resource over a scheduling horizon."""

    def __init__(self, resource_id: str, max_duration: int, name: str = "") -> None:
        super().__init__(name=name or f"MaxWorkload_{resource_id}")
        self.resource_id = resource_id
        self.max_duration = max_duration

    def apply_to_solver(self, context: SolverContext) -> None:
        duration_terms = []
        for tid, task in context.tasks.items():
            tv = context.task_vars.get(tid)
            if not tv:
                continue

            if self.resource_id in tv.resource_intervals:
                # Optional assignment: add duration only if presence var is 1
                _, pres = tv.resource_intervals[self.resource_id]
                duration_terms.append(pres * task.duration)
            elif self.resource_id in task.required_resources:
                # Static assignment
                duration_terms.append(task.duration)

        if duration_terms:
            context.model.add(sum(duration_terms) <= self.max_duration)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        assignment = resources.get(self.resource_id)
        if not assignment:
            return violations

        total_worked = sum(tasks[tid].duration for tid in assignment.task_ids if tid in tasks)
        if total_worked > self.max_duration:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    resource_id=self.resource_id,
                    message=(
                        f"Resource '{self.resource_id}' exceeded max workload: "
                        f"{total_worked} > {self.max_duration} units"
                    ),
                    severity=Severity.ERROR,
                )
            )
        return violations


class MinRestConstraint(Constraint):
    """Enforces a minimum rest/recovery interval between any two consecutive tasks on a resource."""

    def __init__(self, resource_id: str, min_rest: int, name: str = "") -> None:
        super().__init__(name=name or f"MinRest_{resource_id}")
        self.resource_id = resource_id
        self.min_rest = min_rest

    def apply_to_solver(self, context: SolverContext) -> None:
        # Find all tasks that could run on this resource (static or optional)
        eligible_tids = []
        for tid, task in context.tasks.items():
            tv = context.task_vars.get(tid)
            if not tv:
                continue
            if (
                self.resource_id in tv.resource_intervals
                or self.resource_id in task.required_resources
            ):
                eligible_tids.append(tid)

        if len(eligible_tids) < 2:
            return

        model = context.model
        task_vars = context.task_vars

        for i in range(len(eligible_tids)):
            t1_id = eligible_tids[i]
            tv1 = task_vars[t1_id]
            pres1 = (
                tv1.resource_intervals[self.resource_id][1]
                if self.resource_id in tv1.resource_intervals
                else None
            )

            for j in range(i + 1, len(eligible_tids)):
                t2_id = eligible_tids[j]
                tv2 = task_vars[t2_id]
                pres2 = (
                    tv2.resource_intervals[self.resource_id][1]
                    if self.resource_id in tv2.resource_intervals
                    else None
                )

                b_precedes = model.new_bool_var(f"rest_ord_{self.resource_id}_{t1_id}_{t2_id}")

                if pres1 is not None and pres2 is not None:
                    # Both are optional: rest applies only if both tasks are assigned to this resource
                    both = model.new_bool_var(f"both_{self.resource_id}_{t1_id}_{t2_id}")
                    model.add_bool_and([pres1, pres2]).only_enforce_if(both)
                    model.add_bool_or([pres1.negated(), pres2.negated()]).only_enforce_if(
                        both.negated()
                    )

                    model.add(tv2.start >= tv1.end + self.min_rest).only_enforce_if(
                        [both, b_precedes]
                    )
                    model.add(tv1.start >= tv2.end + self.min_rest).only_enforce_if(
                        [both, b_precedes.negated()]
                    )
                elif pres1 is not None:
                    model.add(tv2.start >= tv1.end + self.min_rest).only_enforce_if(
                        [pres1, b_precedes]
                    )
                    model.add(tv1.start >= tv2.end + self.min_rest).only_enforce_if(
                        [pres1, b_precedes.negated()]
                    )
                elif pres2 is not None:
                    model.add(tv2.start >= tv1.end + self.min_rest).only_enforce_if(
                        [pres2, b_precedes]
                    )
                    model.add(tv1.start >= tv2.end + self.min_rest).only_enforce_if(
                        [pres2, b_precedes.negated()]
                    )
                else:
                    # Both statically assigned
                    model.add(tv2.start >= tv1.end + self.min_rest).only_enforce_if(b_precedes)
                    model.add(tv1.start >= tv2.end + self.min_rest).only_enforce_if(
                        b_precedes.negated()
                    )

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
            rest_gap = t2.start - t1.end
            if rest_gap < self.min_rest:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        resource_id=self.resource_id,
                        task_id=t2.task_id,
                        message=(
                            f"Rest violation on resource '{self.resource_id}': "
                            f"gap between '{t1.task_id}' and '{t2.task_id}' was {rest_gap} units, "
                            f"minimum required rest is {self.min_rest} units"
                        ),
                        severity=Severity.ERROR,
                    )
                )

        return violations
