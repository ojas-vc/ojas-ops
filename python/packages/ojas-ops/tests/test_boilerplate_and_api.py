"""Tests for Ojas boilerplate components, Django models, pure-integer attributes, and Bolt API."""

import pytest
from django_bolt.testing import TestClient
from ojas_ops.adapters.film_production import ProductionDataset, Scene, Talent
from ojas_ops.adapters.manufacturing import ManufacturingScheduler
from ojas_ops.adapters.marketing_flighting import MarketingFlightingScheduler
from ojas_ops.adapters.workforce import WorkforceScheduler
from ojas_ops.api import api as bolt_api
from ojas_ops.apps import OjasOpsConfig
from ojas_ops.exceptions import OptimizationInfeasibleError, ScheduleValidationError
from ojas_ops.models import DisruptionLog, OptimizationJob, ScenarioRecord, ScheduleRun


@pytest.fixture
def client():
    return TestClient(bolt_api)


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


def test_bolt_api_health(client):
    """Verify Django-Bolt health check endpoint."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "ojas-ops"

    resp2 = client.get("/readyz")
    assert resp2.status_code == 200
    assert resp2.json()["ready"] == "true"


def test_bolt_api_optimize_sync(client):
    """Verify Django-Bolt synchronous schedule optimization endpoint."""
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

    resp = client.post("/schedules/optimize", json=req_body)
    assert resp.status_code == 200
    data = resp.json()
    assert data["schedule_id"] == "sched-proj_alpha"
    assert data["makespan"] == 90  # 60 + 30
    assert data["tasks_scheduled_count"] == 2


def test_bolt_api_schedules_runs(client):
    """Verify ModelViewSet CRUD operations for ScheduleRun records."""
    run = ScheduleRun.objects.create(
        tenant_id="tenant_runs_test",
        scenario_name="scen_audit_01",
        status="OPTIMAL",
        makespan=360,
        objective_value=36000,
        result_json={"tasks": {"t1": {"start": 0, "end": 60}}},
    )

    # 1. List with pagination
    resp = client.get("/schedule-runs?tenant_id=tenant_runs_test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    items = data["items"]
    assert items[0]["scenario_name"] == "scen_audit_01"

    # 2. Retrieve
    run_id = run.id
    detail_resp = client.get(f"/schedule-runs/{run_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == run_id
    assert detail["makespan"] == 360
    assert "result_json" in detail

    # 3. Create via POST
    create_resp = client.post(
        "/schedule-runs",
        json={
            "scenario_name": "scen_audit_created",
            "tenant_id": "tenant_runs_test",
            "status": "COMPLETED",
            "makespan": 420,
        },
    )
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    # 4. Partial update via PATCH
    patch_resp = client.patch(
        f"/schedule-runs/{created_id}",
        json={"status": "ARCHIVED"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "ARCHIVED"

    # 5. Delete via DELETE
    del_resp = client.delete(f"/schedule-runs/{created_id}")
    assert del_resp.status_code == 204


def test_bolt_api_workflows_endpoints(client):
    """Verify workflow dispatch, status, jobs list, and signaling."""
    OptimizationJob.objects.create(
        tenant_id="tenant_wf_test",
        temporal_workflow_id="wf-test-active-01",
        status="RUNNING",
        progress_basis_points=5000,
        incumbent_objective=12000,
    )

    # 1. List jobs via ModelViewSet
    resp = client.get("/optimization-jobs?tenant_id=tenant_wf_test")
    assert resp.status_code == 200
    jobs = resp.json()
    assert jobs["total"] >= 1
    assert jobs["items"][0]["temporal_workflow_id"] == "wf-test-active-01"

    # 2. Get status via ViewSet action
    status_resp = client.get("/optimization-jobs/wf-test-active-01/workflow-status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "RUNNING"

    # 3. Send approval signal via ViewSet action
    signal_resp = client.post(
        "/optimization-jobs/wf-test-active-01/approvals",
        json={"decision": "APPROVED", "notes": "Looks optimal"},
    )
    assert signal_resp.status_code == 200
    assert signal_resp.json()["workflow_id"] == "wf-test-active-01"


def test_bolt_api_simulation_endpoints(client):
    """Verify disruption simulation and reactive rescheduling."""
    sim_payload = {
        "tenant_id": "tenant_sim",
        "schedule_id": "sched_base_01",
        "baseline_schedule": {
            "status": "optimal",
            "makespan": 180,
            "tasks": {
                "t1": {
                    "task_id": "t1",
                    "start": 0,
                    "end": 60,
                    "duration": 60,
                    "assigned_resources": ["r1"],
                }
            },
        },
        "disruptions": [
            {
                "disruption_type": "task_delay",
                "task_id": "t1",
                "delay_minutes": 30,
                "description": "Late raw material delivery",
            }
        ],
    }

    resp = client.post("/simulations/disruptions", json=sim_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_feasible"] is True
    assert data["new_makespan"] == 210  # 180 + 30
    assert "t1" in data["affected_tasks"]

    # Test reactive reschedule
    resched_payload = {
        "tenant_id": "tenant_sim",
        "schedule_id": "sched_base_01",
        "disruptions": [
            {
                "disruption_type": "task_delay",
                "task_id": "t1",
                "delay_minutes": 45,
            }
        ],
        "stability_weight": 2.0,
    }
    resched_resp = client.post("/simulations/reschedule", json=resched_payload)
    assert resched_resp.status_code == 200
    assert resched_resp.json()["makespan"] == 525  # 480 + 45


def test_bolt_api_visualizations_endpoints(client):
    """Verify HTML and SVG visual renderers."""
    # Stripboard HTML & SVG
    strip_data = {
        "project_title": "Unit Test Film Shoot",
        "total_shoot_days": 1,
        "days": [
            {
                "day_number": 1,
                "date": "2026-11-10",
                "total_pages_eighths": 16,
                "total_estimated_minutes": 240,
                "strips": [
                    {
                        "scene_number": "1",
                        "setting": "INT",
                        "time_of_day": "DAY",
                        "synopsis": "Opening meeting",
                        "location_name": "Studio A",
                        "character_numbers": [1, 2],
                        "pages_eighths": 8,
                    }
                ],
            }
        ],
    }
    resp_sb_html = client.post(
        "/visualizations/stripboards/html", json={"stripboard_data": strip_data}
    )
    assert resp_sb_html.status_code == 200
    assert "<div" in resp_sb_html.json()["html"]
    assert "DAY 1" in resp_sb_html.json()["html"]

    resp_sb_svg = client.post(
        "/visualizations/stripboards/svg", json={"stripboard_data": strip_data, "width": 750}
    )
    assert resp_sb_svg.status_code == 200
    assert "<svg" in resp_sb_svg.json()["svg"]

    # DOOD HTML
    dood_reports = [
        {
            "talent_id": "cast_1",
            "character_name": "Alice",
            "daily_status": {"1": "SW", "2": "W", "3": "WF"},
            "total_work_days": 3,
            "total_hold_days": 0,
            "total_paid_days": 3,
            "total_cost": 3000.0,
        }
    ]
    resp_dood = client.post(
        "/visualizations/dood-reports", json={"reports": dood_reports, "total_days": 3}
    )
    assert resp_dood.status_code == 200
    assert "Alice" in resp_dood.json()["html"]

    # Gantt SVG
    gantt_payload = {
        "tasks": [{"id": "t1", "resource": "M1", "start": 0, "end": 120}],
        "resources": ["M1"],
        "total_makespan": 120,
    }
    resp_gantt = client.post("/visualizations/gantt-charts", json=gantt_payload)
    assert resp_gantt.status_code == 200
    assert "<svg" in resp_gantt.json()["svg"]

    # Report Export HTML
    report_payload = {
        "title": "Comprehensive Optimization Report",
        "sections": ["<h3>Section 1</h3><p>Details</p>"],
    }
    resp_report = client.post("/visualizations/reports", json=report_payload)
    assert resp_report.status_code == 200
    assert "<!DOCTYPE html>" in resp_report.json()["html"]


def test_bolt_api_calendars_endpoints(client):
    """Verify cultural Panchang and standard blackout interval calculations."""
    cult_resp = client.post(
        "/calendars/cultural/intervals",
        json={"horizon_days": 7, "enable_rahu_kalam": True, "enable_yamagandam": True},
    )
    assert cult_resp.status_code == 200
    cult_data = cult_resp.json()
    assert len(cult_data["blackout_windows"]) > 0

    std_resp = client.post(
        "/calendars/standard/blackouts",
        json={
            "horizon_days": 7,
            "working_day_start_minute": 540,
            "working_day_end_minute": 1020,
            "weekend_days": [5, 6],
        },
    )
    assert std_resp.status_code == 200
    assert len(std_resp.json()["blackout_windows"]) > 0


def test_bolt_api_adapters_manufacturing(client):
    """Verify domain adapter optimization for manufacturing job shop."""
    mfg_payload = {
        "machines": [{"id": "m1", "name": "Lathe", "capacity": 1, "hourly_rate_cents": 4000}],
        "jobs": [
            {
                "id": "job_1",
                "name": "Gear",
                "operations": [
                    {
                        "id": "op_1",
                        "job_id": "job_1",
                        "sequence_index": 0,
                        "machine_id": "m1",
                        "duration_minutes": 45,
                    }
                ],
            }
        ],
        "max_time_seconds": 3.0,
    }
    resp = client.post("/adapters/manufacturing/optimize", json=mfg_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"].upper() in ("OPTIMAL", "FEASIBLE")
    assert data["makespan"] == 45


def test_bolt_api_adapters_workforce(client):
    """Verify domain adapter optimization for workforce shift scheduling."""
    wf_payload = {
        "staff": [{"id": "nurse_1", "name": "Nurse Joy", "hourly_rate_cents": 5000}],
        "shifts": [
            {
                "id": "shift_morning",
                "name": "Morning Shift",
                "start_minute": 480,
                "duration_minutes": 480,
            }
        ],
        "max_time_seconds": 3.0,
    }
    resp = client.post("/adapters/workforce/optimize", json=wf_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"].upper() in ("OPTIMAL", "FEASIBLE")


def test_bolt_api_adapters_film(client):
    """Verify domain adapter optimization for film shooting schedule."""
    film_dataset = ProductionDataset(
        project_title="Teaser Shoot",
        max_shooting_days=3,
        talents=[Talent(id="actor_1", name="Lead Actor", daily_rate_cents=500000)],
        scenes=[
            Scene(
                id="sc_1",
                scene_number="1",
                duration_minutes=180,
                required_cast=["actor_1"],
            )
        ],
    )
    import msgspec

    payload = msgspec.to_builtins(film_dataset)
    resp = client.post("/adapters/film-production/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_feasible"] is True
    assert "stripboard" in data
    assert "dood_reports" in data


def test_bolt_api_scenarios_generate_and_records(client):
    """Verify synthetic scenario generation and record queries."""
    # 1. Generate scenario
    gen_resp = client.post(
        "/scenarios/generate",
        json={"scenario_type": "jobshop", "num_jobs": 4, "num_machines": 3, "seed": 42},
    )
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["scenario_type"] == "jobshop"
    assert gen_data["tasks_count"] > 0
    assert gen_data["resources_count"] == 3

    # 2. List scenario records via ModelViewSet
    record = ScenarioRecord.objects.create(
        tenant_id="tenant_scen_test",
        name="test_bench_scenario",
        domain="manufacturing",
        scale="small",
    )
    rec_resp = client.get("/scenarios?tenant_id=tenant_scen_test")
    assert rec_resp.status_code == 200
    records = rec_resp.json()
    assert records["total"] >= 1
    assert records["items"][0]["name"] == "test_bench_scenario"

    # 3. Retrieve scenario record
    detail_resp = client.get(f"/scenarios/{record.id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["name"] == "test_bench_scenario"
