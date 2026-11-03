"""Anthropic Claude tool specifications and conversation message helpers for Ojas Ops."""

import json
from typing import Any

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop
from ojas_ops.agents.tools.validation import verify_schedule_feasibility


def get_claude_tool_definitions() -> list[dict[str, Any]]:
    """Returns tool specifications matching the Anthropic Claude Messages API schema."""
    return [
        {
            "name": "optimize_film_schedule",
            "description": (
                "Solves a combinatorial film shooting schedule using Google OR-Tools CP-SAT. "
                "Enforces SAG-AFTRA 10-day drop-and-pickup, continuous soundstage leases, "
                "multi-unit concurrency, and location setup minimization."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "dataset_dict": {
                        "type": "object",
                        "description": "Production dataset containing scenes, cast, and locations.",
                    },
                    "max_time_seconds": {
                        "type": "number",
                        "description": "Time limit in seconds.",
                        "default": 30.0,
                    },
                    "enable_drop_pickup": {
                        "type": "boolean",
                        "description": "Whether to enforce SAG-AFTRA 10-day hold drop/pickup rule.",
                        "default": True,
                    },
                },
                "required": ["dataset_dict"],
            },
        },
        {
            "name": "optimize_job_shop",
            "description": "Optimizes discrete manufacturing machine scheduling with setup minimization.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operations": {"type": "array", "items": {"type": "object"}},
                    "machines": {"type": "array", "items": {"type": "object"}},
                    "time_limit_seconds": {"type": "number", "default": 30.0},
                },
                "required": ["operations", "machines"],
            },
        },
        {
            "name": "verify_schedule_feasibility",
            "description": "Performs deterministic validation on candidate schedules without solver dependencies.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "schedule_id": {"type": "string"},
                    "tasks": {"type": "array", "items": {"type": "object"}},
                    "resources": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["schedule_id"],
            },
        },
    ]


def format_claude_tool_result(
    tool_use_id: str,
    content: Any,
    is_error: bool = False,
) -> dict[str, Any]:
    """Formats solver result into an Anthropic tool_result message block."""
    text_content = json.dumps(content) if not isinstance(content, str) else content
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": text_content,
        "is_error": is_error,
    }


async def handle_claude_tool_call(tool_name: str, tool_input: dict[str, Any]) -> Any:
    """Dispatches Claude tool call to the appropriate ojas-ops engine."""
    if tool_name == "optimize_film_schedule":
        return optimize_film_shoot(**tool_input)
    elif tool_name == "optimize_job_shop":
        return optimize_job_shop(**tool_input)
    elif tool_name == "verify_schedule_feasibility":
        return await verify_schedule_feasibility(**tool_input)
    raise ValueError(f"Unknown tool name: {tool_name}")
