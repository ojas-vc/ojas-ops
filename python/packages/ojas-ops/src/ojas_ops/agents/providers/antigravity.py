"""Google Antigravity SDK tool declarations for Ojas Ops."""

from __future__ import annotations

from typing import Any

from ojas_ops.agents.security import MissingAPIKeyError, require_api_key
from ojas_ops.agents.tools.registry import default_tool_registry


def get_antigravity_tools() -> list[dict[str, Any]]:
    """Returns tool schemas compatible with Google Antigravity agent declarations."""
    return default_tool_registry.get_antigravity_tools()


def require_antigravity_api_key() -> str:
    """Verifies that GEMINI_API_KEY or GOOGLE_API_KEY is configured for Antigravity."""
    try:
        return require_api_key("GEMINI_API_KEY", "Google Antigravity")
    except MissingAPIKeyError:
        return require_api_key("GOOGLE_API_KEY", "Google Antigravity")
