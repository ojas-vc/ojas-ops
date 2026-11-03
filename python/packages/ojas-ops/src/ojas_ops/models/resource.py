"""Resource models representing people, equipment, locations, and facilities."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from enum import StrEnum

import msgspec

from ojas_ops.models.time import IntervalWindow


class ResourceType(StrEnum):
    PERSON = "person"
    MACHINE = "machine"
    LOCATION = "location"
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    CHANNEL = "channel"


class Resource(msgspec.Struct, kw_only=True):
    """An entity required to execute tasks."""

    id: str
    name: str = ""
    capacity: int = 1
    resource_type: ResourceType = ResourceType.MACHINE
    cost_per_time_unit: float = 0.0
    overtime_cost_per_time_unit: float = 0.0
    regular_capacity_limit: int | None = None
    skills: list[str] = msgspec.field(default_factory=list)
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)
    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            msg = f"Resource '{self.id}' capacity must be positive, got {self.capacity}"
            raise ValueError(msg)
        if not self.name:
            self.name = self.id

    def is_available_during(self, start: int, end: int) -> bool:
        """Check if resource is free from blackout windows during [start, end)."""
        for window in self.blackout_windows:
            if window.hard and window.overlaps(start, end):
                return False
        return True
