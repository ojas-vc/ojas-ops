"""Selectors for DisruptionLog records."""

from __future__ import annotations

from ojas_ops.models.disruption_log import DisruptionLog


def get_disruption_log_by_id(log_id: int) -> DisruptionLog | None:
    """Fetch a DisruptionLog by primary key."""
    return DisruptionLog.objects.filter(id=log_id).first()


async def aget_disruption_log_by_id(log_id: int) -> DisruptionLog | None:
    """Fetch a DisruptionLog by primary key asynchronously."""
    return await DisruptionLog.objects.filter(id=log_id).afirst()


def list_disruption_logs_for_tenant(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[DisruptionLog]:
    """List recent disruption logs for a tenant."""
    return list(DisruptionLog.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:limit])


async def alist_disruption_logs_for_tenant(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[DisruptionLog]:
    """List recent disruption logs for a tenant asynchronously."""
    return [
        log
        async for log in DisruptionLog.objects.filter(tenant_id=tenant_id).order_by("-created_at")[
            :limit
        ]
    ]


def list_disruption_logs_for_schedule_run(
    schedule_run_id: str,
    tenant_id: str = "default",
) -> list[DisruptionLog]:
    """List disruption logs associated with a specific schedule run."""
    return list(
        DisruptionLog.objects.filter(tenant_id=tenant_id, schedule_run_id=schedule_run_id).order_by(
            "-created_at"
        )
    )


async def alist_disruption_logs_for_schedule_run(
    schedule_run_id: str,
    tenant_id: str = "default",
) -> list[DisruptionLog]:
    """List disruption logs associated with a specific schedule run asynchronously."""
    return [
        log
        async for log in DisruptionLog.objects.filter(
            tenant_id=tenant_id, schedule_run_id=schedule_run_id
        ).order_by("-created_at")
    ]
