"""Unit tests for the Google OR-Tools CP-SAT solver compilation and execution."""

from ojas_ops.models import (
    IntervalWindow,
    Resource,
    ResourceRequirement,
    ResourceType,
    ScheduleStatus,
    Task,
    TimeWindow,
)
from ojas_ops.solvers import CpSatSolver


def test_cpsat_solver_precedence_and_resource() -> None:
    solver = CpSatSolver()

    res = {"crane_1": Resource(id="crane_1", capacity=1, resource_type=ResourceType.EQUIPMENT)}

    tasks = {
        "job_a": Task(
            id="job_a",
            duration=30,
            required_resources=["crane_1"],
        ),
        "job_b": Task(
            id="job_b",
            duration=45,
            required_resources=["crane_1"],
            dependencies=["job_a"],
        ),
    }

    result = solver.solve(tasks=tasks, resources=res)

    assert result.status == ScheduleStatus.OPTIMAL
    assert result.is_feasible
    assert result.makespan == 75

    st_a = result.tasks["job_a"]
    st_b = result.tasks["job_b"]
    assert st_a.start >= 0
    assert st_a.end == st_a.start + 30
    assert st_b.start >= st_a.end
    assert st_b.end == st_b.start + 45


def test_cpsat_solver_candidate_pool_selection() -> None:
    solver = CpSatSolver()

    res = {
        "truck_1": Resource(id="truck_1", capacity=1, resource_type=ResourceType.EQUIPMENT),
        "truck_2": Resource(id="truck_2", capacity=1, resource_type=ResourceType.EQUIPMENT),
    }

    # Two concurrent tasks that both need a truck, selecting from candidate pool
    req1 = ResourceRequirement(
        resource_id="truck_1",
        capacity=1,
        candidate_pool=["truck_1", "truck_2"],
    )
    req2 = ResourceRequirement(
        resource_id="truck_1",
        capacity=1,
        candidate_pool=["truck_1", "truck_2"],
    )

    tasks = {
        "delivery_1": Task(
            id="delivery_1",
            duration=60,
            resource_requirements=[req1],
            time_window=TimeWindow(latest_end=60),
        ),
        "delivery_2": Task(
            id="delivery_2",
            duration=60,
            resource_requirements=[req2],
            time_window=TimeWindow(latest_end=60),
        ),
    }

    result = solver.solve(tasks=tasks, resources=res)

    assert result.status == ScheduleStatus.OPTIMAL
    assert result.makespan == 60

    # Since both finished at 60 and each had duration 60, they must have been assigned to different trucks!
    t1_assigned = result.tasks["delivery_1"].assigned_resources[0]
    t2_assigned = result.tasks["delivery_2"].assigned_resources[0]
    assert t1_assigned != t2_assigned


def test_cpsat_solver_blackout_and_target_windows() -> None:
    solver = CpSatSolver()

    # Resource with blackout window from 30 to 90
    blackout = IntervalWindow(start=30, end=90, label="maintenance")
    res = {
        "lathe": Resource(
            id="lathe",
            capacity=1,
            resource_type=ResourceType.MACHINE,
            blackout_windows=[blackout],
        )
    }

    tasks = {
        "part_1": Task(
            id="part_1",
            duration=40,
            required_resources=["lathe"],
        ),
        "part_2": Task(
            id="part_2",
            duration=40,
            required_resources=["lathe"],
        ),
    }

    result = solver.solve(tasks=tasks, resources=res)

    assert result.is_feasible
    for st in result.tasks.values():
        # Neither task should overlap with [30, 90)
        assert not (max(st.start, 30) < min(st.end, 90))
