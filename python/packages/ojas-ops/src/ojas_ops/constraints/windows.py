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

        # 1. If bound to a task directly: enforce non-overlap between task interval and blackout interval
        if self.task_id and self.task_id in context.task_vars:
            tv = context.task_vars[self.task_id]
            b_int = model.new_interval_var(
                self.window.start, self.window.duration, self.window.end, f"{self.name}_task_int"
            )
            model.add_no_overlap([tv.interval, b_int])

        # 2. If bound to a resource: add fixed interval to the resource's interval list
        if self.resource_id and self.resource_id in context.resources:
            res = context.resources[self.resource_id]
            b_int = model.new_interval_var(
                self.window.start,
                self.window.duration,
                self.window.end,
                f"blackout_{self.resource_id}_{self.window.start}_{self.window.end}",
            )
            context.resource_intervals[self.resource_id].append(b_int)
            context.resource_demands[self.resource_id].append((b_int, res.capacity))

        # 3. If global (neither resource nor task specified - e.g. general Rahu Kalam)
        if not self.resource_id and not self.task_id:
            for tid, tv in context.task_vars.items():
                b_int = model.new_interval_var(
                    self.window.start,
                    self.window.duration,
                    self.window.end,
                    f"{self.name}_{tid}_int",
                )
                model.add_no_overlap([tv.interval, b_int])

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
        else:
            # Soft target window: create linear violation slacks penalized in objective
            early_slack = context.model.new_int_var(
                0, context.horizon.end, f"{self.name}_early_slack"
            )
            late_slack = context.model.new_int_var(
                0, context.horizon.end, f"{self.name}_late_slack"
            )
            context.model.add(early_slack >= self.window.start - tv.start)
            context.model.add(late_slack >= tv.end - self.window.end)
            context.soft_penalties.append(early_slack)
            context.soft_penalties.append(late_slack)

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
