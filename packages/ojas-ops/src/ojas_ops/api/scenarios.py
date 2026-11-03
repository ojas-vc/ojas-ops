"""Scenarios execution API router."""

from django_bolt import Router

from ojas_ops.scenarios.models import ScenarioDefinition
from ojas_ops.scenarios.runner import run_scenario

router = Router()


@router.post("/run")
async def execute_scenario(scenario: ScenarioDefinition) -> dict:
    """Execute declarative scenario JSON and verify golden assertions."""
    run_result = run_scenario(scenario)
    return {
        "is_success": run_result.is_success,
        "verification_failures": run_result.verification_failures,
        "makespan": run_result.result.makespan if run_result.result else None,
        "status": run_result.result.status.value if run_result.result else "FAILED",
    }
