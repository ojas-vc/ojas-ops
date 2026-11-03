"""Scenario benchmark and execution request/response schemas."""

from __future__ import annotations

import msgspec

from ojas_ops.schemas.base import Contract


class GenerateScenarioRequest(Contract, kw_only=True):
    """Parameters to generate a synthetic benchmark scenario."""

    scenario_type: str = "jobshop"
    num_jobs: int = 6
    num_machines: int = 4
    num_staff: int = 10
    num_shifts: int = 24
    horizon_hours: int = 48
    num_scenes: int = 12
    num_cast: int = 6
    num_locations: int = 3
    seed: int = 42
    # Keyword argument aliases for domain flexibility
    num_nurses: int | None = None
    num_days: int | None = None
    num_actors: int | None = None


class ScenarioExecutionResponse(Contract, kw_only=True):
    """Response returned upon declarative scenario execution."""

    is_success: bool
    verification_failures: list[str] = msgspec.field(default_factory=list)
    makespan: int | None = None
    status: str = "FAILED"
