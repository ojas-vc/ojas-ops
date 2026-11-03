"""Tests for multi-framework AI Agent Tool Harness."""

import asyncio

from ojas_ops.agents.elicitation import (
    FILM_EXTRACTION_SYSTEM_PROMPT,
    JOB_SHOP_EXTRACTION_SYSTEM_PROMPT,
)
from ojas_ops.agents.providers.anthropic import (
    format_claude_tool_result,
    get_claude_tool_definitions,
    handle_claude_tool_call,
)
from ojas_ops.agents.providers.antigravity import get_antigravity_tools
from ojas_ops.agents.providers.google_adk import ojas_adk_activity_tool
from ojas_ops.agents.tools.film import audit_dood
from ojas_ops.agents.tools.manufacturing import optimize_job_shop

SAMPLE_FILM_DATASET = {
    "project_title": "Agent Unit Test Film",
    "talents": [
        {
            "id": 1,
            "name": "Actor A",
            "character_name": "Hero",
            "daily_rate": 5000.0,
            "is_minor": False,
            "max_daily_hours": 12.0,
            "hmu_duration_minutes": 30,
            "wardrobe_duration_minutes": 15,
            "travel_duration_minutes": 30,
            "blackout_days": [],
        }
    ],
    "locations": [
        {
            "id": 1,
            "name": "Stage 1",
            "location_type": "SOUNDSTAGE",
            "permitted_days": [1, 2, 3],
            "noise_curfew_hour": None,
            "allows_sync_sound": True,
            "daily_rental_cost": 2000.0,
            "prep_days_required": 0,
            "strike_days_required": 0,
        }
    ],
    "props": [],
    "costumes": [],
    "specialty_equipments": [],
    "stunt_packages": [],
    "calendar_days": [
        {"day_number": 1, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 2, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 3, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
    ],
    "production_units": [
        {"id": 1, "name": "Main Unit", "unit_type": "FIRST_UNIT", "max_operating_hours": 12.0}
    ],
    "camera_setups": [],
    "location_travel_matrix": [],
    "max_shooting_days": 3,
    "max_hours_per_day": 12.0,
    "scenes": [
        {
            "id": 1,
            "scene_number": "1",
            "script_day": 1,
            "pages_eighths": 16,
            "setting": "INT",
            "time_of_day": "DAY",
            "location_id": 1,
            "required_talent_ids": [1],
            "required_prop_ids": [],
            "required_costume_ids": [],
            "required_equipment_ids": [],
            "stunt_package_id": None,
            "camera_setup_ids": [],
            "preferred_unit": "FIRST_UNIT",
            "weather_requirement": "ANY",
            "sound_recording": "SYNC_SOUND",
            "estimated_minutes": 120,
            "sequence_dependent_setup_minutes": 15,
            "is_locked": False,
            "locked_day": None,
            "earliest_day": 1,
            "latest_day": 3,
        }
    ],
}


def test_antigravity_tools_schema_and_execution():
    tools = get_antigravity_tools()
    assert len(tools) == 3
    tool_names = [t["name"] for t in tools]
    assert "optimize_film_schedule" in tool_names
    assert "optimize_job_shop" in tool_names
    assert "verify_schedule_feasibility" in tool_names

    # Test executing film schedule tool handler
    film_handler = next(t["handler"] for t in tools if t["name"] == "optimize_film_schedule")
    res = film_handler(dataset_dict=SAMPLE_FILM_DATASET, max_time_seconds=5.0)
    assert res["is_feasible"] is True
    assert res["total_days"] >= 1
    assert "dood_summary" in res

    # Test audit_dood
    dood = audit_dood(SAMPLE_FILM_DATASET, max_time_seconds=5.0)
    assert len(dood) == 1
    assert dood[0]["character_name"] == "Hero"


def test_manufacturing_tool_execution():
    ops = [
        {"id": "OP1", "machine_id": "M1", "duration_minutes": 30},
        {"id": "OP2", "machine_id": "M1", "duration_minutes": 45, "predecessors": ["OP1"]},
    ]
    machines = [{"id": "M1", "name": "Lathe", "hourly_rate": 60.0}]

    res = optimize_job_shop(operations=ops, machines=machines, time_limit_seconds=5.0)
    assert res["is_feasible"] is True
    assert res["makespan_minutes"] == 75
    assert len(res["schedule"]) == 2


def test_anthropic_claude_tools():
    tool_defs = get_claude_tool_definitions()
    assert len(tool_defs) == 3
    assert tool_defs[0]["name"] == "optimize_film_schedule"

    # Test result formatting
    formatted = format_claude_tool_result("tool_use_999", {"makespan": 120})
    assert formatted["type"] == "tool_result"
    assert formatted["tool_use_id"] == "tool_use_999"
    assert '"makespan": 120' in formatted["content"]
    assert formatted["is_error"] is False

    # Test handle_claude_tool_call
    res = asyncio.run(
        handle_claude_tool_call(
            "optimize_film_schedule",
            {"dataset_dict": SAMPLE_FILM_DATASET, "max_time_seconds": 5.0},
        )
    )
    assert res["is_feasible"] is True


def test_google_adk_activity_tool():
    async def sample_activity(val: int) -> int:
        return val * 2

    adk_tool = ojas_adk_activity_tool(sample_activity)
    res = asyncio.run(adk_tool(21))
    assert res == 42


def test_elicitation_prompts():
    assert "ProductionDataset" in FILM_EXTRACTION_SYSTEM_PROMPT
    assert "operations" in JOB_SHOP_EXTRACTION_SYSTEM_PROMPT


def test_crewai_provider_msgspec_structs():
    import pytest
    from ojas_ops.agents.providers.crewai import (
        FilmScheduleInput,
        ManufacturingScheduleInput,
        get_crewai_tools,
    )

    film_inp = FilmScheduleInput(dataset_json="{}", max_time_seconds=15.0)
    assert film_inp.max_time_seconds == 15.0

    mfg_inp = ManufacturingScheduleInput(operations_json="[]", machines_json="[]")
    assert mfg_inp.time_limit_seconds == 30.0

    with pytest.raises(ImportError, match="crewai is not installed"):
        get_crewai_tools()


def test_langchain_provider_msgspec_structs():
    import msgspec
    import pytest
    from ojas_ops.agents.providers.langchain import (
        FilmToolInput,
        ManufacturingToolInput,
        _mfg_tool,
        get_langchain_tools,
    )

    film_inp = FilmToolInput(dataset_json="{}", max_time_seconds=20.0)
    assert film_inp.max_time_seconds == 20.0

    mfg_inp = ManufacturingToolInput(operations_json="[]", machines_json="[]")
    assert mfg_inp.time_limit_seconds == 30.0

    # Verify msgspec serialization in _mfg_tool
    ops_json = msgspec.json.encode(
        [{"id": "OP1", "machine_id": "M1", "duration_minutes": 30}]
    ).decode("utf-8")
    macs_json = msgspec.json.encode([{"id": "M1", "hourly_rate": 50.0}]).decode("utf-8")
    res_str = _mfg_tool(ops_json, macs_json, time_limit_seconds=3.0)
    res = msgspec.json.decode(res_str.encode("utf-8"))
    assert res["is_feasible"] is True

    with pytest.raises(ImportError, match="langchain_core is not installed"):
        get_langchain_tools()
