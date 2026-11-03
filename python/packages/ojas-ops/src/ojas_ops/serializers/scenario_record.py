"""Django-Bolt serializers for ScenarioRecord records."""

from __future__ import annotations

from typing import Any

from django_bolt.serializers import Serializer


class ScenarioRecordSerializer(Serializer):
    """Full serializer for retrieving and updating ScenarioRecord records."""

    id: int
    tenant_id: str
    name: str
    domain: str
    scale: str = "medium"
    definition_json: dict[str, Any] = {}
    benchmark_metrics_json: dict[str, Any] = {}


class ScenarioRecordCreateSerializer(Serializer):
    """Serializer for creating ScenarioRecord records without requiring database-assigned primary key."""

    name: str
    domain: str
    tenant_id: str = "default"
    scale: str = "medium"
    definition_json: dict[str, Any] = {}
    benchmark_metrics_json: dict[str, Any] = {}
