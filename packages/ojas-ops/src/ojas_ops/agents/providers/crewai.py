"""CrewAI tool bindings for Ojas Ops optimization engine."""

from __future__ import annotations

from typing import Any

import msgspec

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop


class FilmScheduleInput(msgspec.Struct, kw_only=True):
    """Input parameters for film shooting schedule optimization."""

    dataset_json: str
    max_time_seconds: float = 30.0


class ManufacturingScheduleInput(msgspec.Struct, kw_only=True):
    """Input parameters for manufacturing job shop optimization."""

    operations_json: str
    machines_json: str
    time_limit_seconds: float = 30.0


try:
    from crewai.tools import BaseTool

    class CrewAIFilmOptimizerTool(BaseTool):
        name: str = "Film Shooting Schedule Optimizer"
        description: str = "Optimizes film cross-boarding using pure-integer CP-SAT."
        args_schema: type[Any] = FilmScheduleInput

        def _run(self, dataset_json: str, max_time_seconds: float = 30.0) -> str:
            data = (
                msgspec.json.decode(dataset_json.encode("utf-8"))
                if isinstance(dataset_json, str)
                else dataset_json
            )
            result = optimize_film_shoot(data, max_time_seconds=max_time_seconds)
            return msgspec.json.encode(result).decode("utf-8")

    class CrewAIManufacturingOptimizerTool(BaseTool):
        name: str = "Manufacturing Job Shop Scheduler"
        description: str = (
            "Sequences operations on machines to minimize makespan and setup changeovers."
        )
        args_schema: type[Any] = ManufacturingScheduleInput

        def _run(
            self, operations_json: str, machines_json: str, time_limit_seconds: float = 30.0
        ) -> str:
            ops = (
                msgspec.json.decode(operations_json.encode("utf-8"))
                if isinstance(operations_json, str)
                else operations_json
            )
            macs = (
                msgspec.json.decode(machines_json.encode("utf-8"))
                if isinstance(machines_json, str)
                else machines_json
            )
            result = optimize_job_shop(ops, macs, time_limit_seconds=time_limit_seconds)
            return msgspec.json.encode(result).decode("utf-8")

    _CREWAI_AVAILABLE = True
except ImportError:
    _CREWAI_AVAILABLE = False
    CrewAIFilmOptimizerTool = None  # type: ignore[assignment,misc]
    CrewAIManufacturingOptimizerTool = None  # type: ignore[assignment,misc]


def get_crewai_tools() -> list[Any]:
    """Returns initialized CrewAI tools if crewai is installed."""
    if not _CREWAI_AVAILABLE:
        raise ImportError(
            "crewai is not installed in the current environment. "
            "Install it with `pip install crewai` to use CrewAI tools."
        )
    return [CrewAIFilmOptimizerTool(), CrewAIManufacturingOptimizerTool()]
