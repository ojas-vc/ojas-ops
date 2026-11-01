"""Abstract base class and protocol for calendar providers."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from abc import ABC, abstractmethod

from ojas_ops.models.calendar import CalendarEvent, CalendarKind
from ojas_ops.models.time import IntervalWindow


class CalendarProvider(ABC):
    """Abstract interface for operational, standard, and cultural calendar providers."""

    @abstractmethod
    def get_blackout_windows(self, resource_id: str | None = None) -> list[IntervalWindow]:
        """Return blackout / unavailable windows for a resource or general operations."""

    @abstractmethod
    def get_target_windows(self, task_id: str | None = None) -> list[IntervalWindow]:
        """Return target / auspicious / preferred windows for task execution."""

    @abstractmethod
    def get_events(self, kind: CalendarKind | None = None) -> list[CalendarEvent]:
        """Return registered calendar events optionally filtered by kind."""

    def is_available(self, resource_id: str, start: int, end: int) -> bool:
        """Check if a resource is available during [start, end)."""
        blackouts = self.get_blackout_windows(resource_id)
        for window in blackouts:
            if window.hard and window.overlaps(start, end):
                return False
        return True
