"""Unit tests for standard and cultural calendar providers."""

from ojas_ops.calendars import CulturalCalendarProvider, StandardCalendarProvider


def test_standard_calendar_provider() -> None:
    # 7-day horizon with 9-5 working hours Mon-Fri
    cal = StandardCalendarProvider(
        horizon_days=7,
        work_start_minute=9 * 60,
        work_end_minute=17 * 60,
    )
    events = cal.get_events()
    assert len(events) > 0

    # Resource maintenance
    cal.add_maintenance("machine_1", start=1000, end=1200, name="Oil Change")
    blackouts = cal.get_blackout_windows(resource_id="machine_1")
    assert any(w.label == "maintenance:machine_1" for w in blackouts)

    # Check availability
    assert not cal.is_available("machine_1", 1050, 1150)


def test_cultural_calendar_provider() -> None:
    cal = CulturalCalendarProvider(
        horizon_days=7,
        enable_rahu_kalam=True,
        enable_yamagandam=True,
    )

    blackouts = cal.get_blackout_windows()
    assert any("rahu_kalam" in w.label for w in blackouts)
    assert any("yamagandam" in w.label for w in blackouts)

    # Add auspicious Shubh Muhurat
    cal.add_muhurat(
        start=600,
        end=720,
        name="Abhijeet Muhurat",
        task_id="ceremony_1",
    )
    targets = cal.get_target_windows(task_id="ceremony_1")
    assert len(targets) == 1
    assert targets[0].label == "muhurat:Abhijeet Muhurat"

    # Test dynamic lunar festival anchor
    # Festival on Day 10, campaign flight at D - 3 days
    anchor_win = cal.anchor_lunar_offset(
        festival_day=10,
        offset_days=-3,
        task_id="campaign_launch",
        duration_minutes=120,
    )
    assert anchor_win.start == 7 * 1440 + 10 * 60  # Day 7 at 10:00
    assert anchor_win.duration == 120
