"""Class-Based ViewSet for Scenarios execution and synthetic benchmark generation."""

from typing import Any

import msgspec
from django_bolt import ViewSet, action

from ojas_ops.scenarios.generator import (
    generate_film_scenario,
    generate_jobshop_scenario,
    generate_workforce_scenario,
)
from ojas_ops.scenarios.models import ScenarioDefinition
from ojas_ops.scenarios.runner import run_scenario


class GenerateScenarioRequest(msgspec.Struct, kw_only=True):
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
    # Optional backward-compatible aliases
    num_nurses: int | None = None
    num_days: int | None = None
    num_actors: int | None = None


class ScenarioViewSet(ViewSet):
    """Class-Based ViewSet managing declarative scenario verification and synthetic benchmarking."""

    @action(methods=["POST"], detail=False, path="run")
    async def execute_scenario(
        self,
        request,
        scenario: ScenarioDefinition,
    ) -> dict[str, Any]:
        """Execute declarative scenario JSON and verify golden assertions."""
        run_result = run_scenario(scenario)
        return {
            "is_success": run_result.is_success,
            "verification_failures": run_result.verification_failures,
            "makespan": run_result.result.makespan if run_result.result else None,
            "status": run_result.result.status.value if run_result.result else "FAILED",
        }

    @action(methods=["POST"], detail=False, path="generate")
    async def generate_benchmark_scenario(
        self,
        request,
        payload: GenerateScenarioRequest,
    ) -> dict[str, Any]:
        """Generate a synthetic benchmark scenario (jobshop, workforce, film)."""
        scenario_type = payload.scenario_type.lower()
        seed = payload.seed

        if scenario_type == "jobshop":
            scen = generate_jobshop_scenario(
                num_jobs=payload.num_jobs,
                num_machines=payload.num_machines,
                seed=seed,
            )
        elif scenario_type == "workforce":
            staff_count = (
                payload.num_nurses if payload.num_nurses is not None else payload.num_staff
            )
            hours = payload.num_days * 24 if payload.num_days is not None else payload.horizon_hours
            scen = generate_workforce_scenario(
                num_staff=staff_count,
                num_shifts=payload.num_shifts,
                horizon_hours=hours,
                seed=seed,
            )
        elif scenario_type == "film":
            cast_count = payload.num_actors if payload.num_actors is not None else payload.num_cast
            scen = generate_film_scenario(
                num_scenes=payload.num_scenes,
                num_cast=cast_count,
                num_locations=payload.num_locations,
                seed=seed,
            )
        else:
            return {
                "error": f"Unknown scenario_type: {scenario_type}. Supported: jobshop, workforce, film"
            }

        return {
            "scenario_type": scenario_type,
            "name": scen.metadata.name,
            "domain": scen.metadata.domain,
            "tasks_count": len(scen.tasks),
            "resources_count": len(scen.resources),
            "tasks": [t.id for t in scen.tasks],
            "resources": [r.id for r in scen.resources],
        }
