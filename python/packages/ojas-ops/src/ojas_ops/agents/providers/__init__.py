"""Multi-framework agent tool providers for Ojas Ops."""

from ojas_ops.agents.providers.anthropic import (
    ahandle_claude_tool_call,
    format_claude_tool_result,
    get_anthropic_client,
    get_async_anthropic_client,
    get_claude_tool_definitions,
    handle_claude_tool_call,
)
from ojas_ops.agents.providers.antigravity import (
    get_antigravity_tools,
    require_antigravity_api_key,
)
from ojas_ops.agents.providers.crewai import (
    BaseTool,
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

__all__ = [
    "BaseTool",
    "ahandle_claude_tool_call",
    "format_claude_tool_result",
    "get_anthropic_client",
    "get_antigravity_tools",
    "get_async_anthropic_client",
    "get_claude_tool_definitions",
    "get_crewai_tools",
    "get_langchain_tools",
    "handle_claude_tool_call",
    "ojas_adk_activity_tool",
    "require_antigravity_api_key",
    "require_crewai_api_key",
    "require_google_adk_api_key",
    "require_langchain_api_key",
]
