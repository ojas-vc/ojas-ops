"""Selectors for ScenarioRecord records."""

from ojas_ops.models.scenario_record import ScenarioRecord


def get_scenario_record_by_id(record_id: int) -> ScenarioRecord | None:
    """Fetch a ScenarioRecord by primary key."""
    return ScenarioRecord.objects.filter(id=record_id).first()


async def aget_scenario_record_by_id(record_id: int) -> ScenarioRecord | None:
    """Fetch a ScenarioRecord by primary key asynchronously."""
    return await ScenarioRecord.objects.filter(id=record_id).afirst()


def list_scenario_records(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[ScenarioRecord]:
    """List recent scenario records for a tenant."""
    return list(ScenarioRecord.objects.filter(tenant_id=tenant_id).order_by("-created_at")[:limit])


async def alist_scenario_records(
    tenant_id: str = "default",
    limit: int = 50,
) -> list[ScenarioRecord]:
    """List recent scenario records for a tenant asynchronously."""
    return [
        s
        async for s in ScenarioRecord.objects.filter(tenant_id=tenant_id).order_by("-created_at")[
            :limit
        ]
    ]
