"""High-level fluent Scheduler API orchestrating modeling, optimization, and validation."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from typing import Any

from ojas_ops.calendars.base import CalendarProvider
from ojas_ops.constraints.base import Constraint
from ojas_ops.constraints.temporal import PrecedenceConstraint
from ojas_ops.constraints.transition import TransitionConstraint
from ojas_ops.constraints.windows import BlackoutWindowConstraint, TargetWindowConstraint
from ojas_ops.constraints.workload import MaxWorkloadConstraint, MinRestConstraint
from ojas_ops.models.resource import Resource, ResourceType
from ojas_ops.models.schedule import ScheduleResult
from ojas_ops.models.task import DependencyType, ResourceRequirement, Task, TaskPriority
from ojas_ops.models.time import Horizon, IntervalWindow, TimeWindow
from ojas_ops.objectives.base import Objective
from ojas_ops.objectives.cost import MinimizeCostObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.objectives.tardiness import MinimizeTardinessObjective
from ojas_ops.simulation.disruption import Disruption
from ojas_ops.simulation.simulator import ScenarioSimulator, SimulationOutcome
from ojas_ops.solvers.config import SolverConfig
from ojas_ops.solvers.cp_sat import CpSatSolver
from ojas_ops.validation.report import ValidationReport
from ojas_ops.validation.validator import ScheduleValidator


class Scheduler:
    """Primary developer interface for building, optimizing, and verifying schedules."""

    def __init__(
        self,
        *,
        horizon: Horizon | None = None,
        solver_config: SolverConfig | None = None,
    ) -> None:
        self.horizon = horizon
        self.solver_config = solver_config or SolverConfig()
        self.tasks: dict[str, Task] = {}
        self.resources: dict[str, Resource] = {}
        self.constraints: list[Constraint] = []
        self.calendars: list[CalendarProvider] = []
        self.objective: Objective = MinimizeMakespanObjective()
        self.last_result: ScheduleResult | None = None

    def add_resource(
        self,
        id: str,
        *,
        name: str = "",
        capacity: int = 1,
        resource_type: ResourceType = ResourceType.MACHINE,
        cost_per_time_unit: float = 0.0,
        regular_capacity_limit: int | None = None,
        skills: list[str] | None = None,
        blackout_windows: list[IntervalWindow] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Resource:
        """Register a resource (person, machine, venue, channel)."""
        res = Resource(
            id=id,
            name=name or id,
            capacity=capacity,
            resource_type=resource_type,
            cost_per_time_unit=cost_per_time_unit,
            regular_capacity_limit=regular_capacity_limit,
            skills=skills or [],
            blackout_windows=blackout_windows or [],
            metadata=metadata or {},
        )
        self.resources[id] = res
        return res

    def add_task(
        self,
        id: str,
        *,
        duration: int,
        name: str = "",
        required_resources: list[str] | None = None,
        resource_requirements: list[ResourceRequirement] | None = None,
        dependencies: list[str] | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        time_window: TimeWindow | None = None,
        fixed_start: int | None = None,
        cost: float = 0.0,
        metadata: dict[str, str] | None = None,
    ) -> Task:
        """Register a schedulable task or activity."""
        task = Task(
            id=id,
            duration=duration,
            name=name or id,
            required_resources=required_resources or [],
            resource_requirements=resource_requirements or [],
            dependencies=dependencies or [],
            priority=priority,
            time_window=time_window,
            fixed_start=fixed_start,
            cost=cost,
            metadata=metadata or {},
        )
        self.tasks[id] = task
        return task

    def add_dependency(
        self,
        predecessor_id: str,
        successor_id: str,
        *,
        dependency_type: DependencyType = DependencyType.FS,
        min_lag: int = 0,
        max_lag: int | None = None,
    ) -> PrecedenceConstraint:
        """Enforce chronological precedence between tasks."""
        constraint = PrecedenceConstraint(
            predecessor_id=predecessor_id,
            successor_id=successor_id,
            dependency_type=dependency_type,
            min_lag=min_lag,
            max_lag=max_lag,
        )
        self.constraints.append(constraint)
        return constraint

    def add_blackout_window(
        self,
        *,
        window: IntervalWindow,
        resource_id: str | None = None,
        task_id: str | None = None,
    ) -> BlackoutWindowConstraint:
        """Enforce that a task or resource does not run during an unavailable window."""
        c = BlackoutWindowConstraint(window=window, resource_id=resource_id, task_id=task_id)
        self.constraints.append(c)
        return c

    def add_target_window(
        self,
        *,
        task_id: str,
        window: IntervalWindow,
        hard: bool = True,
    ) -> TargetWindowConstraint:
        """Anchor task to execute within an auspicious or designated target window."""
        c = TargetWindowConstraint(task_id=task_id, window=window, hard=hard)
        self.constraints.append(c)
        return c

    def add_transition_matrix(
        self,
        *,
        resource_id: str,
        transition_matrix: dict[tuple[str, str], int],
        default_buffer: int = 0,
    ) -> TransitionConstraint:
        """Add sequence-dependent setup/turnaround times between tasks on a resource."""
        c = TransitionConstraint(
            resource_id=resource_id,
            transition_matrix=transition_matrix,
            default_buffer=default_buffer,
        )
        self.constraints.append(c)
        return c

    def add_min_rest(self, resource_id: str, min_rest: int) -> MinRestConstraint:
        """Enforce minimum recovery time between tasks assigned to a resource."""
        c = MinRestConstraint(resource_id=resource_id, min_rest=min_rest)
        self.constraints.append(c)
        return c

    def add_max_workload(self, resource_id: str, max_duration: int) -> MaxWorkloadConstraint:
        """Limit cumulative hours assigned to a resource."""
        c = MaxWorkloadConstraint(resource_id=resource_id, max_duration=max_duration)
        self.constraints.append(c)
        return c

    def add_constraint(self, constraint: Constraint) -> None:
        """Add custom mathematical constraint."""
        self.constraints.append(constraint)

    def add_calendar(self, calendar: CalendarProvider) -> None:
        """Attach a standard or cultural calendar provider."""
        self.calendars.append(calendar)

    def set_horizon(self, start: int, end: int, granularity: int = 1) -> None:
        """Define schedule planning horizon."""
        self.horizon = Horizon(start=start, end=end, granularity=granularity)

    def minimize(self, objective_name: str | Objective, **kwargs: Any) -> None:
        """Configure the solver optimization goal to minimize."""
        if isinstance(objective_name, Objective):
            objective_name.is_maximize = False
            self.objective = objective_name
            return

        name_lower = str(objective_name).lower()
        if name_lower == "makespan":
            self.objective = MinimizeMakespanObjective(**kwargs)
        elif name_lower == "cost":
            self.objective = MinimizeCostObjective(**kwargs)
        elif name_lower == "idle_time":
            self.objective = MinimizeIdleTimeObjective(**kwargs)
        elif name_lower == "tardiness":
            self.objective = MinimizeTardinessObjective(**kwargs)
        else:
            msg = f"Unknown optimization objective: '{objective_name}'"
            raise ValueError(msg)

    def maximize(self, objective_name: str | Objective, **kwargs: Any) -> None:
        """Configure the solver optimization goal to maximize."""
        if isinstance(objective_name, Objective):
            objective_name.is_maximize = True
            self.objective = objective_name
            return

        kwargs["is_maximize"] = True
        name_lower = str(objective_name).lower()
        if name_lower == "makespan":
            self.objective = MinimizeMakespanObjective(**kwargs)
        elif name_lower == "cost":
            self.objective = MinimizeCostObjective(**kwargs)
        elif name_lower == "idle_time":
            self.objective = MinimizeIdleTimeObjective(**kwargs)
        elif name_lower == "tardiness":
            self.objective = MinimizeTardinessObjective(**kwargs)
        else:
            msg = f"Unknown optimization objective: '{objective_name}'"
            raise ValueError(msg)

    def solve(
        self,
        config: SolverConfig | None = None,
        *,
        solution_hints: dict[str, int] | None = None,
        callback: Any = None,
    ) -> ScheduleResult:
        """Compile and solve the optimization model using Google OR-Tools CP-SAT."""
        solver = CpSatSolver(config or self.solver_config)
        self.last_result = solver.solve(
            tasks=self.tasks,
            resources=self.resources,
            horizon=self.horizon,
            constraints=self.constraints,
            objective=self.objective,
            calendars=self.calendars,
            solution_hints=solution_hints,
            callback=callback,
        )
        return self.last_result

    def validate(self, result: ScheduleResult | None = None) -> ValidationReport:
        """Deterministically verify schedule feasibility and all constraints independently."""
        target_result = result or self.last_result
        if not target_result:
            msg = "No schedule result to validate. Run solve() first or pass a ScheduleResult."
            raise ValueError(msg)

        validator = ScheduleValidator(
            tasks=self.tasks,
            resources=self.resources,
            constraints=self.constraints,
            calendars=self.calendars,
        )
        return validator.validate(target_result)

    def reschedule(
        self,
        baseline: ScheduleResult,
        disruptions: list[Disruption],
        current_time: int = 0,
        freeze_completed_tasks: bool = True,
        stability_weight: float = 1.0,
        makespan_weight: float = 0.5,
    ) -> SimulationOutcome:
        """Simulate operational disruptions and produce a minimally disruptive revised schedule."""
        simulator = ScenarioSimulator(
            tasks=self.tasks,
            resources=self.resources,
            horizon=self.horizon,
            constraints=self.constraints,
            calendars=self.calendars,
        )
        return simulator.simulate(
            baseline_schedule=baseline,
            disruptions=disruptions,
            current_time=current_time,
            freeze_completed_tasks=freeze_completed_tasks,
            stability_weight=stability_weight,
            makespan_weight=makespan_weight,
        )
