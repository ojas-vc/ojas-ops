# Calendar Providers

Scheduling problems in real-world operations do not occur in continuous uninterrupted time. They are bound by shifts, weekends, statutory blackout hours, and cultural or astronomical factors.

Ojas Ops abstracts time into discrete integer coordinates while providing pluggable `CalendarProvider` adapters.

```python
from ojas_ops.calendars import StandardCalendarProvider, CulturalCalendarProvider
```

---

## 1. Calendar Provider Protocol

Every calendar provider implements the `CalendarProvider` abstract base class:

```python
class CalendarProvider(ABC):
    @abstractmethod
    def get_blackout_windows(self, resource_id: str | None = None) -> list[IntervalWindow]:
        """Return blackout / unavailable windows."""

    @abstractmethod
    def get_target_windows(self, task_id: str | None = None) -> list[IntervalWindow]:
        """Return preferred or mandatory target windows for task execution."""

    @abstractmethod
    def get_events(self, kind: CalendarKind | None = None) -> list[CalendarEvent]:
        """Return registered calendar events."""

    def is_available(self, resource_id: str, start: int, end: int) -> bool:
        """Check availability during an interval."""
```

---

## 2. Standard Operational Calendar

`StandardCalendarProvider` handles traditional business and manufacturing environments:

- Standard working hours (e.g. 09:00 - 17:00).
- Working days (e.g. Monday–Friday).
- Weekend exclusions.
- Public and company holidays.
- Resource-specific preventive maintenance windows.

```python
from ojas_ops.calendars import StandardCalendarProvider

calendar = StandardCalendarProvider(
    horizon_days=14,
    day_minutes=1440,
    work_start_minute=9 * 60,   # 09:00 (minute 540)
    work_end_minute=17 * 60,    # 17:00 (minute 1020)
    working_days=(0, 1, 2, 3, 4), # Monday to Friday
)

# Mark Day 7 as a company holiday
calendar.add_holiday(day=7, name="Quarterly Inventory Day")

# Schedule planned maintenance for CNC Mill 1 on Day 2
calendar.add_maintenance(
    resource_id="cnc_mill_01",
    start=2 * 1440 + 10 * 60,  # Day 2 at 10:00
    end=2 * 1440 + 14 * 60,    # Day 2 at 14:00
    name="Spindle Calibration",
)

scheduler.add_calendar(calendar)
```

---

## 3. Cultural & Astrological Calendar

`CulturalCalendarProvider` provides native modeling for non-Gregorian, Hindu Panchang, lunar, and culturally variable calendar requirements:

### 3.1 Inauspicious Blackout Intervals

Automatically generates daily inauspicious intervals where critical tasks or ceremonies are prohibited:

- **Rahu Kalam**: Daily 90-minute shifting window based on weekday solar hours.
- **Yamagandam**: Daily inauspicious window.

```python
cultural_cal = CulturalCalendarProvider(
    horizon_days=7,
    enable_rahu_kalam=True,
    enable_yamagandam=True,
)
```

### 3.2 Auspicious Target Windows (Shubh Muhurats)

Anchors milestone tasks (e.g., launch ceremonies, foundation stone laying, weddings, high-value trades) strictly within calculated auspicious windows:

```python
# Add an auspicious Shubh Muhurat on Day 1 (11:15 AM to 12:45 PM)
cultural_cal.add_muhurat(
    start=1 * 1440 + 11 * 60 + 15,
    end=1 * 1440 + 12 * 60 + 45,
    name="Abhijeet Muhurat",
    task_id="inauguration_ceremony",
    hard=True,
)
```

### 3.3 Dynamic Lunar Festival Offsets

Allows tasks (e.g. marketing campaigns, inventory ramp-ups) to be anchored relative to a shifting lunar festival date (e.g. `Diwali - 30 days` or `Dhanteras - 14 days`):

```python
# Festival is on Day 20; anchor campaign launch to D - 7 days at 10:00 AM
cultural_cal.anchor_lunar_offset(
    festival_day=20,
    offset_days=-7,
    task_id="festive_campaign_launch",
    duration_minutes=180,
    preferred_start_minute=10 * 60,
)
```

### 3.4 Statutory Curfews & Dry Days

Enforces municipal sound amplification curfew limits (e.g. 22:00 to 06:00) or statutory dry days for event planning:

```python
cultural_cal.add_curfew_blackout(
    start_minute=22 * 60,  # 22:00
    end_minute=24 * 60,    # 24:00
    name="Municipal Noise Ordinance",
)
```
