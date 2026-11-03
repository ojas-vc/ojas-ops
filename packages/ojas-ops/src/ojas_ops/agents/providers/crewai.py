"""CrewAI tool bindings for Ojas Ops optimization engine."""

import json
from typing import Any

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop

try:
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field

    class FilmScheduleInput(BaseModel):
        dataset_json: str = Field(
            ..., description="JSON string containing scenes, cast, and locations"
        )
        max_time_seconds: float = Field(30.0, description="Solver time limit in seconds")

    class CrewAIFilmOptimizerTool(BaseTool):
        name: str = "Film Shooting Schedule Optimizer"
        description: str = "Optimizes film cross-boarding using pure-integer CP-SAT."
        args_schema: type[BaseModel] = FilmScheduleInput

        def _run(self, dataset_json: str, max_time_seconds: float = 30.0) -> str:
            data = json.loads(dataset_json)
            result = optimize_film_shoot(data, max_time_seconds=max_time_seconds)
            return json.dumps(result)

    class ManufacturingScheduleInput(BaseModel):
        operations_json: str = Field(..., description="JSON string of operations")
        machines_json: str = Field(..., description="JSON string of machines")
        time_limit_seconds: float = Field(30.0, description="Solver time limit in seconds")

    class CrewAIManufacturingOptimizerTool(BaseTool):
        name: str = "Manufacturing Job Shop Scheduler"
        description: str = (
            "Sequences operations on machines to minimize makespan and setup changeovers."
        )
        args_schema: type[BaseModel] = ManufacturingScheduleInput

        def _run(
            self, operations_json: str, machines_json: str, time_limit_seconds: float = 30.0
        ) -> str:
            ops = json.loads(operations_json)
            macs = json.loads(machines_json)
            result = optimize_job_shop(ops, macs, time_limit_seconds=time_limit_seconds)
            return json.dumps(result)

    _CREWAI_AVAILABLE = True
except ImportError:
    _CREWAI_AVAILABLE = False
    CrewAIFilmOptimizerTool = None  # type: ignore
    CrewAIManufacturingOptimizerTool = None  # type: ignore


def get_crewai_tools() -> list[Any]:
    """Returns initialized CrewAI tools if crewai is installed."""
    if not _CREWAI_AVAILABLE:
        raise ImportError(
            "crewai is not installed in the current environment. "
            "Install it with `pip install crewai` to use CrewAI tools."
        )
    return [CrewAIFilmOptimizerTool(), CrewAIManufacturingOptimizerTool()]
