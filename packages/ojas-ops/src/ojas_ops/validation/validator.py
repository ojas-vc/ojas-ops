"""Independent deterministic schedule validation engine."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import TYPE_CHECKING

from ojas_ops.models.schedule import ScheduleResult
from ojas_ops.models.task import DependencyType
from ojas_ops.validation.report import ConstraintViolation, Severity, ValidationReport

if TYPE_CHECKING:
    from ojas_ops.calendars.base import CalendarProvider
    from ojas_ops.constraints.base import Constraint
    from ojas_ops.models.resource import Resource
    from ojas_ops.models.task import Task


class ScheduleValidator:
    """Performs deterministic independent validation of scheduling outcomes without solver dependencies."""

    def __init__(
        self,
        *,
        tasks: dict[str, Task],
        resources: dict[str, Resource],
        constraints: list[Constraint] | None = None,
        calendars: list[CalendarProvider] | None = None,
    ) -> None:
        self.tasks = tasks
        self.resources = resources
        self.constraints = constraints or []
        self.calendars = calendars or []

    def validate(self, schedule: ScheduleResult) -> ValidationReport:
        from ojas_ops.constraints.resource import (
            CumulativeResourceConstraint,
            NoOverlapConstraint,
        )
        from ojas_ops.constraints.temporal import (
            FixedTimeConstraint,
            PrecedenceConstraint,
            TimeWindowConstraint,
        )
        from ojas_ops.constraints.windows import (
            BlackoutWindowConstraint,
            TargetWindowConstraint,
        )

        violations: list[ConstraintViolation] = []

        # 1. Status feasibility check
        if not schedule.is_feasible:
            violations.append(
                ConstraintViolation(
                    constraint_name="SolverStatus",
                    message=f"Schedule marked as {schedule.status.value}",
                    severity=Severity.ERROR,
                )
            )
            return ValidationReport(
                is_valid=False,
                violations=violations,
                summary=f"Infeasible schedule with status {schedule.status.value}",
            )

        # 2. Check task duration and existence
        for tid, orig_task in self.tasks.items():
            st = schedule.tasks.get(tid)
            if not st:
                violations.append(
                    ConstraintViolation(
                        constraint_name="TaskCoverage",
                        task_id=tid,
                        message=f"Task '{tid}' was not scheduled",
                        severity=Severity.ERROR,
                    )
                )
                continue

            actual_duration = st.end - st.start
            if actual_duration != orig_task.duration:
                violations.append(
                    ConstraintViolation(
                        constraint_name="TaskDuration",
                        task_id=tid,
                        message=(
                            f"Task '{tid}' scheduled duration ({actual_duration}) does not match "
                            f"required duration ({orig_task.duration})"
                        ),
                        severity=Severity.ERROR,
                    )
                )

            # Fixed start
            if orig_task.fixed_start is not None and st.start != orig_task.fixed_start:
                fixed_c = FixedTimeConstraint(tid, orig_task.fixed_start)
                violations.extend(fixed_c.validate(schedule.tasks, schedule.resources))

            # Time windows
            if orig_task.time_window:
                tw = orig_task.time_window
                tw_c = TimeWindowConstraint(
                    task_id=tid,
                    earliest_start=tw.earliest_start,
                    latest_start=tw.latest_start,
                    earliest_end=tw.earliest_end,
                    latest_end=tw.latest_end,
                    deadline=tw.deadline,
                )
                violations.extend(tw_c.validate(schedule.tasks, schedule.resources))

            # Dependencies
            for pred_id in orig_task.dependencies:
                prec_c = PrecedenceConstraint(pred_id, tid, DependencyType.FS)
                violations.extend(prec_c.validate(schedule.tasks, schedule.resources))

        # 3. Check resources
        for rid, res in self.resources.items():
            if res.capacity == 1:
                no_overlap = NoOverlapConstraint(rid)
                violations.extend(no_overlap.validate(schedule.tasks, schedule.resources))
            else:
                demands: dict[str, int] = {}
                for t_id, task in self.tasks.items():
                    for req in task.resource_requirements:
                        if req.resource_id == rid or rid in req.candidate_pool:
                            demands[t_id] = req.capacity
                cumul = CumulativeResourceConstraint(rid, res.capacity, task_demands=demands)
                violations.extend(cumul.validate(schedule.tasks, schedule.resources))

            for b_win in res.blackout_windows:
                b_c = BlackoutWindowConstraint(b_win, resource_id=rid)
                violations.extend(b_c.validate(schedule.tasks, schedule.resources))

        # 4. Check calendars
        for cal in self.calendars:
            for b_win in cal.get_blackout_windows():
                for tid in schedule.tasks:
                    b_c = BlackoutWindowConstraint(b_win, task_id=tid)
                    violations.extend(b_c.validate(schedule.tasks, schedule.resources))

            for tid in schedule.tasks:
                for t_win in cal.get_target_windows(tid):
                    t_c = TargetWindowConstraint(tid, t_win)
                    violations.extend(t_c.validate(schedule.tasks, schedule.resources))

        # 5. Check custom explicit constraints
        for c in self.constraints:
            violations.extend(c.validate(schedule.tasks, schedule.resources))

        is_valid = not any(v.severity == Severity.ERROR for v in violations)
        summary = (
            "Schedule is valid and satisfied all constraints."
            if is_valid
            else f"Validation failed with {sum(1 for v in violations if v.severity == Severity.ERROR)} errors."
        )

        return ValidationReport(
            is_valid=is_valid,
            violations=violations,
            summary=summary,
        )
