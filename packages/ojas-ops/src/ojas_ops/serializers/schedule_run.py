"""Django-Bolt serializers for ScheduleRun records."""

from __future__ import annotations

from typing import Any

from django_bolt.serializers import Serializer


class ScheduleRunSerializer(Serializer):
    """Full serializer for retrieving and updating ScheduleRun records."""

    id: int
    tenant_id: str
    scenario_name: str
    status: str
    makespan: int | None = None
    objective_value: int | None = None
    solver_status: str = "UNKNOWN"
    solve_time_seconds: float = 0.0
    result_json: dict[str, Any] = {}
    metadata: dict[str, Any] = {}


class ScheduleRunCreateSerializer(Serializer):
    """Serializer for creating ScheduleRun records without requiring database-assigned primary key."""

    scenario_name: str
    tenant_id: str = "default"
    status: str = "PENDING"
    makespan: int | None = None
    objective_value: int | None = None
    solver_status: str = "UNKNOWN"
    solve_time_seconds: float = 0.0
    result_json: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
