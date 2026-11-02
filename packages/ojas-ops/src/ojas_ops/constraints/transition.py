"""Sequence-dependent setup times, turnaround buffers, and transition matrices."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ortools.sat.python import cp_model

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
        k = len(relevant_task_ids)

        presences = []
        for tid in relevant_task_ids:
            tv = task_vars[tid]
            if self.resource_id in tv.resource_intervals:
                # Optional interval: presence is tv.resource_intervals[self.resource_id][1]
                presences.append(tv.resource_intervals[self.resource_id][1])
            else:
                # Statically assigned task: always present on this resource
                presences.append(model.new_constant(1))

        # Build Hamiltonian circuit through node 0 (dummy) and 1..K (tasks)
        arcs: list[cp_model.ArcT] = []
        for i in range(k):
            tid_i = relevant_task_ids[i]
            # Arc 0 -> i + 1: task i is first in sequence on this resource
            start_lit = model.new_bool_var(f"circ_start_{self.resource_id}_{tid_i}")
            arcs.append((0, i + 1, start_lit))

            # Arc i + 1 -> 0: task i is last in sequence on this resource
            end_lit = model.new_bool_var(f"circ_end_{self.resource_id}_{tid_i}")
            arcs.append((i + 1, 0, end_lit))

            for j in range(k):
                if i == j:
                    # Self-loop when task i is not present
                    arcs.append((i + 1, i + 1, ~presences[i]))
                else:
                    tid_j = relevant_task_ids[j]
                    arc_lit = model.new_bool_var(f"circ_arc_{self.resource_id}_{tid_i}_{tid_j}")
                    arcs.append((i + 1, j + 1, arc_lit))
                    buf = self.get_buffer(tid_i, tid_j)
                    # Enforce transition buffer when j immediately succeeds i
                    model.add(task_vars[tid_j].start >= task_vars[tid_i].end + buf).only_enforce_if(
                        arc_lit
                    )

        # Handle empty circuit if no tasks execute on this resource
        empty_lit = model.new_bool_var(f"circ_empty_{self.resource_id}")
        arcs.append((0, 0, empty_lit))
        for i in range(k):
            model.add_implication(empty_lit, ~presences[i])

        model.add_circuit(arcs)

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
