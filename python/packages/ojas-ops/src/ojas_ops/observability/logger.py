"""Structured JSON logging with correlation contexts."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """Custom logging formatter outputting single-line JSON with correlation fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include standard context fields if attached to the record
        for field in (
            "trace_id",
            "tenant_id",
            "project_id",
            "pipeline",
            "stage",
            "tool",
            "duration_ms",
            "solver_status",
            "makespan",
            "tokens_used",
        ):
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter injecting correlation identifiers into structured records."""

    def process(self, msg: Any, kwargs: Any) -> tuple[Any, Any]:
        extra = kwargs.setdefault("extra", {})
        if self.extra:
            extra.update(self.extra)
        return msg, kwargs


def get_structured_logger(
    name: str = "ojas_ops",
    *,
    tenant_id: Optional[str] = None,
    project_id: Optional[str] = None,
    pipeline: Optional[str] = None,
    stage: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> StructuredLoggerAdapter:
    """Retrieve a structured logger instance bound with context metadata."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    context = {
        k: v
        for k, v in {
            "tenant_id": tenant_id,
            "project_id": project_id,
            "pipeline": pipeline,
            "stage": stage,
            "trace_id": trace_id,
        }.items()
        if v is not None
    }
    return StructuredLoggerAdapter(logger, context)
