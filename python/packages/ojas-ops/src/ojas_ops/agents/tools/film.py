"""Agent tools for film production optimization, DOOD auditing, and call sheet generation."""

from typing import Any

import msgspec

from ojas_ops.adapters.film_production import (
    ProductionDataset,
    optimize_production_schedule,
)


def optimize_film_shoot(
    dataset_dict: dict[str, Any],
    max_time_seconds: float = 30.0,
    enable_drop_pickup: bool = True,
) -> dict[str, Any]:
    """Optimizes film cross-boarding using pure-integer CP-SAT."""
    data_bytes = msgspec.json.encode(dataset_dict)
    dataset = msgspec.json.decode(data_bytes, type=ProductionDataset)
    result = optimize_production_schedule(
        dataset,
        max_time_in_seconds=max_time_seconds,
        enable_drop_pickup=enable_drop_pickup,
    )
    return {
        "is_feasible": result.is_feasible,
        "status": result.status.value,
        "total_days": result.stripboard.total_shoot_days if result.stripboard else 0,
        "objective_cost": result.objective_cost,
        "solve_time_seconds": result.solve_time_seconds,
        "scene_assignments": result.scene_day_assignments,
        "dood_summary": [
            {
                "talent_id": r.talent_id,
                "character_name": r.character_name,
                "work_days": r.total_work_days,
                "hold_days": r.total_hold_days,
            }
            for r in result.dood_reports
        ],
    }


def audit_dood(
    dataset_dict: dict[str, Any], max_time_seconds: float = 30.0
) -> list[dict[str, Any]]:
    """Generates Day Out of Days (DOOD) cast utilization audit."""
    solve_res = optimize_film_shoot(dataset_dict, max_time_seconds=max_time_seconds)
    return solve_res.get("dood_summary", [])
