"""Selectors for OptimizationJob records."""

from ojas_ops.models.optimization_job import OptimizationJob


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
