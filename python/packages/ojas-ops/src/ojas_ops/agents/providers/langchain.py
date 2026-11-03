"""LangChain and LangGraph tool bindings for Ojas Ops optimization engine."""

from __future__ import annotations

from langchain_core.tools import StructuredTool

from ojas_ops.agents.security import require_api_key
from ojas_ops.agents.tools.registry import default_tool_registry


def get_langchain_tools() -> list[StructuredTool]:
    """Returns canonical LangChain StructuredTools from default tool registry."""
    return default_tool_registry.get_langchain_tools()


def require_langchain_api_key(provider: str = "openai") -> str:
    """Verifies that the appropriate LLM API key for LangChain is set in environment or .env."""
    if provider.lower() in ("anthropic", "claude"):
        return require_api_key("ANTHROPIC_API_KEY", "LangChain (Anthropic)")
    elif provider.lower() in ("google", "gemini"):
        return require_api_key("GEMINI_API_KEY", "LangChain (Google)")
    return require_api_key("OPENAI_API_KEY", "LangChain (OpenAI)")
