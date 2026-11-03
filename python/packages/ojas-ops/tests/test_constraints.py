"""Unit tests for constraint formulations and independent validation checks."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.constraints import (
    CumulativeResourceConstraint,
    MaxWorkloadConstraint,
    MinRestConstraint,
    NoOverlapConstraint,
    PrecedenceConstraint,
    TransitionConstraint,
)
from ojas_ops.models import (
    DependencyType,
    ResourceAssignment,
    ScheduledTask,
)
from ojas_ops.validation.report import Severity


def test_precedence_constraint_validation() -> None:
    c = PrecedenceConstraint("t1", "t2", dependency_type=DependencyType.FS, min_lag=10)

    # Valid schedule: t1 ends at 50, t2 starts at 60 (lag >= 10)
    valid_tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=50, duration=50),
        "t2": ScheduledTask(task_id="t2", start=60, end=100, duration=40),
    }
    assert len(c.validate(valid_tasks, {})) == 0

    # Invalid schedule: t2 starts at 55 (lag only 5 < 10)
    invalid_tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=50, duration=50),
        "t2": ScheduledTask(task_id="t2", start=55, end=95, duration=40),
    }
    violations = c.validate(invalid_tasks, {})
    assert len(violations) == 1
    assert violations[0].severity == Severity.ERROR
    assert "Precedence violation" in violations[0].message


def test_no_overlap_constraint_validation() -> None:
    c = NoOverlapConstraint("machine_1")

    # Overlapping tasks on machine_1
    tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=50, duration=50),
        "t2": ScheduledTask(task_id="t2", start=40, end=90, duration=50),
    }
    resources = {
        "machine_1": ResourceAssignment(resource_id="machine_1", task_ids=["t1", "t2"]),
    }
    violations = c.validate(tasks, resources)
    assert len(violations) == 1
    assert "collision" in violations[0].message


def test_cumulative_resource_constraint_validation() -> None:
    c = CumulativeResourceConstraint("server_pool", capacity=2)

    tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=50, duration=50),
        "t2": ScheduledTask(task_id="t2", start=10, end=60, duration=50),
        "t3": ScheduledTask(task_id="t3", start=20, end=40, duration=20),
    }
    resources = {
        "server_pool": ResourceAssignment(resource_id="server_pool", task_ids=["t1", "t2", "t3"]),
    }
    # At time 20, t1, t2, and t3 run concurrently => demand is 3 > capacity 2
    violations = c.validate(tasks, resources)
    assert len(violations) == 1
    assert "capacity exceeded" in violations[0].message


def test_transition_constraint_validation() -> None:
    c = TransitionConstraint(
        resource_id="hall_1",
        transition_matrix={("t1", "t2"): 30},
        default_buffer=10,
    )
    tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=60, duration=60),
        "t2": ScheduledTask(task_id="t2", start=70, end=120, duration=50),
    }
    resources = {
        "hall_1": ResourceAssignment(resource_id="hall_1", task_ids=["t1", "t2"]),
    }
    # Gap is 10, but transition matrix requires 30
    violations = c.validate(tasks, resources)
    assert len(violations) == 1
    assert "Insufficient transition buffer" in violations[0].message


def test_min_rest_and_max_workload_validation() -> None:
    min_rest = MinRestConstraint("nurse_1", min_rest=60)
    max_work = MaxWorkloadConstraint("nurse_1", max_duration=100)

    tasks = {
        "t1": ScheduledTask(task_id="t1", start=0, end=50, duration=50),
        "t2": ScheduledTask(task_id="t2", start=80, end=150, duration=70),
    }
    resources = {
        "nurse_1": ResourceAssignment(resource_id="nurse_1", task_ids=["t1", "t2"]),
    }

    # Rest gap is 30 < 60
    rest_violations = min_rest.validate(tasks, resources)
    assert len(rest_violations) == 1
    assert "Rest violation" in rest_violations[0].message

    # Total duration is 50 + 70 = 120 > 100
    workload_violations = max_work.validate(tasks, resources)
    assert len(workload_violations) == 1
    assert "exceeded max workload" in workload_violations[0].message
