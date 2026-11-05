"""Real-time event streaming bus for operational projects."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ojas_ops.config import get_projects_dir

# In-memory pub/sub queues per project: (tenant_id, project_id) -> set of asyncio.Queue
_SUBSCRIBERS: dict[tuple[str, str], set[asyncio.Queue]] = defaultdict(set)

# In-memory recent events buffer: (tenant_id, project_id) -> list of events
_RECENT_EVENTS: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
_MAX_BUFFER_SIZE = 500


def _events_file_path(tenant_id: str, project_id: str) -> Path:
    proj_dir = get_projects_dir() / tenant_id / project_id / "logs"
    proj_dir.mkdir(parents=True, exist_ok=True)
    return proj_dir / "events.jsonl"


def emit_project_event(
    tenant_id: str,
    project_id: str,
    event_type: str,
    message: str,
    *,
    stage: Optional[str] = None,
    data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Emit an operational event, writing to event log and notifying SSE subscribers."""
    event_payload: dict[str, Any] = {
        "id": f"evt-{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "project_id": project_id,
        "type": event_type,
        "message": message,
    }
    if stage:
        event_payload["stage"] = stage
    if data:
        event_payload["data"] = data

    key = (tenant_id, project_id)
    # Store in memory
    buf = _RECENT_EVENTS[key]
    buf.append(event_payload)
    if len(buf) > _MAX_BUFFER_SIZE:
        buf.pop(0)

    # Persist to disk asynchronously / best-effort
    try:
        fpath = _events_file_path(tenant_id, project_id)
        with open(fpath, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_payload) + "\n")
    except Exception:
        pass

    # Notify live subscribers
    subscribers = _SUBSCRIBERS.get(key, set())
    for queue in list(subscribers):
        try:
            queue.put_nowait(event_payload)
        except asyncio.QueueFull:
            pass

    return event_payload


def get_project_events(tenant_id: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """Retrieve recent events for a given project."""
    key = (tenant_id, project_id)
    in_mem = _RECENT_EVENTS.get(key, [])
    if in_mem:
        return in_mem[-limit:]

    # Fallback to reading from disk
    fpath = _events_file_path(tenant_id, project_id)
    if not fpath.exists():
        return []

    events = []
    try:
        with open(fpath, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        return events[-limit:]
    except Exception:
        return []


async def subscribe_project_events(
    tenant_id: str, project_id: str
) -> AsyncGenerator[dict[str, Any], None]:
    """Async generator yielding real-time events for SSE streaming."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    key = (tenant_id, project_id)
    _SUBSCRIBERS[key].add(queue)

    # Send historical events first
    for ev in get_project_events(tenant_id, project_id, limit=20):
        yield ev

    try:
        while True:
            event = await queue.get()
            yield event
    finally:
        _SUBSCRIBERS[key].discard(queue)
