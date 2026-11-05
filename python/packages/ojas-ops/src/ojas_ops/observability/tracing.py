"""OpenTelemetry distributed tracing seam for Ojas Ops."""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Generator
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.trace import Tracer

    _TRACING_AVAILABLE = True
except ImportError:
    _TRACING_AVAILABLE = False
    trace = None  # type: ignore[assignment]
    Tracer = Any  # type: ignore[assignment,misc]


def get_tracer(name: str = "ojas_ops") -> Any:
    """Retrieve an OpenTelemetry tracer instance or dummy tracer."""
    if _TRACING_AVAILABLE and trace is not None:
        return trace.get_tracer(name)
    return None


@contextlib.contextmanager
def trace_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
    tracer_name: str = "ojas_ops",
) -> Generator[Any, None, None]:
    """Context manager yielding an active trace span, safe even when OpenTelemetry is inactive."""
    if _TRACING_AVAILABLE and trace is not None:
        tracer = trace.get_tracer(tracer_name)
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for k, v in attributes.items():
                    if v is not None:
                        span.set_attribute(k, str(v) if not isinstance(v, (int, float, bool)) else v)
            yield span
    else:
        yield None

