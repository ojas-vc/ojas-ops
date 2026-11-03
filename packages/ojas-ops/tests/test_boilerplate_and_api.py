"""Tests for Ojas boilerplate components, Django models, pure-integer attributes, and Bolt API."""

import pytest
from django_bolt.testing import TestClient
from ojas_ops.adapters.manufacturing import ManufacturingScheduler
from ojas_ops.adapters.marketing_flighting import MarketingFlightingScheduler
from ojas_ops.adapters.workforce import WorkforceScheduler
from ojas_ops.api import api as bolt_api
from ojas_ops.apps import OjasOpsConfig
from ojas_ops.exceptions import OptimizationInfeasibleError, ScheduleValidationError
from ojas_ops.models import DisruptionLog, OptimizationJob, ScenarioRecord, ScheduleRun


def test_boilerplate_apps_config():
    """Verify OjasOpsConfig properties."""
    assert OjasOpsConfig.name == "ojas_ops"
    assert OjasOpsConfig.verbose_name == "Ojas Operations Optimization"


def test_boilerplate_exceptions():
    """Verify domain exception hierarchy."""
    with pytest.raises(OptimizationInfeasibleError):
        raise OptimizationInfeasibleError("Infeasible")

    with pytest.raises(ScheduleValidationError):
        raise ScheduleValidationError("Validation failed")


def test_django_models_instantiation():
    """Verify concrete Django models inherit abstract bases properly."""
    run = ScheduleRun(
        tenant_id="tenant_alpha",
        scenario_name="jobshop_medium",
        status="FEASIBLE",
        makespan=480,
    )
    assert run.tenant_id == "tenant_alpha"
    assert run.makespan == 480

    job = OptimizationJob(
        tenant_id="tenant_alpha",
        temporal_workflow_id="wf-123",
        status="RUNNING",
    )
    assert job.temporal_workflow_id == "wf-123"

    scenario = ScenarioRecord(
        tenant_id="tenant_alpha",
        name="film_benchmark_01",
        domain="film",
    )
    assert scenario.domain == "film"

    disruption = DisruptionLog(
        tenant_id="tenant_alpha",
        schedule_run_id="run-456",
        disruption_type="WEATHER_DELAY",
        magnitude_minutes=120,
    )
    assert disruption.magnitude_minutes == 120


def test_manufacturing_pure_integer_attributes():
    """Verify integer minor currency attributes on ManufacturingScheduler."""
    mfg = ManufacturingScheduler()
    machine = mfg.add_machine("cnc_1", name="5-Axis CNC", hourly_rate=50.0, hourly_rate_cents=5000)
    assert machine.hourly_rate_cents == 5000
    assert machine.hourly_rate == 50.0

    # Test backward-compatibility float setter
    machine.hourly_rate = 75.50
    assert machine.hourly_rate_cents == 7550
    assert machine.hourly_rate == 75.50


def test_workforce_pure_integer_attributes():
    """Verify integer minor currency and minutes attributes on WorkforceScheduler."""
    wf = WorkforceScheduler()
    staff = wf.add_staff("doc_1", name="Dr. Smith", hourly_rate=120.0, hourly_rate_cents=12000)
    assert staff.hourly_rate_cents == 12000
    assert staff.hourly_rate == 120.0

    staff.hourly_rate = 150.25
    assert staff.hourly_rate_cents == 15025
    assert staff.hourly_rate == 150.25


def test_marketing_pure_integer_attributes():
    """Verify integer cents on MarketingFlightingScheduler."""
    mktg = MarketingFlightingScheduler()
    channel = mktg.add_channel(
        "yt", name="YouTube", daily_budget_cap=2000.0, daily_budget_cap_cents=200000
    )
    assert channel.daily_budget_cap_cents == 200000
    assert channel.daily_budget_cap == 2000.0

    flight = mktg.add_flight(
        "fl_1",
        channel_id="yt",
        duration_days=10,
        daily_budget=500.0,
        daily_budget_cents=50000,
    )
    assert flight.daily_budget_cents == 50000
    assert flight.daily_budget == 500.0


def test_bolt_api_health():
    """Verify Django-Bolt health check endpoint."""
    client = TestClient(bolt_api)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "ojas-ops"


def test_bolt_api_optimize_sync():
    """Verify Django-Bolt synchronous schedule optimization endpoint."""
    client = TestClient(bolt_api)
    req_body = {
        "tenant_id": "org_chitram",
        "project_id": "proj_alpha",
        "horizon": {
            "start": 0,
            "end": 1440,
        },
        "resources": [
            {
                "id": "machine_a",
                "name": "Machine Alpha",
                "capacity": 1,
                "cost_per_time_unit_minor": 100,
            }
        ],
        "tasks": [
            {
                "id": "task_1",
                "name": "Task 1",
                "duration": 60,
                "required_resources": ["machine_a"],
            },
            {
                "id": "task_2",
                "name": "Task 2",
                "duration": 30,
                "required_resources": ["machine_a"],
                "dependencies": ["task_1"],
            },
        ],
        "strategy": "balanced",
        "max_time_seconds": 5.0,
    }

    resp = client.post("/schedules/optimize/sync", json=req_body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["schedule_id"] == "sched-proj_alpha"
    assert data["makespan"] == 90  # 60 + 30
    assert data["tasks_scheduled_count"] == 2
