"""Multi-Framework AI Agent Tool Harness for Ojas Ops."""

from ojas_ops.agents.elicitation import (
    FILM_EXTRACTION_SYSTEM_PROMPT,
    JOB_SHOP_EXTRACTION_SYSTEM_PROMPT,
)
from ojas_ops.agents.providers import (
    format_claude_tool_result,
    get_antigravity_tools,
    get_claude_tool_definitions,
    get_crewai_tools,
    get_langchain_tools,
    handle_claude_tool_call,
    ojas_adk_activity_tool,
)
from ojas_ops.agents.tools import (
    audit_dood,
    optimize_film_shoot,
    optimize_job_shop,
    simulate_schedule_delay,
    verify_schedule_feasibility,
)

__all__ = [
    "FILM_EXTRACTION_SYSTEM_PROMPT",
    "JOB_SHOP_EXTRACTION_SYSTEM_PROMPT",
    "audit_dood",
    "format_claude_tool_result",
    "get_antigravity_tools",
    "get_claude_tool_definitions",
    "get_crewai_tools",
    "get_langchain_tools",
    "handle_claude_tool_call",
    "ojas_adk_activity_tool",
    "optimize_film_shoot",
    "optimize_job_shop",
    "simulate_schedule_delay",
    "verify_schedule_feasibility",
]
