"""Unit tests for the fluent Scheduler API matching README Quick Start."""

from ojas_ops import Scheduler
from ojas_ops.models import IntervalWindow, ScheduleStatus


def test_quick_start_api_flow() -> None:
    scheduler = Scheduler()

    # Add a venue or production resource
    scheduler.add_resource(
        id="main-auditorium",
        capacity=1,
    )

    # Add an event session or task
    scheduler.add_task(
        id="keynote-launch",
        duration=60,  # minutes
        required_resources=["main-auditorium"],
    )

    # Enforce a blackout window (e.g., maintenance or Rahu Kalam)
    scheduler.add_blackout_window(
        resource_id="main-auditorium",
        window=IntervalWindow(start=90, end=150, label="blackout_window"),
    )

    # Anchor to an auspicious target window (e.g., Shubh Muhurat)
    scheduler.add_target_window(
        task_id="keynote-launch",
        window=IntervalWindow(start=180, end=300, label="shubh_muhurat"),
        hard=True,
    )

    scheduler.minimize("makespan")

    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid

    task_result = result.tasks["keynote-launch"]
    assert task_result.start >= 180
    assert task_result.end <= 300
    assert not (max(task_result.start, 90) < min(task_result.end, 150))

