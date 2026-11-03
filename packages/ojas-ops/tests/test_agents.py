"""Tests for multi-framework AI Agent Tool Harness."""

import asyncio

import pytest
from ojas_ops.agents.elicitation import (
    FILM_EXTRACTION_SYSTEM_PROMPT,
    JOB_SHOP_EXTRACTION_SYSTEM_PROMPT,
)
from ojas_ops.agents.providers.anthropic import (
    format_claude_tool_result,
    get_anthropic_client,
    get_claude_tool_definitions,
    handle_claude_tool_call,
)
from ojas_ops.agents.providers.antigravity import (
    get_antigravity_tools,
    require_antigravity_api_key,
)
from ojas_ops.agents.providers.crewai import (
    get_crewai_tools,
    require_crewai_api_key,
)
from ojas_ops.agents.providers.google_adk import (
    ojas_adk_activity_tool,
    require_google_adk_api_key,
)
from ojas_ops.agents.providers.langchain import (
    get_langchain_tools,
    require_langchain_api_key,
)
from ojas_ops.agents.security import MissingAPIKeyError, require_api_key
from ojas_ops.agents.tools import (
    AgentTool,
    audit_dood,
    default_tool_registry,
    optimize_job_shop,
)

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


def test_canonical_agent_tool_and_registry():
    """Verify ToolRegistry and canonical AgentTool execution with dict and string inputs."""
    assert len(default_tool_registry.all()) == 5
    film_tool = default_tool_registry.get("optimize_film_schedule")
    assert isinstance(film_tool, AgentTool)
    assert film_tool.name == "optimize_film_schedule"

    # Test execution with dict kwargs
    res_dict = film_tool.run(dataset_dict=SAMPLE_FILM_DATASET, max_time_seconds=3.0)
    assert res_dict["is_feasible"] is True

    # Test execution with stringified JSON kwargs
    import msgspec

    json_str = msgspec.json.encode(SAMPLE_FILM_DATASET).decode("utf-8")
    res_json = film_tool.run(dataset_dict=json_str, max_time_seconds=3.0)
    assert res_json["is_feasible"] is True


def test_antigravity_tools_schema_and_execution():
    """Verify Antigravity tool declarations from canonical registry."""
    tools = get_antigravity_tools()
    assert len(tools) == 5
    tool_names = [t["name"] for t in tools]
    assert "optimize_film_schedule" in tool_names
    assert "audit_dood" in tool_names
    assert "optimize_job_shop" in tool_names
    assert "simulate_schedule_delay" in tool_names
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
    """Verify Anthropic Claude specifications and dispatch via canonical registry."""
    tool_defs = get_claude_tool_definitions()
    assert len(tool_defs) == 5
    tool_names = [t["name"] for t in tool_defs]
    assert "optimize_film_schedule" in tool_names
    assert "audit_dood" in tool_names
    assert "optimize_job_shop" in tool_names
    assert "simulate_schedule_delay" in tool_names
    assert "verify_schedule_feasibility" in tool_names

    # Test result formatting
    formatted = format_claude_tool_result("tool_use_999", {"makespan": 120})
    assert formatted["type"] == "tool_result"
    assert formatted["tool_use_id"] == "tool_use_999"
    assert "120" in formatted["content"]
    assert formatted["is_error"] is False

    # Test handle_claude_tool_call
    res = handle_claude_tool_call(
        "optimize_film_schedule",
        {"dataset_dict": SAMPLE_FILM_DATASET, "max_time_seconds": 5.0},
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


def test_crewai_provider_tools():
    """Verify CrewAI tool bindings from canonical registry."""
    tools = get_crewai_tools()
    assert len(tools) == 5
    tool_names = [t.name for t in tools]
    assert "optimize_film_schedule" in tool_names
    assert "optimize_job_shop" in tool_names

    mfg_tool = next(t for t in tools if t.name == "optimize_job_shop")
    ops = [{"id": "OP1", "machine_id": "M1", "duration_minutes": 20}]
    macs = [{"id": "M1", "hourly_rate": 40.0}]
    res = mfg_tool.run(operations=ops, machines=macs, time_limit_seconds=3.0)
    assert res["is_feasible"] is True


def test_langchain_provider_tools():
    """Verify LangChain tool bindings from canonical registry."""
    tools = get_langchain_tools()
    assert len(tools) == 5
    tool_names = [t.name for t in tools]
    assert "optimize_film_schedule" in tool_names
    assert "audit_dood" in tool_names
    assert "optimize_job_shop" in tool_names

    film_tool = next(t for t in tools if t.name == "optimize_film_schedule")
    res = film_tool.func(dataset_dict=SAMPLE_FILM_DATASET, max_time_seconds=3.0)
    assert res["is_feasible"] is True


def test_runtime_api_key_verification(monkeypatch):
    """Verify lazy runtime API key checks and MissingAPIKeyError."""
    # Ensure key is absent
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(MissingAPIKeyError, match="ANTHROPIC_API_KEY"):
        require_api_key("ANTHROPIC_API_KEY", "Anthropic Claude")

    with pytest.raises(MissingAPIKeyError, match="ANTHROPIC_API_KEY"):
        get_anthropic_client()

    with pytest.raises(MissingAPIKeyError, match="OPENAI_API_KEY"):
        require_crewai_api_key()

    with pytest.raises(MissingAPIKeyError, match="OPENAI_API_KEY"):
        require_langchain_api_key()

    with pytest.raises(MissingAPIKeyError, match="GOOGLE_API_KEY"):
        require_antigravity_api_key()

    with pytest.raises(MissingAPIKeyError, match="GOOGLE_API_KEY"):
        require_google_adk_api_key()

    # Verify success when key is present
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-12345")
    assert require_api_key("ANTHROPIC_API_KEY", "Anthropic Claude") == "sk-ant-test-key-12345"
    client = get_anthropic_client()
    assert client.api_key == "sk-ant-test-key-12345"

    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key")
    assert require_crewai_api_key() == "sk-openai-test-key"
    assert require_langchain_api_key() == "sk-openai-test-key"

    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    assert require_antigravity_api_key() == "gemini-test-key"
    assert require_google_adk_api_key() == "gemini-test-key"
