"""Unit tests for independent deterministic schedule validation."""

from ojas_ops.models import (
    Resource,
    ResourceType,
    ScheduledTask,
    ScheduleResult,
    ScheduleStatus,
    Task,
    TimeWindow,
)
from ojas_ops.validation import ScheduleValidator


def test_validator_detects_violations() -> None:
    tasks = {
        "t1": Task(
            id="t1",
            duration=60,
            required_resources=["m1"],
            time_window=TimeWindow(deadline=100),
        ),
        "t2": Task(
            id="t2",
            duration=30,
            required_resources=["m1"],
            dependencies=["t1"],
        ),
    }

    resources = {
        "m1": Resource(id="m1", capacity=1, resource_type=ResourceType.MACHINE),
    }

    validator = ScheduleValidator(tasks=tasks, resources=resources)

    # Valid schedule
    valid_result = ScheduleResult(
        status=ScheduleStatus.OPTIMAL,
        tasks={
            "t1": ScheduledTask(
                task_id="t1", start=0, end=60, duration=60, assigned_resources=["m1"]
            ),
            "t2": ScheduledTask(
                task_id="t2", start=60, end=90, duration=30, assigned_resources=["m1"]
            ),
        },
        resources={
            "m1": ScheduledTask(task_id="t1", start=0, end=60, duration=60).assigned_resources
            or [],
        },
    )
    # Correct resources map
    from ojas_ops.models import ResourceAssignment

    valid_result.resources = {"m1": ResourceAssignment(resource_id="m1", task_ids=["t1", "t2"])}

    report = validator.validate(valid_result)
    assert report.is_valid
    assert report.error_count == 0

    # Invalidate by breaking precedence: t2 starts before t1 finishes
    invalid_result = ScheduleResult(
        status=ScheduleStatus.FEASIBLE,
        tasks={
            "t1": ScheduledTask(
                task_id="t1", start=0, end=60, duration=60, assigned_resources=["m1"]
            ),
            "t2": ScheduledTask(
                task_id="t2", start=20, end=50, duration=30, assigned_resources=["m1"]
            ),
        },
        resources={"m1": ResourceAssignment(resource_id="m1", task_ids=["t1", "t2"])},
    )

    report_inv = validator.validate(invalid_result)
    assert not report_inv.is_valid
    assert report_inv.error_count >= 1
    # Check that error is precedence or collision
    violation_names = [v.constraint_name for v in report_inv.violations]
    assert any("Precedence" in name or "NoOverlap" in name for name in violation_names)
