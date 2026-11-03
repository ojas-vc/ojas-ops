"""Django-Bolt Serializer definitions for Ojas Ops models."""

from typing import Any

from django_bolt.serializers import Serializer


# --- ScheduleRun ---
class ScheduleRunSerializer(Serializer):
    """Full serializer for ScheduleRun records."""

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
    """Serializer for creating/updating ScheduleRun records."""

    scenario_name: str
    tenant_id: str = "default"
    status: str = "PENDING"
    makespan: int | None = None
    objective_value: int | None = None
    solver_status: str = "UNKNOWN"
    solve_time_seconds: float = 0.0
    result_json: dict[str, Any] = {}
    metadata: dict[str, Any] = {}


# --- OptimizationJob ---
class OptimizationJobSerializer(Serializer):
    """Full serializer for OptimizationJob records."""

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
    """Serializer for creating/updating OptimizationJob records."""

    temporal_workflow_id: str
    tenant_id: str = "default"
    task_queue: str = "ojas-ops-workflows"
    status: str = "PENDING"
    progress_basis_points: int = 0
    incumbent_objective: int | None = None
    best_bound: int | None = None
    solve_time_seconds: float = 0.0


# --- ScenarioRecord ---
class ScenarioRecordSerializer(Serializer):
    """Full serializer for ScenarioRecord records."""

    id: int
    tenant_id: str
    name: str
    domain: str
    scale: str = "medium"
    definition_json: dict[str, Any] = {}
    benchmark_metrics_json: dict[str, Any] = {}


class ScenarioRecordCreateSerializer(Serializer):
    """Serializer for creating/updating ScenarioRecord records."""

    name: str
    domain: str
    tenant_id: str = "default"
    scale: str = "medium"
    definition_json: dict[str, Any] = {}
    benchmark_metrics_json: dict[str, Any] = {}


# --- DisruptionLog ---
class DisruptionLogSerializer(Serializer):
    """Full serializer for DisruptionLog records."""

    id: int
    tenant_id: str
    schedule_run_id: str
    disruption_type: str
    magnitude_minutes: int = 0
    affected_tasks: list[str] = []
    notes: str = ""


class DisruptionLogCreateSerializer(Serializer):
    """Serializer for creating/updating DisruptionLog records."""

    schedule_run_id: str
    disruption_type: str
    tenant_id: str = "default"
    magnitude_minutes: int = 0
    affected_tasks: list[str] = []
    notes: str = ""
