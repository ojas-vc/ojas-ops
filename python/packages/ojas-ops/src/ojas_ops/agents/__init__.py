"""Multi-Framework AI Agent Tool Harness for Ojas Ops."""

from ojas_ops.agents.elicitation import (
    FILM_EXTRACTION_SYSTEM_PROMPT,
    JOB_SHOP_EXTRACTION_SYSTEM_PROMPT,
)
from ojas_ops.agents.providers import (
    BaseTool,
    format_claude_tool_result,
    get_anthropic_client,
    get_antigravity_tools,
    get_async_anthropic_client,
    get_claude_tool_definitions,
    get_crewai_tools,
    get_langchain_tools,
    handle_claude_tool_call,
    ojas_adk_activity_tool,
    require_antigravity_api_key,
    require_crewai_api_key,
    require_google_adk_api_key,
    require_langchain_api_key,
)
from ojas_ops.agents.security import MissingAPIKeyError, require_api_key
from ojas_ops.agents.tools import (
    AgentTool,
    ToolRegistry,
    audit_dood,
    default_tool_registry,
    optimize_film_shoot,
    optimize_job_shop,
    simulate_schedule_delay,
    verify_schedule_feasibility,
)

__all__ = [
    "AgentTool",
    "BaseTool",
    "FILM_EXTRACTION_SYSTEM_PROMPT",
    "JOB_SHOP_EXTRACTION_SYSTEM_PROMPT",
    "MissingAPIKeyError",
    "ToolRegistry",
    "audit_dood",
    "default_tool_registry",
    "format_claude_tool_result",
    "get_anthropic_client",
    "get_antigravity_tools",
    "get_async_anthropic_client",
    "get_claude_tool_definitions",
    "get_crewai_tools",
    "get_langchain_tools",
    "handle_claude_tool_call",
    "ojas_adk_activity_tool",
    "optimize_film_shoot",
    "optimize_job_shop",
    "require_antigravity_api_key",
    "require_api_key",
    "require_crewai_api_key",
    "require_google_adk_api_key",
    "require_langchain_api_key",
    "simulate_schedule_delay",
    "verify_schedule_feasibility",
]
