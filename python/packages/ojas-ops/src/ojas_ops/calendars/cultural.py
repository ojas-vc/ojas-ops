"""Cultural, astrological, lunar, and Panchang calendar provider."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.calendars.base import CalendarProvider
from ojas_ops.models.calendar import CalendarEvent, CalendarKind
from ojas_ops.models.time import IntervalWindow


class CulturalCalendarProvider(CalendarProvider):
    """Provides auspicious windows (Muhurats) and inauspicious blackout intervals (Rahu Kalam, etc.)."""

    # Typical daily 1.5-hour Rahu Kalam windows relative to sunrise (e.g. 06:00 sunrise)
    # Stored as minute offset from midnight for a standard 06:00-18:00 day
    # Monday: 07:30 - 09:00 (450 - 540)
    # Tuesday: 15:00 - 16:30 (900 - 990)
    # Wednesday: 12:00 - 13:30 (720 - 810)
    # Thursday: 13:30 - 15:00 (810 - 900)
    # Friday: 10:30 - 12:00 (630 - 720)
    # Saturday: 09:00 - 10:30 (540 - 630)
    # Sunday: 16:30 - 18:00 (990 - 1080)
    RAHU_KALAM_DEFAULTS: dict[int, tuple[int, int]] = {
        0: (7 * 60 + 30, 9 * 60),  # Monday
        1: (15 * 60, 16 * 60 + 30),  # Tuesday
        2: (12 * 60, 13 * 60 + 30),  # Wednesday
        3: (13 * 60 + 30, 15 * 60),  # Thursday
        4: (10 * 60 + 30, 12 * 60),  # Friday
        5: (9 * 60, 10 * 60 + 30),  # Saturday
        6: (16 * 60 + 30, 18 * 60),  # Sunday
    }

    # Daily Yamagandam windows (inauspicious)
    YAMAGANDAM_DEFAULTS: dict[int, tuple[int, int]] = {
        0: (10 * 60 + 30, 12 * 60),  # Monday
        1: (9 * 60, 10 * 60 + 30),  # Tuesday
        2: (7 * 60 + 30, 9 * 60),  # Wednesday
        3: (6 * 60, 7 * 60 + 30),  # Thursday
        4: (15 * 60, 16 * 60 + 30),  # Friday
        5: (13 * 60 + 30, 15 * 60),  # Saturday
        6: (12 * 60, 13 * 60 + 30),  # Sunday
    }

    def __init__(
        self,
        *,
        horizon_days: int = 7,
        day_minutes: int = 1440,
        enable_rahu_kalam: bool = True,
        enable_yamagandam: bool = True,
    ) -> None:
        self.horizon_days = horizon_days
        self.day_minutes = day_minutes
        self._events: list[CalendarEvent] = []
        self._target_windows: dict[str, list[IntervalWindow]] = {}
        self._general_targets: list[IntervalWindow] = []

        if enable_rahu_kalam:
            self._generate_rahu_kalam()
        if enable_yamagandam:
            self._generate_yamagandam()

    def _generate_rahu_kalam(self) -> None:
        for day in range(self.horizon_days):
            day_offset = day * self.day_minutes
            weekday = day % 7
            if weekday in self.RAHU_KALAM_DEFAULTS:
                start_min, end_min = self.RAHU_KALAM_DEFAULTS[weekday]
                self._events.append(
                    CalendarEvent(
                        name=f"Rahu Kalam Day {day}",
                        kind=CalendarKind.BLACKOUT,
                        start=day_offset + start_min,
                        end=day_offset + end_min,
                        is_blackout=True,
                        hard=True,
                        label="rahu_kalam",
                    )
                )

    def _generate_yamagandam(self) -> None:
        for day in range(self.horizon_days):
            day_offset = day * self.day_minutes
            weekday = day % 7
            if weekday in self.YAMAGANDAM_DEFAULTS:
                start_min, end_min = self.YAMAGANDAM_DEFAULTS[weekday]
                self._events.append(
                    CalendarEvent(
                        name=f"Yamagandam Day {day}",
                        kind=CalendarKind.BLACKOUT,
                        start=day_offset + start_min,
                        end=day_offset + end_min,
                        is_blackout=True,
                        hard=True,
                        label="yamagandam",
                    )
                )

    def add_muhurat(
        self,
        start: int,
        end: int,
        name: str = "Shubh Muhurat",
        task_id: str | None = None,
        hard: bool = True,
    ) -> None:
        """Add an auspicious target window for ceremonies, launches, or key tasks."""
        window = IntervalWindow(start=start, end=end, label=f"muhurat:{name}", hard=hard)
        if task_id:
            if task_id not in self._target_windows:
                self._target_windows[task_id] = []
            self._target_windows[task_id].append(window)
        else:
            self._general_targets.append(window)

        self._events.append(
            CalendarEvent(
                name=name,
                kind=CalendarKind.AUSPICIOUS,
                start=start,
                end=end,
                is_blackout=False,
                hard=hard,
                label=f"muhurat:{name}",
            )
        )

    def add_curfew_blackout(
        self,
        start_minute: int = 22 * 60,  # 22:00
        end_minute: int = 24 * 60,  # 24:00 (and 00:00 - 06:00)
        name: str = "Municipal Sound Curfew",
    ) -> None:
        """Add recurring sound/amplification curfew blackout hours across all days."""
        for day in range(self.horizon_days):
            day_offset = day * self.day_minutes
            self._events.append(
                CalendarEvent(
                    name=f"{name} Night (Day {day})",
                    kind=CalendarKind.STATUTORY,
                    start=day_offset + start_minute,
                    end=day_offset + end_minute,
                    is_blackout=True,
                    hard=True,
                    label="sound_curfew",
                )
            )

    def anchor_lunar_offset(
        self,
        festival_day: int,
        offset_days: int,
        task_id: str,
        duration_minutes: int = 60,
        preferred_start_minute: int = 10 * 60,
    ) -> IntervalWindow:
        """Calculate and attach a target window anchored relative to a shifting lunar festival."""
        target_day = festival_day + offset_days
        start = target_day * self.day_minutes + preferred_start_minute
        end = start + duration_minutes
        window = IntervalWindow(start=start, end=end, label=f"lunar_anchor:{task_id}", hard=True)
        if task_id not in self._target_windows:
            self._target_windows[task_id] = []
        self._target_windows[task_id].append(window)
        return window

    def get_blackout_windows(self, resource_id: str | None = None) -> list[IntervalWindow]:
        return [event.to_interval_window() for event in self._events if event.is_blackout]

    def get_target_windows(self, task_id: str | None = None) -> list[IntervalWindow]:
        targets = list(self._general_targets)
        if task_id and task_id in self._target_windows:
            targets.extend(self._target_windows[task_id])
        return targets

    def get_events(self, kind: CalendarKind | None = None) -> list[CalendarEvent]:
        if kind is None:
            return list(self._events)
        return [e for e in self._events if e.kind == kind]
