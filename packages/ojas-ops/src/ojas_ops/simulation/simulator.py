"""Simulation and reactive rescheduling engine."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import copy
from typing import TYPE_CHECKING

import msgspec

from ojas_ops.models.schedule import ScheduleResult
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.objectives.stability import ScheduleStabilityObjective
from ojas_ops.simulation.disruption import Disruption, DisruptionType
from ojas_ops.simulation.metrics import ScheduleStabilityMetrics, calculate_stability_metrics
from ojas_ops.solvers.cp_sat import CpSatSolver
from ojas_ops.validation.report import ValidationReport
from ojas_ops.validation.validator import ScheduleValidator

if TYPE_CHECKING:
    from ojas_ops.calendars.base import CalendarProvider
    from ojas_ops.constraints.base import Constraint
    from ojas_ops.models.resource import Resource
    from ojas_ops.models.task import Task
    from ojas_ops.models.time import Horizon


class SimulationOutcome(msgspec.Struct, kw_only=True):
    """Result of a scenario simulation and reschedule proposal."""

    rescheduled_result: ScheduleResult
    validation_report: ValidationReport
    stability_metrics: ScheduleStabilityMetrics
    affected_tasks: list[str] = msgspec.field(default_factory=list)


class ScenarioSimulator:
    """Simulates operational disruptions and generates minimally disruptive rescheduled alternatives."""

    def __init__(
        self,
        *,
        tasks: dict[str, Task],
        resources: dict[str, Resource],
        horizon: Horizon | None = None,
        constraints: list[Constraint] | None = None,
        calendars: list[CalendarProvider] | None = None,
    ) -> None:
        self.tasks = copy.deepcopy(tasks)
        self.resources = copy.deepcopy(resources)
        self.horizon = horizon
        self.constraints = list(constraints or [])
        self.calendars = list(calendars or [])

    def simulate(
        self,
        *,
        baseline_schedule: ScheduleResult,
        disruptions: list[Disruption],
        current_time: int = 0,
        freeze_completed_tasks: bool = True,
        stability_weight: float = 1.0,
        makespan_weight: float = 0.5,
    ) -> SimulationOutcome:
        """Apply disruptions, maintain stability relative to baseline, and solve."""
        tasks_copy = copy.deepcopy(self.tasks)
        resources_copy = copy.deepcopy(self.resources)
        affected_tasks: set[str] = set()

        # 1. Freeze tasks that finished or started before current_time if requested
        baseline_starts: dict[str, int] = {}
        for tid, st in baseline_schedule.tasks.items():
            baseline_starts[tid] = st.start
            if freeze_completed_tasks and st.start < current_time and tid in tasks_copy:
                tasks_copy[tid].fixed_start = st.start

        # 2. Apply disruptions
        for d in disruptions:
            if d.type == DisruptionType.RESOURCE_UNAVAILABLE:
                if d.resource_id and d.start is not None and d.end is not None:
                    if d.resource_id in resources_copy:
                        win = IntervalWindow(
                            start=d.start,
                            end=d.end,
                            label=f"disruption:{d.description or 'outage'}",
                            hard=True,
                        )
                        resources_copy[d.resource_id].blackout_windows.append(win)
                        # Identify tasks scheduled on this resource that overlap
                        for tid, st in baseline_schedule.tasks.items():
                            if d.resource_id in st.assigned_resources and win.overlaps(
                                st.start, st.end
                            ):
                                affected_tasks.add(tid)

            elif d.type == DisruptionType.TASK_DELAYED:
                if d.task_id and d.task_id in tasks_copy:
                    affected_tasks.add(d.task_id)
                    # Push earliest start
                    min_new_start = (
                        baseline_schedule.tasks[d.task_id].start + d.delta
                        if d.task_id in baseline_schedule.tasks
                        else d.delta
                    )
                    from ojas_ops.models.time import TimeWindow

                    orig_tw = tasks_copy[d.task_id].time_window or TimeWindow()
                    tasks_copy[d.task_id].time_window = TimeWindow(
                        earliest_start=max(orig_tw.earliest_start or 0, min_new_start),
                        latest_start=orig_tw.latest_start,
                        earliest_end=orig_tw.earliest_end,
                        latest_end=orig_tw.latest_end,
                        deadline=orig_tw.deadline,
                    )

            elif d.type == DisruptionType.TASK_DURATION_INCREASED:
                if d.task_id and d.task_id in tasks_copy:
                    affected_tasks.add(d.task_id)
                    tasks_copy[d.task_id].duration += d.delta

            elif d.type == DisruptionType.TASK_ADDED:
                if d.new_task:
                    tasks_copy[d.new_task.id] = d.new_task
                    affected_tasks.add(d.new_task.id)

            elif d.type == DisruptionType.TASK_CANCELLED:
                if d.task_id and d.task_id in tasks_copy:
                    del tasks_copy[d.task_id]
                    affected_tasks.add(d.task_id)

            elif d.type == DisruptionType.CAPACITY_REDUCED:
                if d.resource_id and d.resource_id in resources_copy:
                    resources_copy[d.resource_id].capacity = max(
                        1, resources_copy[d.resource_id].capacity - d.delta
                    )

        # 3. Formulate dual stability + makespan objective
        objectives = [
            ScheduleStabilityObjective(baseline_starts=baseline_starts, weight=stability_weight),
            MinimizeMakespanObjective(weight=makespan_weight),
        ]
        composite_objective = WeightedCompositeObjective(objectives)

        # 4. Solve with warm-start solution hints from baseline schedule
        solver = CpSatSolver()
        rescheduled_result = solver.solve(
            tasks=tasks_copy,
            resources=resources_copy,
            horizon=self.horizon,
            constraints=self.constraints,
            objective=composite_objective,
            calendars=self.calendars,
            solution_hints=baseline_starts,
        )

        # 5. Validate independently
        validator = ScheduleValidator(
            tasks=tasks_copy,
            resources=resources_copy,
            constraints=self.constraints,
            calendars=self.calendars,
        )
        validation_report = validator.validate(rescheduled_result)

        # 6. Measure stability metrics
        stability_metrics = calculate_stability_metrics(baseline_schedule, rescheduled_result)

        return SimulationOutcome(
            rescheduled_result=rescheduled_result,
            validation_report=validation_report,
            stability_metrics=stability_metrics,
            affected_tasks=sorted(affected_tasks),
        )
