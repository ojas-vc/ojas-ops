"""Interval window constraints for blackout exclusions and target window inclusions."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING

from ojas_ops.constraints.base import Constraint, SolverContext
from ojas_ops.models.time import IntervalWindow
from ojas_ops.validation.report import ConstraintViolation, Severity

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class BlackoutWindowConstraint(Constraint):
    """Enforces that a resource or task does not execute during an unavailable blackout window."""

    def __init__(
        self,
        window: IntervalWindow,
        resource_id: str | None = None,
        task_id: str | None = None,
        name: str = "",
    ) -> None:
        super().__init__(
            name=name
            or f"Blackout_{resource_id or task_id or 'global'}_{window.start}_{window.end}",
            hard=window.hard,
        )
        self.window = window
        self.resource_id = resource_id
        self.task_id = task_id

    def apply_to_solver(self, context: SolverContext) -> None:
        model = context.model

        # 1. If bound to a task directly
        if self.task_id and self.task_id in context.task_vars:
            tv = context.task_vars[self.task_id]
            b_before = model.new_bool_var(f"{self.name}_before")
            model.add(tv.end <= self.window.start).only_enforce_if(b_before)
            model.add(tv.start >= self.window.end).only_enforce_if(b_before.negated())

        # 2. If bound to a resource
        if self.resource_id and self.resource_id in context.resources:
            for tid, tv in context.task_vars.items():
                task = context.tasks[tid]
                if self.resource_id in tv.resource_intervals:
                    # Optional resource assignment: enforce non-overlap only if assigned
                    _, pres = tv.resource_intervals[self.resource_id]
                    b_before = model.new_bool_var(f"blackout_{self.resource_id}_{tid}_before")
                    model.add(tv.end <= self.window.start).only_enforce_if([pres, b_before])
                    model.add(tv.start >= self.window.end).only_enforce_if(
                        [pres, b_before.negated()]
                    )
                elif self.resource_id in task.required_resources:
                    # Statically assigned resource
                    b_before = model.new_bool_var(f"blackout_{self.resource_id}_{tid}_before")
                    model.add(tv.end <= self.window.start).only_enforce_if(b_before)
                    model.add(tv.start >= self.window.end).only_enforce_if(b_before.negated())

        # 3. If global (neither resource nor task specified - e.g. general Rahu Kalam)
        if not self.resource_id and not self.task_id:
            for tid, tv in context.task_vars.items():
                b_before = model.new_bool_var(f"{self.name}_{tid}_before")
                model.add(tv.end <= self.window.start).only_enforce_if(b_before)
                model.add(tv.start >= self.window.end).only_enforce_if(b_before.negated())

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []

        if self.task_id:
            task = tasks.get(self.task_id)
            if task and self.window.overlaps(task.start, task.end):
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.task_id,
                        message=(
                            f"Task '{self.task_id}' [{task.start}, {task.end}) violated blackout window "
                            f"[{self.window.start}, {self.window.end}) ({self.window.label})"
                        ),
                        severity=Severity.ERROR if self.hard else Severity.WARNING,
                    )
                )

        if self.resource_id:
            assignment = resources.get(self.resource_id)
            if assignment:
                for tid in assignment.task_ids:
                    task = tasks.get(tid)
                    if task and self.window.overlaps(task.start, task.end):
                        violations.append(
                            ConstraintViolation(
                                constraint_name=self.name,
                                resource_id=self.resource_id,
                                task_id=tid,
                                message=(
                                    f"Resource '{self.resource_id}' scheduled task '{tid}' [{task.start}, {task.end}) "
                                    f"inside blackout window [{self.window.start}, {self.window.end}) ({self.window.label})"
                                ),
                                severity=Severity.ERROR if self.hard else Severity.WARNING,
                            )
                        )

        if not self.resource_id and not self.task_id:
            for tid, task in tasks.items():
                if self.window.overlaps(task.start, task.end):
                    violations.append(
                        ConstraintViolation(
                            constraint_name=self.name,
                            task_id=tid,
                            message=(
                                f"Task '{tid}' [{task.start}, {task.end}) violated global blackout window "
                                f"[{self.window.start}, {self.window.end}) ({self.window.label})"
                            ),
                            severity=Severity.ERROR if self.hard else Severity.WARNING,
                        )
                    )

        return violations


class TargetWindowConstraint(Constraint):
    """Enforces that a task must execute entirely within an allowed / auspicious window."""

    def __init__(
        self,
        task_id: str,
        window: IntervalWindow,
        name: str = "",
        hard: bool = True,
    ) -> None:
        super().__init__(name=name or f"TargetWindow_{task_id}_{window.label}", hard=hard)
        self.task_id = task_id
        self.window = window

    def apply_to_solver(self, context: SolverContext) -> None:
        if self.task_id not in context.task_vars:
            return
        tv = context.task_vars[self.task_id]
        if self.hard:
            context.model.add(tv.start >= self.window.start)
            context.model.add(tv.end <= self.window.end)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        task = tasks.get(self.task_id)
        if not task:
            return violations

        if not self.window.encloses(task.start, task.end):
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=(
                        f"Task '{self.task_id}' [{task.start}, {task.end}) was not within target window "
                        f"[{self.window.start}, {self.window.end}) ({self.window.label})"
                    ),
                    severity=Severity.ERROR if self.hard else Severity.WARNING,
                )
            )

        return violations
