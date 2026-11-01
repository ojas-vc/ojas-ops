"""Google OR-Tools CP-SAT mathematical optimization solver backend."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import time
from typing import TYPE_CHECKING

from ortools.sat.python import cp_model

from ojas_ops.constraints.base import SolverContext, TaskVars
from ojas_ops.constraints.resource import (
    CumulativeResourceConstraint,
    NoOverlapConstraint,
)
from ojas_ops.constraints.temporal import (
    PrecedenceConstraint,
)
from ojas_ops.constraints.windows import (
    BlackoutWindowConstraint,
    TargetWindowConstraint,
)
from ojas_ops.models.schedule import (
    ResourceAssignment,
    ScheduledTask,
    ScheduleResult,
    ScheduleStatus,
)
from ojas_ops.models.task import DependencyType, Task
from ojas_ops.models.time import Horizon
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.solvers.config import SolverConfig

if TYPE_CHECKING:
    from ojas_ops.calendars.base import CalendarProvider
    from ojas_ops.constraints.base import Constraint
    from ojas_ops.models.resource import Resource
    from ojas_ops.objectives.base import Objective


class CpSatSolver:
    """Compiles operational scheduling models and executes Google OR-Tools CP-SAT."""

    def __init__(self, config: SolverConfig | None = None) -> None:
        self.config = config or SolverConfig()

    def solve(
        self,
        *,
        tasks: dict[str, Task],
        resources: dict[str, Resource],
        horizon: Horizon | None = None,
        constraints: list[Constraint] | None = None,
        objective: Objective | None = None,
        calendars: list[CalendarProvider] | None = None,
    ) -> ScheduleResult:
        wall_start = time.perf_counter()

        # Compute horizon if not provided
        if horizon is None:
            max_duration = sum(t.duration for t in tasks.values()) + 1440
            horizon = Horizon(start=0, end=max_duration)

        model = cp_model.CpModel()
        context = SolverContext(
            model=model,
            tasks=tasks,
            resources=resources,
            horizon=horizon,
        )

        # 1. Create task variables
        for tid, task in tasks.items():
            earliest_start = 0
            latest_start = horizon.end
            earliest_end = task.duration
            latest_end = horizon.end

            if task.time_window:
                tw = task.time_window
                if tw.earliest_start is not None:
                    earliest_start = max(earliest_start, tw.earliest_start)
                if tw.latest_start is not None:
                    latest_start = min(latest_start, tw.latest_start)
                if tw.earliest_end is not None:
                    earliest_end = max(earliest_end, tw.earliest_end)
                if tw.latest_end is not None:
                    latest_end = min(latest_end, tw.latest_end)
                if tw.deadline is not None:
                    latest_end = min(latest_end, tw.deadline)

            start_var = model.new_int_var(earliest_start, latest_start, f"start_{tid}")
            end_var = model.new_int_var(earliest_end, latest_end, f"end_{tid}")
            interval_var = model.new_interval_var(
                start_var, task.duration, end_var, f"interval_{tid}"
            )

            tv = TaskVars(
                start=start_var,
                end=end_var,
                interval=interval_var,
                duration=task.duration,
            )

            # Fixed start
            if task.fixed_start is not None:
                model.add(start_var == task.fixed_start)

            # Check for candidate pool assignment or direct required resources
            for req in task.resource_requirements:
                if req.candidate_pool:
                    # Alternative resource choice from candidate pool
                    presence_vars = []
                    for cand_id in req.candidate_pool:
                        if cand_id in resources:
                            pres = model.new_bool_var(f"pres_{tid}_{cand_id}")
                            opt_int = model.new_optional_interval_var(
                                start_var, task.duration, end_var, pres, f"opt_{tid}_{cand_id}"
                            )
                            tv.resource_intervals[cand_id] = (opt_int, pres)
                            presence_vars.append(pres)
                            context.resource_intervals[cand_id].append(opt_int)
                            context.resource_demands[cand_id].append((opt_int, req.capacity))
                    # Exactly one resource from pool must be chosen
                    if presence_vars:
                        model.add_exactly_one(presence_vars)
                else:
                    # Direct assigned resource
                    rid = req.resource_id
                    if rid in resources:
                        context.resource_intervals[rid].append(interval_var)
                        context.resource_demands[rid].append((interval_var, req.capacity))

            context.task_vars[tid] = tv

        # 2. Add implicit precedence from task.dependencies
        for tid, task in tasks.items():
            for pred_id in task.dependencies:
                if pred_id in tasks:
                    prec = PrecedenceConstraint(pred_id, tid, DependencyType.FS)
                    prec.apply_to_solver(context)

        # 3. Add implicit resource constraints (NoOverlap or Cumulative)
        for rid, res in resources.items():
            if res.capacity == 1:
                no_overlap = NoOverlapConstraint(rid)
                no_overlap.apply_to_solver(context)
            else:
                cumulative = CumulativeResourceConstraint(rid, res.capacity)
                cumulative.apply_to_solver(context)

            # Add resource blackout windows
            for b_win in res.blackout_windows:
                b_constraint = BlackoutWindowConstraint(b_win, resource_id=rid)
                b_constraint.apply_to_solver(context)

        # 4. Integrate CalendarProviders
        if calendars:
            for cal in calendars:
                # Blackout windows
                for b_win in cal.get_blackout_windows():
                    b_constraint = BlackoutWindowConstraint(b_win)
                    b_constraint.apply_to_solver(context)
                # Task target windows
                for tid in tasks:
                    for t_win in cal.get_target_windows(tid):
                        t_constraint = TargetWindowConstraint(tid, t_win)
                        t_constraint.apply_to_solver(context)

        # 5. Apply user-provided explicit constraints
        if constraints:
            for c in constraints:
                c.apply_to_solver(context)

        # 6. Apply objective
        active_objective = objective or MinimizeMakespanObjective()
        obj_expr = active_objective.build_expression(context)
        if getattr(active_objective, "is_maximize", False):
            model.maximize(obj_expr)
        else:
            model.minimize(obj_expr)

        # 7. Configure and run CP-SAT solver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.config.time_limit_seconds
        solver.parameters.num_workers = self.config.num_workers
        solver.parameters.random_seed = self.config.random_seed
        solver.parameters.log_search_progress = self.config.log_search_progress
        if self.config.stop_after_first_solution:
            solver.parameters.stop_after_first_solution = True

        solve_status = solver.solve(model)
        solve_time = solver.wall_time

        # 8. Translate status
        status_map = {
            cp_model.OPTIMAL: ScheduleStatus.OPTIMAL,
            cp_model.FEASIBLE: ScheduleStatus.FEASIBLE,
            cp_model.INFEASIBLE: ScheduleStatus.INFEASIBLE,
            cp_model.MODEL_INVALID: ScheduleStatus.MODEL_INVALID,
            cp_model.UNKNOWN: ScheduleStatus.UNKNOWN,
        }
        res_status = status_map.get(solve_status, ScheduleStatus.UNKNOWN)

        if res_status not in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE):
            return ScheduleResult(
                status=res_status,
                objective_value=float("inf"),
                tasks={},
                resources={},
                makespan=0,
                solve_time_seconds=solve_time,
                wall_time=time.perf_counter() - wall_start,
                metadata={"solver_status_name": solver.status_name(solve_status)},
            )

        # 9. Extract scheduled tasks and resource assignments
        scheduled_tasks: dict[str, ScheduledTask] = {}
        resource_task_map: dict[str, list[str]] = {rid: [] for rid in resources}

        for tid, task in tasks.items():
            tv = context.task_vars[tid]
            start_val = solver.value(tv.start)
            end_val = solver.value(tv.end)

            assigned: list[str] = []
            # Check direct requirements
            for req in task.resource_requirements:
                if req.candidate_pool:
                    for cand_id in req.candidate_pool:
                        if cand_id in tv.resource_intervals:
                            _, pres_var = tv.resource_intervals[cand_id]
                            if solver.value(pres_var) == 1:
                                assigned.append(cand_id)
                                resource_task_map[cand_id].append(tid)
                else:
                    if req.resource_id in resources:
                        assigned.append(req.resource_id)
                        resource_task_map[req.resource_id].append(tid)

            scheduled_tasks[tid] = ScheduledTask(
                task_id=tid,
                start=start_val,
                end=end_val,
                duration=task.duration,
                assigned_resources=assigned,
                metadata=dict(task.metadata),
            )

        # Build ResourceAssignment summaries
        resource_assignments: dict[str, ResourceAssignment] = {}
        for rid, tids in resource_task_map.items():
            res = resources[rid]
            tids.sort(key=lambda t_id: scheduled_tasks[t_id].start)
            total_worked = sum(scheduled_tasks[t_id].duration for t_id in tids)

            idle_time = 0
            if len(tids) > 1:
                first_start = scheduled_tasks[tids[0]].start
                last_end = scheduled_tasks[tids[-1]].end
                span = last_end - first_start
                idle_time = max(0, span - total_worked)

            overtime = 0
            if res.regular_capacity_limit is not None:
                overtime = max(0, total_worked - res.regular_capacity_limit)

            resource_assignments[rid] = ResourceAssignment(
                resource_id=rid,
                task_ids=tids,
                total_utilized_time=total_worked,
                idle_time=idle_time,
                overtime=overtime,
            )

        makespan = max((st.end for st in scheduled_tasks.values()), default=0)

        return ScheduleResult(
            status=res_status,
            objective_value=float(solver.objective_value),
            tasks=scheduled_tasks,
            resources=resource_assignments,
            makespan=makespan,
            solve_time_seconds=solve_time,
            wall_time=time.perf_counter() - wall_start,
            metadata={"solver_status_name": solver.status_name(solve_status)},
        )
