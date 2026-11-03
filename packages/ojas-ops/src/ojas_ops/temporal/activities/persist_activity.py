"""Temporal activity for persisting solved schedule runs to database."""

from typing import Any

from temporalio import activity

from ojas_ops.schemas.scheduling import OptimizeScheduleResponse


@activity.defn(name="persist_schedule_run_activity")
async def persist_schedule_run_activity(
    response: OptimizeScheduleResponse,
) -> dict[str, Any]:
    """Persists an optimization run outcome to Django database if configured."""
    try:
        from django.conf import settings

        if settings.configured:
            from ojas_ops.models.schedule_run import ScheduleRun

            run = await ScheduleRun.objects.acreate(
                tenant_id="default",
                scenario_name=f"run_{response.schedule_id}",
                status=response.status.value,
                makespan=response.makespan,
                objective_value=int(response.objective_value),
                solver_status=response.status.value,
                solve_time_seconds=response.solve_time_seconds,
                metadata={
                    "tasks_scheduled_count": response.tasks_scheduled_count,
                    "schedule_id": response.schedule_id,
                },
            )
            return {"persisted": True, "schedule_run_id": run.id}
    except Exception as e:
        activity.logger.warning(f"Could not persist schedule run to DB: {e}")

    return {"persisted": False, "schedule_id": response.schedule_id}
