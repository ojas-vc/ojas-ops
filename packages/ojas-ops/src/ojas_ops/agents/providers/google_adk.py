"""Google Agent Development Kit (ADK) integration with Temporal activity tools."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

try:
    from temporalio.contrib.google_adk_agents.workflow import (
        activity_tool as _upstream_activity_tool,
    )
    from temporalio.exceptions import ActivityError

    _ADK_AVAILABLE = True
except Exception:
    _ADK_AVAILABLE = False
    _upstream_activity_tool = None
    ActivityError = Exception


def ojas_adk_activity_tool(activity_def: Callable, **kwargs: Any) -> Callable:
    """Wrap a Temporal Activity as a Google ADK Tool with graceful failure."""
    if _ADK_AVAILABLE and _upstream_activity_tool is not None:
        inner = _upstream_activity_tool(activity_def, **kwargs)

        async def wrapper(*args: Any, **kw: Any):
            try:
                return await inner(*args, **kw)
            except ActivityError as e:
                return f"OPTIMIZATION_ERROR: {activity_def.__name__} failed: {e}. Revise constraints and retry."

        wrapper.__name__ = activity_def.__name__
        wrapper.__doc__ = activity_def.__doc__
        wrapper.__annotations__ = dict(getattr(activity_def, "__annotations__", {}))
        wrapper.__signature__ = inspect.signature(activity_def)
        return wrapper

    # Fallback when temporal google_adk extra is not installed
    async def fallback_wrapper(*args: Any, **kw: Any):
        try:
            return await activity_def(*args, **kw)
        except Exception as e:
            return f"OPTIMIZATION_ERROR: {activity_def.__name__} failed: {e}"

    fallback_wrapper.__name__ = activity_def.__name__
    fallback_wrapper.__doc__ = activity_def.__doc__
    fallback_wrapper.__annotations__ = dict(getattr(activity_def, "__annotations__", {}))
    fallback_wrapper.__signature__ = inspect.signature(activity_def)
    return fallback_wrapper
