"""LangChain and LangGraph tool bindings for Ojas Ops optimization engine."""

from __future__ import annotations

from typing import Any

import msgspec

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop


class FilmToolInput(msgspec.Struct, kw_only=True):
    """Input parameters for film shooting schedule optimization."""

    dataset_json: str
    max_time_seconds: float = 30.0


class ManufacturingToolInput(msgspec.Struct, kw_only=True):
    """Input parameters for manufacturing job shop optimization."""

    operations_json: str
    machines_json: str
    time_limit_seconds: float = 30.0


def _film_tool(dataset_json: str, max_time_seconds: float = 30.0) -> str:
    data = (
        msgspec.json.decode(dataset_json.encode("utf-8"))
        if isinstance(dataset_json, str)
        else dataset_json
    )
    res = optimize_film_shoot(data, max_time_seconds=max_time_seconds)
    return msgspec.json.encode(res).decode("utf-8")


def _mfg_tool(operations_json: str, machines_json: str, time_limit_seconds: float = 30.0) -> str:
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
    res = optimize_job_shop(ops, macs, time_limit_seconds=time_limit_seconds)
    return msgspec.json.encode(res).decode("utf-8")


try:
    from langchain_core.tools import StructuredTool

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
