"""Unit tests for the Google OR-Tools CP-SAT solver compilation and execution."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


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


def test_cpsat_circuit_transition_constraint() -> None:
    """Verifies OR-Tools circuit transition formulation applies delay only between immediate consecutive tasks."""
    from ojas_ops.constraints import TransitionConstraint
    from ojas_ops.models import Horizon

    solver = CpSatSolver()
    res = {"cnc": Resource(id="cnc", capacity=1, resource_type=ResourceType.MACHINE)}
    tasks = {
        "t1": Task(id="t1", duration=10, required_resources=["cnc"], fixed_start=0),
        "t2": Task(id="t2", duration=10, required_resources=["cnc"]),
        "t3": Task(id="t3", duration=10, required_resources=["cnc"]),
    }
    # Direct t1 -> t2 has large delay 50. But t1 -> t3 is 5, t3 -> t2 is 5.
    trans = TransitionConstraint(
        resource_id="cnc",
        transition_matrix={
            ("t1", "t2"): 50,
            ("t1", "t3"): 5,
            ("t3", "t2"): 5,
        },
        default_buffer=0,
    )

    result = solver.solve(
        tasks=tasks,
        resources=res,
        horizon=Horizon(start=0, end=100),
        constraints=[trans],
    )

    assert result.status == ScheduleStatus.OPTIMAL
    # The optimal sequence is t1 -> t3 -> t2, achieving makespan 40, NOT >= 70!
    assert result.makespan == 40
    assert result.tasks["t1"].start == 0
    assert result.tasks["t1"].end == 10
    assert result.tasks["t3"].start == 15
    assert result.tasks["t3"].end == 25
    assert result.tasks["t2"].start == 30
    assert result.tasks["t2"].end == 40


def test_cpsat_cost_optimization_with_candidate_selection() -> None:
    """Verifies cost minimization correctly selects cheaper candidate resource."""
    from ojas_ops.objectives import MinimizeCostObjective

    solver = CpSatSolver()
    res = {
        "cheap_worker": Resource(id="cheap_worker", capacity=1, cost_per_time_unit=5.0),
        "expensive_worker": Resource(id="expensive_worker", capacity=1, cost_per_time_unit=50.0),
    }
    req = ResourceRequirement(
        resource_id="cheap_worker",
        capacity=1,
        candidate_pool=["cheap_worker", "expensive_worker"],
    )
    tasks = {
        "job_1": Task(id="job_1", duration=20, resource_requirements=[req]),
    }

    cost_obj = MinimizeCostObjective()
    result = solver.solve(tasks=tasks, resources=res, objective=cost_obj)

    assert result.status == ScheduleStatus.OPTIMAL
    assert result.tasks["job_1"].assigned_resources == ["cheap_worker"]
    expected_cost = 20 * 5.0  # 100.0
    assert result.objective_value == expected_cost
    assert cost_obj.evaluate(result.tasks, result.resources) == expected_cost


def test_cpsat_solver_metadata_and_hints() -> None:
    """Verifies solver telemetry reporting and solution hinting."""
    solver = CpSatSolver()
    res = {"m1": Resource(id="m1", capacity=1)}
    tasks = {
        "a": Task(id="a", duration=15, required_resources=["m1"]),
        "b": Task(id="b", duration=15, required_resources=["m1"]),
    }

    hints = {"a": 0, "b": 15}
    result = solver.solve(tasks=tasks, resources=res, solution_hints=hints)

    assert result.status == ScheduleStatus.OPTIMAL
    assert "best_objective_bound" in result.metadata
    assert "user_time" in result.metadata
    assert "num_branches" in result.metadata
    assert "num_conflicts" in result.metadata
