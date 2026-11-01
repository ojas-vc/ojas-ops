"""Calendar events and operational temporal windows."""

from __future__ import annotations

from enum import StrEnum

import msgspec

from ojas_ops.models.time import IntervalWindow


class CalendarKind(StrEnum):
    OPERATIONAL = "operational"
    SHIFT = "shift"
    MAINTENANCE = "maintenance"
    HOLIDAY = "holiday"
    AUSPICIOUS = "auspicious"
    BLACKOUT = "blackout"
    CULTURAL = "cultural"
    STATUTORY = "statutory"


class CalendarEvent(msgspec.Struct, kw_only=True):
    """An event on an operational or cultural calendar."""

    name: str
    kind: CalendarKind
    start: int
    end: int
    affected_resources: list[str] = msgspec.field(default_factory=list)
    is_blackout: bool = True
    hard: bool = True
    label: str = ""
    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.start > self.end:
            msg = (
                f"Calendar event '{self.name}' start ({self.start}) cannot exceed end ({self.end})"
            )
            raise ValueError(msg)
        if not self.label:
            self.label = self.name

    def to_interval_window(self) -> IntervalWindow:
        return IntervalWindow(
            start=self.start,
            end=self.end,
            label=self.label,
            hard=self.hard,
        )
