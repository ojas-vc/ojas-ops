"""Canonical framework-agnostic AgentTool interface built with msgspec."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import Any

import msgspec


class AgentTool(msgspec.Struct, kw_only=True):
    """Canonical definition of an operational optimization tool.

    Serves as the single source of truth across Google Antigravity,
    Anthropic Claude, LangChain, CrewAI, and Google ADK.
    """

    name: str
    description: str
    parameters_schema: dict[str, Any]
    fn: Callable[..., Any]
    input_type: type[msgspec.Struct] | None = None
    is_async: bool = False
    capability: str = ""
    provider: str = "ojas-ops"
    tier: str = "core"
    agent_skills: list[str] = msgspec.field(default_factory=list)
    supports: list[str] = msgspec.field(default_factory=list)
    fallback_tools: list[str] = msgspec.field(default_factory=list)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Universal synchronous runner handling dictionaries or stringified JSON payloads."""
        # Unpack single JSON string if passed as first positional arg
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            try:
                decoded = msgspec.json.decode(args[0].encode("utf-8"))
                if isinstance(decoded, dict):
                    kwargs = decoded
            except Exception:
                pass

        # Coerce any stringified JSON values in kwargs
        coerced_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, str) and v.startswith(("{", "[")) and v.endswith(("}", "]")):
                try:
                    coerced_kwargs[k] = msgspec.json.decode(v.encode("utf-8"))
                    continue
                except Exception:
                    pass
            coerced_kwargs[k] = v

        if inspect.iscoroutinefunction(self.fn) or self.is_async:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Running in active loop, return awaitable or run in thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(asyncio.run, self.fn(*args, **coerced_kwargs)).result()
            return asyncio.run(self.fn(*args, **coerced_kwargs))

        return self.fn(*args, **coerced_kwargs)

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        """Universal asynchronous runner."""
        if inspect.iscoroutinefunction(self.fn) or self.is_async:
            return await self.fn(*args, **kwargs)
        return self.fn(*args, **kwargs)

    def to_antigravity(self) -> dict[str, Any]:
        """Project to Google Antigravity tool declaration."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "handler": self.fn,
        }

    def to_anthropic(self) -> dict[str, Any]:
        """Project to Anthropic Claude Messages API specification."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters_schema,
        }

    def to_langchain(self) -> Any:
        """Project to LangChain / LangGraph StructuredTool."""
        from langchain_core.tools import StructuredTool

        return StructuredTool.from_function(
            func=self.fn,
            name=self.name,
            description=self.description,
            args_schema=self.parameters_schema,
        )

    def to_crewai(self) -> Any:
        """Project to CrewAI BaseTool instance."""
        from ojas_ops.agents.providers.crewai import BaseTool

        tool_cls = type(
            f"CrewAI_{self.name.replace('-', '_')}",
            (BaseTool,),
            {
                "name": self.name,
                "description": self.description,
                "args_schema": self.input_type,
                "_run": lambda _self, *a, **kw: self.run(*a, **kw),
            },
        )
        return tool_cls()
