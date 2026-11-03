"""Operational disruption models for what-if simulation and reactive rescheduling."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from enum import StrEnum

import msgspec

from ojas_ops.models.task import Task


class DisruptionType(StrEnum):
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    TASK_DELAYED = "task_delayed"
    TASK_DURATION_INCREASED = "task_duration_increased"
    TASK_ADDED = "task_added"
    TASK_CANCELLED = "task_cancelled"
    CALENDAR_SHIFT = "calendar_shift"
    CAPACITY_REDUCED = "capacity_reduced"


class Disruption(msgspec.Struct, kw_only=True):
    """Specification of an operational disturbance, delay, outage, or schedule change."""

    type: DisruptionType
    resource_id: str | None = None
    task_id: str | None = None
    start: int | None = None
    end: int | None = None
    delta: int = 0
    description: str = ""
    new_task: Task | None = None
