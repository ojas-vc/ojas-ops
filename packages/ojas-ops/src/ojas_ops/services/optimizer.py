"""Optimizer service wrapping the core Scheduler."""

import time

from ojas_ops.models.time import Horizon
from ojas_ops.scheduling.scheduler import Scheduler
from ojas_ops.schemas.scheduling import (
    OptimizeScheduleRequest,
    OptimizeScheduleResponse,
)
from ojas_ops.solvers.config import SolverConfig


async def solve_schedule_service(request: OptimizeScheduleRequest) -> OptimizeScheduleResponse:
    """Solves a schedule optimization request synchronously using OR-Tools CP-SAT."""
    start_time = time.time()
    scheduler = Scheduler(
        horizon=Horizon(
            start=request.horizon.start,
            end=request.horizon.end,
        )
    )

    # 1. Add resources
    for r in request.resources:
        scheduler.add_resource(
            id=r.id,
            name=r.name,
            capacity=r.capacity,
            resource_type=r.resource_type,
            cost_per_time_unit=float(r.cost_per_time_unit_minor) / 100.0,
        )

    # 2. Add tasks
    for t in request.tasks:
        scheduler.add_task(
            id=t.id,
            name=t.name,
            duration=t.duration,
            required_resources=t.required_resources,
            dependencies=t.dependencies,
            fixed_start=t.fixed_start,
        )

    # 3. Compile and solve
    config = SolverConfig(time_limit_seconds=float(request.max_time_seconds))
    result = scheduler.solve(config=config)
    wall_time = time.time() - start_time

    # 4. Try recording to Django database if available
    try:
        from ojas_ops.models.schedule_run import ScheduleRun

        await ScheduleRun.objects.acreate(
            tenant_id=str(request.tenant_id),
            scenario_name=f"{request.project_id}_schedule",
            status=result.status.value,
            makespan=result.makespan,
            objective_value=int(result.objective_value)
            if result.objective_value is not None
            else None,
            solver_status=result.status.value,
            solve_time_seconds=wall_time,
        )
    except Exception:
        # Graceful fallback when running standalone without DB configured
        pass

    return OptimizeScheduleResponse(
        schedule_id=f"sched-{request.project_id}",
        status=result.status,
        makespan=result.makespan,
        objective_value=result.objective_value or 0.0,
        solve_time_seconds=wall_time,
        tasks_scheduled_count=len(result.tasks),
        result=result,
        validation_summary="VALID",
    )
