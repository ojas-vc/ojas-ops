"""CrewAI tool bindings for Ojas Ops optimization engine."""

from __future__ import annotations

from typing import Any

from ojas_ops.agents.security import require_api_key
from ojas_ops.agents.tools.registry import default_tool_registry


class BaseTool:
    """Canonical base class for CrewAI operational tools."""

    name: str = ""
    description: str = ""
    args_schema: Any = None

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def run(self, *args: Any, **kwargs: Any) -> Any:
        return self._run(*args, **kwargs)

    def to_langchain(self) -> Any:
        """Allows seamless consumption by CrewAI's internal LangChain tool parser."""
        from langchain_core.tools import StructuredTool

        return StructuredTool.from_function(
            func=self.run,
            name=self.name,
            description=self.description,
        )


def get_crewai_tools() -> list[Any]:
    """Returns canonical tools formatted for CrewAI from default registry."""
    return default_tool_registry.get_crewai_tools()


def require_crewai_api_key(provider: str = "openai") -> str:
    """Verifies that the appropriate LLM API key for CrewAI is set in environment or .env."""
    if provider.lower() in ("anthropic", "claude"):
        return require_api_key("ANTHROPIC_API_KEY", "CrewAI (Anthropic)")
    return require_api_key("OPENAI_API_KEY", "CrewAI (OpenAI)")
