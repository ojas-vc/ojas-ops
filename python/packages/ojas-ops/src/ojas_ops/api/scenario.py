"""ModelViewSet for ScenarioRecord benchmarks, synthetic generators, and execution."""

from __future__ import annotations

from typing import Any

from django_bolt import action

from ojas_ops.api.base import BaseOjasModelViewSet
from ojas_ops.models.scenario_record import ScenarioRecord
from ojas_ops.scenarios.generator import (
    generate_film_scenario,
    generate_jobshop_scenario,
    generate_workforce_scenario,
)
from ojas_ops.scenarios.models import ScenarioDefinition
from ojas_ops.scenarios.runner import run_scenario
from ojas_ops.schemas.scenarios import GenerateScenarioRequest, ScenarioExecutionResponse
from ojas_ops.serializers.scenario_record import (
    ScenarioRecordCreateSerializer,
    ScenarioRecordSerializer,
)


class ScenarioModelViewSet(BaseOjasModelViewSet):
    """Full ModelViewSet managing scenario benchmarks, synthetic generation, and execution."""

    queryset = ScenarioRecord.objects.all().order_by("-created_at")
    serializer_class = ScenarioRecordSerializer
    create_serializer_class = ScenarioRecordCreateSerializer
    lookup_field = "id"

    @action(methods=["POST"], detail=False, path="execute")
    async def execute_scenario(
        self,
        request: Any,
        scenario: ScenarioDefinition,
    ) -> ScenarioExecutionResponse:
        """Execute declarative scenario JSON and verify golden expected assertions."""
        run_result = run_scenario(scenario)
        return ScenarioExecutionResponse(
            is_success=run_result.is_success,
            verification_failures=run_result.verification_failures,
            makespan=run_result.result.makespan if run_result.result else None,
            status=run_result.result.status.value if run_result.result else "FAILED",
        )

    @action(methods=["POST"], detail=False, path="generate")
    async def generate_benchmark_scenario(
        self,
        request: Any,
        payload: GenerateScenarioRequest,
    ) -> dict[str, Any]:
        """Generate synthetic benchmark scenario datasets (jobshop, workforce, film)."""
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
