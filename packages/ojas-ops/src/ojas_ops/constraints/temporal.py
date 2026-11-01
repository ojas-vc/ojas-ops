"""Temporal constraints including task precedence, dependencies, and window bounds."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING

from ojas_ops.constraints.base import Constraint, SolverContext
from ojas_ops.models.task import DependencyType
from ojas_ops.validation.report import ConstraintViolation, Severity

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class PrecedenceConstraint(Constraint):
    """Enforces dependency ordering between a predecessor and successor task."""

    def __init__(
        self,
        predecessor_id: str,
        successor_id: str,
        dependency_type: DependencyType = DependencyType.FS,
        min_lag: int = 0,
        max_lag: int | None = None,
        name: str = "",
    ) -> None:
        super().__init__(name=name or f"Precedence_{predecessor_id}->{successor_id}")
        self.predecessor_id = predecessor_id
        self.successor_id = successor_id
        self.dependency_type = dependency_type
        self.min_lag = min_lag
        self.max_lag = max_lag

    def apply_to_solver(self, context: SolverContext) -> None:
        if (
            self.predecessor_id not in context.task_vars
            or self.successor_id not in context.task_vars
        ):
            return

        pred = context.task_vars[self.predecessor_id]
        succ = context.task_vars[self.successor_id]

        if self.dependency_type == DependencyType.FS:
            context.model.add(succ.start >= pred.end + self.min_lag)
            if self.max_lag is not None:
                context.model.add(succ.start <= pred.end + self.max_lag)
        elif self.dependency_type == DependencyType.SS:
            context.model.add(succ.start >= pred.start + self.min_lag)
            if self.max_lag is not None:
                context.model.add(succ.start <= pred.start + self.max_lag)
        elif self.dependency_type == DependencyType.FF:
            context.model.add(succ.end >= pred.end + self.min_lag)
            if self.max_lag is not None:
                context.model.add(succ.end <= pred.end + self.max_lag)
        elif self.dependency_type == DependencyType.SF:
            context.model.add(succ.end >= pred.start + self.min_lag)
            if self.max_lag is not None:
                context.model.add(succ.end <= pred.start + self.max_lag)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        pred = tasks.get(self.predecessor_id)
        succ = tasks.get(self.successor_id)

        if not pred or not succ:
            return violations

        if self.dependency_type == DependencyType.FS:
            expected_min = pred.end + self.min_lag
            if succ.start < expected_min:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.successor_id,
                        message=(
                            f"Precedence violation: {self.successor_id} started at {succ.start}, "
                            f"but {self.predecessor_id} finished at {pred.end} (min lag {self.min_lag})"
                        ),
                        severity=Severity.ERROR,
                    )
                )
            if self.max_lag is not None and succ.start > pred.end + self.max_lag:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.successor_id,
                        message=(
                            f"Max lag exceeded: {self.successor_id} started at {succ.start}, "
                            f"exceeding max lag {self.max_lag} after {pred.end}"
                        ),
                        severity=Severity.ERROR,
                    )
                )
        elif self.dependency_type == DependencyType.SS:
            if succ.start < pred.start + self.min_lag:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.successor_id,
                        message=f"SS precedence violation: {self.successor_id} start < {self.predecessor_id} start + {self.min_lag}",
                        severity=Severity.ERROR,
                    )
                )
        elif self.dependency_type == DependencyType.FF:
            if succ.end < pred.end + self.min_lag:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.successor_id,
                        message=f"FF precedence violation: {self.successor_id} end < {self.predecessor_id} end + {self.min_lag}",
                        severity=Severity.ERROR,
                    )
                )
        elif self.dependency_type == DependencyType.SF:
            if succ.end < pred.start + self.min_lag:
                violations.append(
                    ConstraintViolation(
                        constraint_name=self.name,
                        task_id=self.successor_id,
                        message=f"SF precedence violation: {self.successor_id} end < {self.predecessor_id} start + {self.min_lag}",
                        severity=Severity.ERROR,
                    )
                )

        return violations


class TimeWindowConstraint(Constraint):
    """Enforces earliest/latest start, end, and deadline boundaries on a task."""

    def __init__(
        self,
        task_id: str,
        earliest_start: int | None = None,
        latest_start: int | None = None,
        earliest_end: int | None = None,
        latest_end: int | None = None,
        deadline: int | None = None,
        name: str = "",
    ) -> None:
        super().__init__(name=name or f"TimeWindow_{task_id}")
        self.task_id = task_id
        self.earliest_start = earliest_start
        self.latest_start = latest_start
        self.earliest_end = earliest_end
        self.latest_end = latest_end
        self.deadline = deadline

    def apply_to_solver(self, context: SolverContext) -> None:
        if self.task_id not in context.task_vars:
            return
        tv = context.task_vars[self.task_id]

        if self.earliest_start is not None:
            context.model.add(tv.start >= self.earliest_start)
        if self.latest_start is not None:
            context.model.add(tv.start <= self.latest_start)
        if self.earliest_end is not None:
            context.model.add(tv.end >= self.earliest_end)
        if self.latest_end is not None:
            context.model.add(tv.end <= self.latest_end)
        if self.deadline is not None:
            context.model.add(tv.end <= self.deadline)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        task = tasks.get(self.task_id)
        if not task:
            return violations

        if self.earliest_start is not None and task.start < self.earliest_start:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} start ({task.start}) < earliest start ({self.earliest_start})",
                    severity=Severity.ERROR,
                )
            )
        if self.latest_start is not None and task.start > self.latest_start:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} start ({task.start}) > latest start ({self.latest_start})",
                    severity=Severity.ERROR,
                )
            )
        if self.earliest_end is not None and task.end < self.earliest_end:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} end ({task.end}) < earliest end ({self.earliest_end})",
                    severity=Severity.ERROR,
                )
            )
        if self.latest_end is not None and task.end > self.latest_end:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} end ({task.end}) > latest end ({self.latest_end})",
                    severity=Severity.ERROR,
                )
            )
        if self.deadline is not None and task.end > self.deadline:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} missed deadline {self.deadline} (finished at {task.end})",
                    severity=Severity.ERROR,
                )
            )

        return violations


class FixedTimeConstraint(Constraint):
    """Pins a task to an exact start time."""

    def __init__(self, task_id: str, fixed_start: int, name: str = "") -> None:
        super().__init__(name=name or f"FixedTime_{task_id}")
        self.task_id = task_id
        self.fixed_start = fixed_start

    def apply_to_solver(self, context: SolverContext) -> None:
        if self.task_id in context.task_vars:
            context.model.add(context.task_vars[self.task_id].start == self.fixed_start)

    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        violations: list[ConstraintViolation] = []
        task = tasks.get(self.task_id)
        if task and task.start != self.fixed_start:
            violations.append(
                ConstraintViolation(
                    constraint_name=self.name,
                    task_id=self.task_id,
                    message=f"Task {self.task_id} scheduled at {task.start}, expected fixed start {self.fixed_start}",
                    severity=Severity.ERROR,
                )
            )
        return violations
