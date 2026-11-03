"""Integration test suite for Ojas Ops Django-Bolt API in sandbox environment."""

import uuid

import pytest
from django_bolt.testing import TestClient
from ojas_ops.api import api
from ojas_ops.models.disruption_log import DisruptionLog
from ojas_ops.models.optimization_job import OptimizationJob
from ojas_ops.models.scenario_record import ScenarioRecord
from ojas_ops.models.schedule_run import ScheduleRun


@pytest.fixture
def client():
    return TestClient(api)


def test_sandbox_health_endpoints(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "ojas-ops"

    res_ready = client.get("/readyz")
    assert res_ready.status_code == 200
    ready_data = res_ready.json()
    assert ready_data["ready"] == "true"
    assert ready_data["engine"] == "google-ortools-cp-sat"


def test_sandbox_schedules_optimize_sync(client):
    payload = {
        "tenant_id": "test_tenant",
        "project_id": "sandbox_proj",
        "horizon": {"start": 0, "end": 1440},
        "resources": [
            {
                "id": "R1",
                "name": "Machine 1",
                "capacity": 1,
                "cost_per_time_unit_minor": 100,
            }
        ],
        "tasks": [
            {
                "id": "T1",
                "name": "Task 1",
                "duration": 60,
                "required_resources": ["R1"],
            },
            {
                "id": "T2",
                "name": "Task 2",
                "duration": 90,
                "required_resources": ["R1"],
                "dependencies": ["T1"],
            },
        ],
        "strategy": "balanced",
        "max_time_seconds": 5.0,
    }

    res = client.post("/schedules/optimize/sync", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["schedule_id"] == "sched-sandbox_proj"
    assert data["status"].upper() in ("OPTIMAL", "FEASIBLE")
    assert data["makespan"] == 150
    assert data["tasks_scheduled_count"] == 2


def test_sandbox_scenarios_run(client):
    payload = {
        "metadata": {
            "name": "sandbox_scenario",
            "description": "Sandbox scenario benchmark",
            "domain": "manufacturing",
        },
        "resources": [
            {
                "id": "res_1",
                "name": "Mill",
                "capacity": 1,
                "cost_per_hour_cents": 5000,
            }
        ],
        "tasks": [
            {
                "id": "task_1",
                "name": "Op 1",
                "duration": 30,
                "resource_requirements": [{"resource_id": "res_1", "quantity": 1}],
            }
        ],
    }
    res = client.post("/scenarios/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_success"] is True
    assert data["status"].upper() in ("OPTIMAL", "FEASIBLE")
    assert data["makespan"] == 30


def test_sandbox_workflow_status_not_found(client):
    res = client.get("/workflows/wf-nonexistent-000/status")
    assert res.status_code == 200
    data = res.json()
    assert data["workflow_id"] == "wf-nonexistent-000"
    assert data["status"] == "NOT_FOUND"


def test_sandbox_workflow_status_existing(client):
    wf_id = f"wf-sandbox-{uuid.uuid4()}"
    OptimizationJob.objects.create(
        tenant_id="tenant_x",
        temporal_workflow_id=wf_id,
        status="RUNNING",
        incumbent_objective=42000,
        best_bound=40000,
        progress_basis_points=8500,
    )
    res = client.get(f"/workflows/{wf_id}/status")
    assert res.status_code == 200
    data = res.json()
    assert data["workflow_id"] == wf_id
    assert data["status"] == "RUNNING"
    assert data["incumbent_objective"] == 42000
    assert data["best_bound"] == 40000
    assert data["progress_basis_points"] == 8500


def test_sandbox_database_persistence():
    record = ScenarioRecord.objects.create(
        name="test_persisted_scenario",
        domain="unit_test",
        scale="small",
        definition_json={"key": "value"},
    )
    assert record.id is not None
    assert record.created_at is not None

    run = ScheduleRun.objects.create(
        scenario_name="test_persisted_scenario",
        status="OPTIMAL",
        makespan=180,
        objective_value=18000,
    )
    assert run.id is not None
    assert ScheduleRun.objects.filter(scenario_name="test_persisted_scenario").exists()

    disruption = DisruptionLog.objects.create(
        schedule_run_id=f"run_{run.id}",
        disruption_type="MACHINE_BREAKDOWN",
        magnitude_minutes=60,
        affected_tasks=["task_1"],
    )
    assert disruption.id is not None


def test_sandbox_simulation_endpoints(client):
    sim_payload = {
        "tenant_id": "tenant_sandbox",
        "schedule_id": "sched_sb_01",
        "baseline_schedule": {
            "status": "optimal",
            "makespan": 120,
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
                "delay_minutes": 20,
                "description": "Late setup",
            }
        ],
    }
    resp = client.post("/simulation/simulate", json=sim_payload)
    assert resp.status_code == 200
    assert resp.json()["new_makespan"] == 140


def test_sandbox_visualizations(client):
    gantt_payload = {
        "tasks": [{"id": "t1", "resource": "res1", "start": 0, "end": 60}],
        "resources": ["res1"],
        "total_makespan": 60,
    }
    resp = client.post("/visualizations/gantt/svg", json=gantt_payload)
    assert resp.status_code == 200
    assert "<svg" in resp.json()["svg"]


def test_sandbox_calendars(client):
    resp = client.post(
        "/calendars/cultural/intervals",
        json={"horizon_days": 3},
    )
    assert resp.status_code == 200
    assert len(resp.json()["blackout_windows"]) > 0


def test_sandbox_scenarios_generate(client):
    resp = client.post(
        "/scenarios/generate",
        json={"scenario_type": "jobshop", "num_jobs": 3, "num_machines": 2},
    )
    assert resp.status_code == 200
    assert resp.json()["scenario_type"] == "jobshop"
