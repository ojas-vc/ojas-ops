"""Django-Bolt serializers for DisruptionLog records."""

from __future__ import annotations

import msgspec
from django_bolt.serializers import Serializer


class DisruptionLogSerializer(Serializer):
    """Full serializer for retrieving and updating DisruptionLog records."""

    id: int
    tenant_id: str
    schedule_run_id: str
    disruption_type: str
    magnitude_minutes: int = 0
    affected_tasks: list[str] = msgspec.field(default_factory=list)
    notes: str = ""


class DisruptionLogCreateSerializer(Serializer):
    """Serializer for creating DisruptionLog records without requiring database-assigned primary key."""

    schedule_run_id: str
    disruption_type: str
    tenant_id: str = "default"
    magnitude_minutes: int = 0
    affected_tasks: list[str] = msgspec.field(default_factory=list)
    notes: str = ""
