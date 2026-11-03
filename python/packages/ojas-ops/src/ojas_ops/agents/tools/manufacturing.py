"""Agent tools for manufacturing and job shop scheduling optimization."""

from typing import Any

from ojas_ops.adapters.manufacturing import ManufacturingScheduler


def optimize_job_shop(
    operations: list[dict[str, Any]],
    machines: list[dict[str, Any]],
    time_limit_seconds: float = 30.0,
) -> dict[str, Any]:
    """Optimizes discrete machine sequencing and setup minimization for manufacturing operations."""
    mfg = ManufacturingScheduler()
    for m in machines:
        mfg.add_machine(
            m["id"],
            name=m.get("name", m["id"]),
            hourly_rate_cents=m.get("hourly_rate_cents", int(m.get("hourly_rate", 50.0) * 100)),
        )

    jobs_added = set()
    for op in operations:
        job_id = op.get("job_id", "default_job")
        if job_id not in jobs_added:
            mfg.add_job(job_id, name=job_id)
            jobs_added.add(job_id)

        mfg.add_operation(
            job_id,
            op["id"],
            op["machine_id"],
            duration_minutes=op["duration_minutes"],
            product_family=op.get("family", "default"),
        )

    from ojas_ops.solvers.config import SolverConfig

    scheduler = mfg.build_scheduler()
    config = SolverConfig(time_limit_seconds=time_limit_seconds)
    result = scheduler.solve(config=config)
    return {
        "is_feasible": result.is_feasible,
        "status": result.status.value,
        "makespan_minutes": result.makespan,
        "total_cost": result.objective_value,
        "solve_time_seconds": result.solve_time_seconds,
        "schedule": [
            {
                "task_id": t.task_id,
                "start": t.start,
                "end": t.end,
                "resource": t.assigned_resources[0] if t.assigned_resources else None,
            }
            for t in result.tasks.values()
        ],
    }
