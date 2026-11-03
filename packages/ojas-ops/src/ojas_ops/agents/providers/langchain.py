"""LangChain and LangGraph tool bindings for Ojas Ops optimization engine."""

import json
from typing import Any

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop

try:
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, Field

    class FilmToolInput(BaseModel):
        dataset_json: str = Field(..., description="JSON string with scenes, cast, and locations")
        max_time_seconds: float = Field(30.0, description="Max search time in seconds")

    class ManufacturingToolInput(BaseModel):
        operations_json: str = Field(..., description="JSON string with operations")
        machines_json: str = Field(..., description="JSON string with machines")
        time_limit_seconds: float = Field(30.0, description="Max search time in seconds")

    def _film_tool(dataset_json: str, max_time_seconds: float = 30.0) -> str:
        data = json.loads(dataset_json)
        res = optimize_film_shoot(data, max_time_seconds=max_time_seconds)
        return json.dumps(res)

    def _mfg_tool(
        operations_json: str, machines_json: str, time_limit_seconds: float = 30.0
    ) -> str:
        ops = json.loads(operations_json)
        macs = json.loads(machines_json)
        res = optimize_job_shop(ops, macs, time_limit_seconds=time_limit_seconds)
        return json.dumps(res)

    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False


def get_langchain_tools() -> list[Any]:
    """Returns LangChain StructuredTools if langchain_core is installed."""
    if not _LANGCHAIN_AVAILABLE:
        raise ImportError(
            "langchain_core is not installed in the current environment. "
            "Install it with `pip install langchain-core` to use LangChain tools."
        )
    return [
        StructuredTool.from_function(
            func=_film_tool,
            name="optimize_film_schedule",
            description="Solves film cross-boarding schedules using CP-SAT.",
            args_schema=FilmToolInput,
        ),
        StructuredTool.from_function(
            func=_mfg_tool,
            name="optimize_job_shop",
            description="Sequences operations on machines to minimize makespan using CP-SAT.",
            args_schema=ManufacturingToolInput,
        ),
    ]
