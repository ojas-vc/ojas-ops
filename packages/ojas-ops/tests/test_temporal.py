"""Unit and integration tests for Temporal.io durable orchestration and custom converter."""

import asyncio

import msgspec
from ojas_ops.schemas.scheduling import (
    HorizonContract,
    OptimizeScheduleRequest,
    ResourceContract,
    SolveStrategy,
    TaskContract,
    ValidateScheduleRequest,
)
from ojas_ops.temporal.activities import (
    TemporalHeartbeatCallback,
    persist_schedule_run_activity,
    run_cp_sat_solver_activity,
    validate_schedule_activity,
)
from ojas_ops.temporal.converter import (
    MsgspecEncodingPayloadConverter,
    OjasOpsPayloadConverter,
    get_ojas_ops_data_converter,
)
from ojas_ops.temporal.workflows import (
    FilmScheduleApprovalWorkflow,
    ScheduleOptimizationWorkflow,
)
from temporalio.testing import ActivityEnvironment


class SampleStruct(msgspec.Struct):
    id: str
    count: int


def test_msgspec_payload_converter():
    converter = MsgspecEncodingPayloadConverter()
    item = SampleStruct(id="item_123", count=42)

    # Convert to Payload
    payload = converter.to_payload(item)
    assert payload is not None
    assert payload.metadata["encoding"] == b"application/x-msgspec-json"

    # Convert back with type hint
    decoded = converter.from_payload(payload, type_hint=SampleStruct)
    assert isinstance(decoded, SampleStruct)
    assert decoded.id == "item_123"
    assert decoded.count == 42

    # Non-struct handling
    assert converter.to_payload("plain string") is None


def test_ojas_ops_data_converter():
    data_converter = get_ojas_ops_data_converter()
    assert isinstance(data_converter.payload_converter_class(), OjasOpsPayloadConverter)


def test_run_cp_sat_solver_activity():
    async def _run():
        env = ActivityEnvironment()
        request = OptimizeScheduleRequest(
            tenant_id="tenant_temporal",
            project_id="proj_temporal",
            horizon=HorizonContract(start=0, end=1440),
            tasks=[
                TaskContract(
                    id="T1",
                    name="Task 1",
                    duration=60,
                    required_resources=["R1"],
                ),
                TaskContract(
                    id="T2",
                    name="Task 2",
                    duration=40,
                    required_resources=["R1"],
                    dependencies=["T1"],
                ),
            ],
            resources=[
                ResourceContract(
                    id="R1",
                    name="Machine 1",
                    capacity=1,
                )
            ],
            strategy=SolveStrategy.BALANCED,
            max_time_seconds=5.0,
        )

        response = await env.run(run_cp_sat_solver_activity, request)
        assert response.schedule_id == "sched-proj_temporal"
        assert response.makespan == 100
        assert response.tasks_scheduled_count == 2

    asyncio.run(_run())


def test_validate_schedule_activity():
    async def _run():
        env = ActivityEnvironment()
        req = ValidateScheduleRequest(
            tenant_id="tenant_temporal",
            schedule_id="sched_temp_01",
            tasks=[],
            resources=[],
            result=None,  # type: ignore
            horizon=HorizonContract(start=0, end=1440),
        )
        res = await env.run(validate_schedule_activity, req)
        assert res.schedule_id == "sched_temp_01"
        assert res.is_valid is True

    asyncio.run(_run())


def test_persist_schedule_run_activity():
    async def _run():
        env = ActivityEnvironment()
        from ojas_ops.schemas.schedule import ScheduleResult, ScheduleStatus
        from ojas_ops.schemas.scheduling import OptimizeScheduleResponse

        dummy_result = ScheduleResult(
            status=ScheduleStatus.OPTIMAL,
            makespan=100,
            objective_value=10000.0,
        )

        resp = OptimizeScheduleResponse(
            schedule_id="sched_persisted",
            status=ScheduleStatus.OPTIMAL,
            makespan=100,
            objective_value=10000.0,
            solve_time_seconds=0.05,
            tasks_scheduled_count=2,
            result=dummy_result,
        )

        result = await env.run(persist_schedule_run_activity, resp)
        assert "schedule_id" in result or "schedule_run_id" in result

    asyncio.run(_run())


def test_temporal_heartbeat_callback():
    cb = TemporalHeartbeatCallback(heartbeat_interval_seconds=0.0)
    assert cb.solution_found_count == 0
    # Simulate on_solution_callback
    cb.solution_found_count += 1
    assert cb.solution_found_count == 1


def test_workflow_definitions():
    wf_opt = ScheduleOptimizationWorkflow()
    assert wf_opt.status == "INITIALIZING"
    status = wf_opt.get_status()
    assert status["status"] == "INITIALIZING"
    assert status["is_cancelled"] is False

    wf_opt.cancel_solve()
    assert wf_opt.is_cancelled is True
    assert wf_opt.status == "CANCELLING"

    wf_hitl = FilmScheduleApprovalWorkflow()
    assert wf_hitl.status == "INITIALIZING"
    assert wf_hitl.decision is None
    wf_hitl.submit_review_decision("APPROVED", notes="Looks great")
    assert wf_hitl.decision == "APPROVED"
    assert wf_hitl.reviewer_notes == "Looks great"
    state = wf_hitl.get_review_state()
    assert state["decision"] == "APPROVED"
    assert state["notes"] == "Looks great"
