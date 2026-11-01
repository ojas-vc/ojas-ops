"""Sequence-dependent setup times, turnaround buffers, and transition matrices."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ojas_ops.constraints.base import Constraint, SolverContext
from ojas_ops.validation.report import ConstraintViolation, Severity

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class TransitionConstraint(Constraint):
    """Enforces sequence-dependent setup, turnaround, or travel buffers between tasks on a resource."""

    def __init__(
        self,
        resource_id: str,
        transition_matrix: dict[tuple[str, str], int] | None = None,
        default_buffer: int = 0,
        name: str = "",
    ) -> None:
        super().__init__(name=name or f"Transition_{resource_id}")
        self.resource_id = resource_id
        self.transition_matrix = transition_matrix or {}
        self.default_buffer = default_buffer

    def get_buffer(self, task1_id: str, task2_id: str) -> int:
        return self.transition_matrix.get((task1_id, task2_id), self.default_buffer)

    def apply_to_solver(self, context: SolverContext) -> None:
        # Find all tasks that could run on this resource (static or optional candidate pool)
        relevant_task_ids = []
        for tid, t in context.tasks.items():
            tv = context.task_vars.get(tid)
            if not tv:
                continue
            if (
                self.resource_id in tv.resource_intervals
                or self.resource_id in t.required_resources
            ):
                relevant_task_ids.append(tid)

        if len(relevant_task_ids) < 2:
            return

        model = context.model
        task_vars = context.task_vars

        for i in range(len(relevant_task_ids)):
            t1_id = relevant_task_ids[i]
            tv1 = task_vars[t1_id]
            pres1 = (
                tv1.resource_intervals[self.resource_id][1]
                if self.resource_id in tv1.resource_intervals
                else None
            )

            for j in range(i + 1, len(relevant_task_ids)):
                t2_id = relevant_task_ids[j]
                tv2 = task_vars[t2_id]
                pres2 = (
                    tv2.resource_intervals[self.resource_id][1]
                    if self.resource_id in tv2.resource_intervals
                    else None
                )

                buf_1_to_2 = self.get_buffer(t1_id, t2_id)
                buf_2_to_1 = self.get_buffer(t2_id, t1_id)

                # Boolean var: True if t1 precedes t2, False if t2 precedes t1
                b_precedes = model.new_bool_var(f"trans_{self.resource_id}_{t1_id}_{t2_id}")

                if pres1 is not None and pres2 is not None:
                    both = model.new_bool_var(f"both_trans_{self.resource_id}_{t1_id}_{t2_id}")
                    model.add_bool_and([pres1, pres2]).only_enforce_if(both)
                    model.add_bool_or([pres1.negated(), pres2.negated()]).only_enforce_if(
                        both.negated()
                    )

                    model.add(tv2.start >= tv1.end + buf_1_to_2).only_enforce_if([both, b_precedes])
                    model.add(tv1.start >= tv2.end + buf_2_to_1).only_enforce_if(
                        [both, b_precedes.negated()]
                    )
                elif pres1 is not None:
                    model.add(tv2.start >= tv1.end + buf_1_to_2).only_enforce_if(
                        [pres1, b_precedes]
                    )
                    model.add(tv1.start >= tv2.end + buf_2_to_1).only_enforce_if(
                        [pres1, b_precedes.negated()]
                    )
                elif pres2 is not None:
                    model.add(tv2.start >= tv1.end + buf_1_to_2).only_enforce_if(
                        [pres2, b_precedes]
                    )
                    model.add(tv1.start >= tv2.end + buf_2_to_1).only_enforce_if(
                        [pres2, b_precedes.negated()]
                    )
                else:
                    model.add(tv2.start >= tv1.end + buf_1_to_2).only_enforce_if(b_precedes)
                    model.add(tv1.start >= tv2.end + buf_2_to_1).only_enforce_if(
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
            required_buffer = self.get_buffer(t1.task_id, t2.task_id)
            actual_gap = t2.start - t1.end

            if actual_gap < required_buffer:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        resource_id=self.resource_id,
                        task_id=t2.task_id,
                        message=(
                            f"Insufficient transition buffer on resource '{self.resource_id}': "
                            f"'{t1.task_id}' -> '{t2.task_id}' required {required_buffer} units, "
                            f"but actual gap was {actual_gap} units [{t1.end} to {t2.start}]"
                        ),
                        severity=Severity.ERROR,
                    )
                )

        return violations
