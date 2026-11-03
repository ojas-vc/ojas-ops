"""Selectors for ScheduleRun records."""

from ojas_ops.models.schedule_run import ScheduleRun


def get_schedule_run_by_id(run_id: int) -> ScheduleRun | None:
    """Fetch a ScheduleRun by primary key."""
    return ScheduleRun.objects.filter(id=run_id).first()


def list_schedule_runs_for_tenant(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[ScheduleRun]:
    """List recent schedule runs for a tenant."""
    return list(ScheduleRun.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:limit])
