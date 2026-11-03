"""Time representation and interval window models."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import msgspec


class IntervalWindow(msgspec.Struct, kw_only=True):
    """An interval window defined by start and end integer coordinates."""

    start: int
    end: int
    label: str = ""
    hard: bool = True

    def __post_init__(self) -> None:
        if self.start > self.end:
            msg = f"Invalid window interval: start ({self.start}) cannot exceed end ({self.end})"
            raise ValueError(msg)

    @property
    def duration(self) -> int:
        return self.end - self.start

    def overlaps(self, other_start: int, other_end: int) -> bool:
        """Return True if this window overlaps with [other_start, other_end)."""
        return max(self.start, other_start) < min(self.end, other_end)

    def contains(self, point: int) -> bool:
        """Return True if point is inside [start, end)."""
        return self.start <= point < self.end

    def encloses(self, other_start: int, other_end: int) -> bool:
        """Return True if this window completely encloses [other_start, other_end]."""
        return self.start <= other_start and self.end >= other_end


class TimeWindow(msgspec.Struct, kw_only=True):
    """Temporal boundary constraints for task execution."""

    earliest_start: int | None = None
    latest_start: int | None = None
    earliest_end: int | None = None
    latest_end: int | None = None
    deadline: int | None = None


class Horizon(msgspec.Struct, kw_only=True):
    """Scheduling horizon defining the temporal scope and discretization."""

    start: int = 0
    end: int = 1440
    granularity: int = 1  # Discretization unit (e.g. 1 minute, 15 minutes, 1 hour)

    @property
    def total_units(self) -> int:
        return max(0, (self.end - self.start) // max(1, self.granularity))
