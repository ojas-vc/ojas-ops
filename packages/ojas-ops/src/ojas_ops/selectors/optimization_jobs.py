"""Selectors for OptimizationJob records."""

from ojas_ops.models.optimization_job import OptimizationJob


def get_job_by_id(job_id: int) -> OptimizationJob | None:
    """Fetch an OptimizationJob by primary key."""
    return OptimizationJob.objects.filter(id=job_id).first()


async def aget_job_by_id(job_id: int) -> OptimizationJob | None:
    """Fetch an OptimizationJob by primary key asynchronously."""
    return await OptimizationJob.objects.filter(id=job_id).afirst()


def list_jobs_for_tenant(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[OptimizationJob]:
    """List recent optimization jobs for tenant."""
    return list(OptimizationJob.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:limit])


def alist_jobs_for_tenant(
    tenant_id: str = "default",
    limit: int = 50,
):
    """Alias for alist_recent_jobs."""
    return alist_recent_jobs(tenant_id=tenant_id, limit=limit)


def get_job_by_workflow_id(workflow_id: str) -> OptimizationJob | None:
    """Fetch an OptimizationJob by Temporal workflow id."""
    return OptimizationJob.objects.filter(temporal_workflow_id=workflow_id).first()


async def aget_job_by_workflow_id(workflow_id: str) -> OptimizationJob | None:
    """Fetch an OptimizationJob by Temporal workflow id asynchronously."""
    return await OptimizationJob.objects.filter(temporal_workflow_id=workflow_id).afirst()


def list_active_jobs(tenant_id: str = "default") -> list[OptimizationJob]:
    """List currently pending or running optimization jobs."""
    return list(
        OptimizationJob.objects.filter(
            tenant_id=tenant_id,
            status__in=["PENDING", "RUNNING"],
        ).order_by("-created_at")
    )


async def alist_active_jobs(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[OptimizationJob]:
    """List currently pending or running optimization jobs asynchronously."""
    return [
        j
        async for j in OptimizationJob.objects.filter(
            tenant_id=tenant_id,
            status__in=["PENDING", "RUNNING"],
        ).order_by("-created_at")[:limit]
    ]


async def alist_recent_jobs(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[OptimizationJob]:
    """List recent optimization jobs for tenant asynchronously."""
    return [
        j
        async for j in OptimizationJob.objects.filter(
            tenant_id=tenant_id,
        ).order_by("-created_at")[:limit]
    ]
