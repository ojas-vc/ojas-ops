"""Google Antigravity SDK tool declarations for Ojas Ops."""

from typing import Any

from ojas_ops.agents.tools.film import optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop
from ojas_ops.agents.tools.validation import verify_schedule_feasibility


def get_antigravity_tools() -> list[dict[str, Any]]:
    """Returns tool schemas compatible with Google Antigravity agent declarations."""
    return [
        {
            "name": "optimize_film_schedule",
            "description": (
                "Solves a combinatorial film shooting schedule using Google OR-Tools CP-SAT. "
                "Enforces SAG-AFTRA 10-day drop-and-pickup, continuous soundstage leases, "
                "multi-unit concurrency, and location setup minimization."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dataset_dict": {
                        "type": "object",
                        "description": "JSON object defining scenes, talents, locations, and shoot calendar.",
                    },
                    "max_time_seconds": {
                        "type": "number",
                        "description": "Maximum solver search duration in seconds (default 30.0).",
                        "default": 30.0,
                    },
                    "enable_drop_pickup": {
                        "type": "boolean",
                        "description": "Enforce SAG-AFTRA 10-day drop-and-pickup rule.",
                        "default": True,
                    },
                },
                "required": ["dataset_dict"],
            },
            "handler": optimize_film_shoot,
        },
        {
            "name": "optimize_job_shop",
            "description": (
                "Solves a discrete manufacturing job-shop schedule with machine capacity constraints "
                "and setup minimization using CP-SAT."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of operations with duration and machine requirements.",
                    },
                    "machines": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of available machines and hourly rates.",
                    },
                    "time_limit_seconds": {
                        "type": "number",
                        "default": 30.0,
                    },
                },
                "required": ["operations", "machines"],
            },
            "handler": optimize_job_shop,
        },
        {
            "name": "verify_schedule_feasibility",
            "description": "Deterministically validates schedule constraints without solver dependencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "schedule_id": {"type": "string"},
                    "tasks": {"type": "array", "items": {"type": "object"}},
                    "resources": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["schedule_id"],
            },
            "handler": verify_schedule_feasibility,
        },
    ]
