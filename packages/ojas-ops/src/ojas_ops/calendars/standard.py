"""Standard working calendar provider handling business hours, shifts, weekends, and holidays."""

from __future__ import annotations

import msgspec

from ojas_ops.calendars.base import CalendarProvider
from ojas_ops.models.calendar import CalendarEvent, CalendarKind
from ojas_ops.models.time import IntervalWindow


class Shift(msgspec.Struct, kw_only=True):
    """Working shift definition in minutes from midnight (0..1440)."""

    name: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end > 1440 or self.start >= self.end:
            msg = f"Invalid shift bounds for '{self.name}': {self.start} to {self.end}"
            raise ValueError(msg)


class StandardCalendarProvider(CalendarProvider):
    """Operational calendar supporting work shifts, weekends, holidays, and maintenance."""

    def __init__(
        self,
        *,
        horizon_days: int = 7,
        day_minutes: int = 1440,
        work_start_minute: int = 9 * 60,  # 09:00 (540)
        work_end_minute: int = 17 * 60,  # 17:00 (1020)
        working_days: tuple[int, ...] = (0, 1, 2, 3, 4),  # Monday=0 to Friday=4
    ) -> None:
        self.horizon_days = horizon_days
        self.day_minutes = day_minutes
        self.work_start_minute = work_start_minute
        self.work_end_minute = work_end_minute
        self.working_days = set(working_days)

        self._events: list[CalendarEvent] = []
        self._resource_blackouts: dict[str, list[IntervalWindow]] = {}
        self._task_targets: dict[str, list[IntervalWindow]] = {}

        self._generate_default_non_working_windows()

    def _generate_default_non_working_windows(self) -> None:
        """Generate blackout windows outside working hours and during weekends."""
        for day in range(self.horizon_days):
            day_offset = day * self.day_minutes
            weekday = day % 7

            if weekday not in self.working_days:
                # Full day non-working (e.g. Weekend)
                self._events.append(
                    CalendarEvent(
                        name=f"Weekend Day {day}",
                        kind=CalendarKind.OPERATIONAL,
                        start=day_offset,
                        end=day_offset + self.day_minutes,
                        is_blackout=True,
                        hard=True,
                        label="weekend",
                    )
                )
            else:
                # Off-hours before shift
                if self.work_start_minute > 0:
                    self._events.append(
                        CalendarEvent(
                            name=f"Off-hours pre-shift Day {day}",
                            kind=CalendarKind.OPERATIONAL,
                            start=day_offset,
                            end=day_offset + self.work_start_minute,
                            is_blackout=True,
                            hard=True,
                            label="off_hours",
                        )
                    )
                # Off-hours after shift
                if self.work_end_minute < self.day_minutes:
                    self._events.append(
                        CalendarEvent(
                            name=f"Off-hours post-shift Day {day}",
                            kind=CalendarKind.OPERATIONAL,
                            start=day_offset + self.work_end_minute,
                            end=day_offset + self.day_minutes,
                            is_blackout=True,
                            hard=True,
                            label="off_hours",
                        )
                    )

    def add_holiday(self, day: int, name: str = "Holiday") -> None:
        """Mark an entire day as a holiday blackout window."""
        day_offset = day * self.day_minutes
        self._events.append(
            CalendarEvent(
                name=f"{name} (Day {day})",
                kind=CalendarKind.HOLIDAY,
                start=day_offset,
                end=day_offset + self.day_minutes,
                is_blackout=True,
                hard=True,
                label=name.lower().replace(" ", "_"),
            )
        )

    def add_maintenance(
        self,
        resource_id: str,
        start: int,
        end: int,
        name: str = "Maintenance",
    ) -> None:
        """Add a maintenance blackout window for a specific resource."""
        window = IntervalWindow(start=start, end=end, label=f"maintenance:{name}", hard=True)
        if resource_id not in self._resource_blackouts:
            self._resource_blackouts[resource_id] = []
        self._resource_blackouts[resource_id].append(window)

        self._events.append(
            CalendarEvent(
                name=f"{name} ({resource_id})",
                kind=CalendarKind.MAINTENANCE,
                start=start,
                end=end,
                affected_resources=[resource_id],
                is_blackout=True,
                hard=True,
                label=f"maintenance:{resource_id}",
            )
        )

    def add_target_window(self, task_id: str, window: IntervalWindow) -> None:
        """Assign an execution target window to a task."""
        if task_id not in self._task_targets:
            self._task_targets[task_id] = []
        self._task_targets[task_id].append(window)

    def get_blackout_windows(self, resource_id: str | None = None) -> list[IntervalWindow]:
        windows: list[IntervalWindow] = [
            event.to_interval_window()
            for event in self._events
            if event.is_blackout
            and (
                not event.affected_resources
                or (resource_id and resource_id in event.affected_resources)
            )
        ]
        if resource_id and resource_id in self._resource_blackouts:
            windows.extend(self._resource_blackouts[resource_id])
        return windows

    def get_target_windows(self, task_id: str | None = None) -> list[IntervalWindow]:
        if task_id and task_id in self._task_targets:
            return self._task_targets[task_id]
        return []

    def get_events(self, kind: CalendarKind | None = None) -> list[CalendarEvent]:
        if kind is None:
            return list(self._events)
        return [e for e in self._events if e.kind == kind]
