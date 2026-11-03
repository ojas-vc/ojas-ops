"""Django-Bolt serializers for OptimizationJob records."""

from __future__ import annotations

from django_bolt.serializers import Serializer


class OptimizationJobSerializer(Serializer):
    """Full serializer for retrieving and updating OptimizationJob records."""

    id: int
    tenant_id: str
    temporal_workflow_id: str
    task_queue: str
    status: str
    progress_basis_points: int = 0
    incumbent_objective: int | None = None
    best_bound: int | None = None
    solve_time_seconds: float = 0.0


class OptimizationJobCreateSerializer(Serializer):
    """Serializer for creating OptimizationJob records without requiring database-assigned primary key."""

    temporal_workflow_id: str
    tenant_id: str = "default"
    task_queue: str = "ojas-ops-workflows"
    status: str = "PENDING"
    progress_basis_points: int = 0
    incumbent_objective: int | None = None
    best_bound: int | None = None
    solve_time_seconds: float = 0.0
