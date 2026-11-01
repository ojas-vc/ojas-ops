"""Unit tests for scenario simulation, disruption handling, and schedule stability."""

from ojas_ops.models import ResourceType
from ojas_ops.scheduling import Scheduler
from ojas_ops.simulation import Disruption, DisruptionType, ScenarioSimulator


def test_scenario_simulator_rescheduling() -> None:
    scheduler = Scheduler()
    scheduler.add_resource("oven_1", capacity=1, resource_type=ResourceType.MACHINE)
    scheduler.add_task("batch_1", duration=40, required_resources=["oven_1"])
    scheduler.add_task("batch_2", duration=40, required_resources=["oven_1"])
    scheduler.add_task("batch_3", duration=40, required_resources=["oven_1"])

    baseline = scheduler.solve()
    assert baseline.is_feasible
    assert baseline.makespan == 120

    # Simulate disruption: oven_1 breaks down from t=35 to t=75 (40 mins outage)
    outage = Disruption(
        type=DisruptionType.RESOURCE_UNAVAILABLE,
        resource_id="oven_1",
        start=35,
        end=75,
        description="heater coil failure",
    )

    simulator = ScenarioSimulator(
        tasks=scheduler.tasks,
        resources=scheduler.resources,
        constraints=scheduler.constraints,
    )

    outcome = simulator.simulate(
        baseline_schedule=baseline,
        disruptions=[outage],
        current_time=0,
    )

    assert outcome.rescheduled_result.is_feasible
    assert outcome.validation_report.is_valid
    # The outage pushed tasks out of [35, 75)
    for st in outcome.rescheduled_result.tasks.values():
        assert not (max(st.start, 35) < min(st.end, 75))

    # Stability metrics
    metrics = outcome.stability_metrics
    assert metrics.total_tasks_count == 3
    assert metrics.makespan_delta >= 0
