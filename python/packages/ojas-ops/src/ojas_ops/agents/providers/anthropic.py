"""Anthropic Claude tool specifications and conversation message helpers for Ojas Ops."""

from __future__ import annotations

from typing import Any

import anthropic
import msgspec

from ojas_ops.agents.security import require_api_key
from ojas_ops.agents.tools.registry import default_tool_registry


def get_claude_tool_definitions() -> list[dict[str, Any]]:
    """Returns canonical tool specifications matching Anthropic Claude Messages API schema."""
    return default_tool_registry.get_anthropic_tools()


def format_claude_tool_result(
    tool_use_id: str,
    content: Any,
    is_error: bool = False,
) -> dict[str, Any]:
    """Formats solver result into an Anthropic tool_result message block."""
    text_content = (
        msgspec.json.encode(content).decode("utf-8") if not isinstance(content, str) else content
    )
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": text_content,
        "is_error": is_error,
    }


def handle_claude_tool_call(tool_name: str, tool_input: dict[str, Any]) -> Any:
    """Dispatches Claude tool call to the appropriate ojas-ops engine via default registry."""
    return default_tool_registry.dispatch(tool_name, **tool_input)


async def ahandle_claude_tool_call(tool_name: str, tool_input: dict[str, Any]) -> Any:
    """Dispatches Claude tool call asynchronously to the appropriate ojas-ops engine."""
    return await default_tool_registry.adispatch(tool_name, **tool_input)


def get_anthropic_client(api_key: str | None = None) -> anthropic.Anthropic:
    """Instantiates an Anthropic client, checking .env or environment for ANTHROPIC_API_KEY."""
    key = api_key or require_api_key("ANTHROPIC_API_KEY", "Anthropic Claude")
    return anthropic.Anthropic(api_key=key)


def get_async_anthropic_client(api_key: str | None = None) -> anthropic.AsyncAnthropic:
    """Instantiates an asynchronous Anthropic client, checking .env or environment for ANTHROPIC_API_KEY."""
    key = api_key or require_api_key("ANTHROPIC_API_KEY", "Anthropic Claude")
    return anthropic.AsyncAnthropic(api_key=key)
