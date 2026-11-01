"""Unit tests for Ojas Ops typed domain models."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import msgspec
import pytest
from ojas_ops.models import (
    IntervalWindow,
    Resource,
    ResourceType,
    ScheduledTask,
    ScheduleResult,
    ScheduleStatus,
    Task,
    TaskPriority,
)


def test_interval_window_operations() -> None:
    w1 = IntervalWindow(start=100, end=200, label="window_1")
    assert w1.duration == 100
    assert w1.contains(150)
    assert not w1.contains(250)
    assert w1.overlaps(150, 250)
    assert not w1.overlaps(200, 300)
    assert w1.encloses(120, 180)
    assert not w1.encloses(80, 150)

    with pytest.raises(ValueError, match="Invalid window interval"):
        IntervalWindow(start=300, end=100)


def test_task_model() -> None:
    t = Task(
        id="t1",
        duration=60,
        required_resources=["r1", "r2"],
        priority=TaskPriority.HIGH,
    )
    assert t.name == "t1"
    assert len(t.resource_requirements) == 2
    assert t.priority.weight == 5

    with pytest.raises(ValueError, match="cannot have negative duration"):
        Task(id="invalid", duration=-10)


def test_resource_model() -> None:
    r = Resource(
        id="res1",
        capacity=2,
        resource_type=ResourceType.MACHINE,
        cost_per_time_unit=50.0,
    )
    assert r.name == "res1"
    assert r.is_available_during(0, 100)

    # Add blackout window
    r.blackout_windows.append(IntervalWindow(start=50, end=70, label="maintenance"))
    assert not r.is_available_during(40, 60)
    assert r.is_available_during(80, 120)

    with pytest.raises(ValueError, match="capacity must be positive"):
        Resource(id="invalid_res", capacity=0)


def test_msgspec_serialization() -> None:
    st = ScheduledTask(
        task_id="task_1",
        start=60,
        end=120,
        duration=60,
        assigned_resources=["worker_1"],
    )
    result = ScheduleResult(
        status=ScheduleStatus.OPTIMAL,
        objective_value=120.0,
        tasks={"task_1": st},
        makespan=120,
    )

    encoded = msgspec.json.encode(result)
    decoded = msgspec.json.decode(encoded, type=ScheduleResult)
    assert decoded.status == ScheduleStatus.OPTIMAL
    assert decoded.tasks["task_1"].start == 60
    assert decoded.is_feasible
