"""Unit tests for strictly typed, contract-first schemas and boundaries."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import msgspec
import pytest
from ojas_ops import schemas
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.schedule import ScheduleResult, ScheduleStatus
from ojas_ops.models.task import TaskPriority
from ojas_ops.schemas import (
    APIError,
    Contract,
    DisruptionContract,
    DisruptionInjectedEvent,
    DisruptionInjectedPayload,
    DisruptionType,
    DomainEvent,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    EventMetadata,
    HorizonContract,
    OptimizeScheduleRequest,
    PaginationQuery,
    ResourceContract,
    ScheduleOptimizedEvent,
    ScheduleOptimizedPayload,
    SimulateDisruptionRequest,
    SolveStrategy,
    TaskContract,
    ValueObject,
)


def test_base_contract_forbids_unknown_fields():
    class TestContract(Contract):
        name: str

    # Valid payload
    valid = msgspec.json.decode(b'{"name": "valid"}', type=TestContract)
    assert valid.name == "valid"

    # Unknown field must be rejected
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(b'{"name": "valid", "extra_field": 123}', type=TestContract)


def test_value_object_immutability():
    class TestValueObject(ValueObject):
        id: str
        value: int

    vo = TestValueObject(id="vo-1", value=100)
    assert vo.id == "vo-1"
    with pytest.raises(AttributeError):
        vo.value = 200  # type: ignore[misc]


def test_validated_identifiers_and_constraints():
    class EntityContract(Contract):
        id: schemas.TaskId
        duration: schemas.DurationMinutes
        capacity: schemas.PositiveCapacity

    # Valid entity
    valid = EntityContract(id="task_01-alpha", duration=120, capacity=2)
    assert valid.id == "task_01-alpha"

    # Invalid ID with illegal punctuation/spaces
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(
            b'{"id": "bad task id!", "duration": 10, "capacity": 1}',
            type=EntityContract,
        )

    # Negative duration must be rejected
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(
            b'{"id": "task-1", "duration": -5, "capacity": 1}',
            type=EntityContract,
        )

    # Zero capacity must be rejected (must be >= 1)
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(
            b'{"id": "task-1", "duration": 10, "capacity": 0}',
            type=EntityContract,
        )


def test_pagination_contract():
    query = PaginationQuery(limit=25, cursor="cursor_abc")
    encoded = msgspec.json.encode(query)
    decoded = msgspec.json.decode(encoded, type=PaginationQuery)
    assert decoded.limit == 25
    assert decoded.cursor == "cursor_abc"

    # Limit > 200 must fail
    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(b'{"limit": 500}', type=PaginationQuery)


def test_error_response_contract():
    err_detail = ErrorDetail(field="tasks[0].duration", code="MIN_VALUE", message="Must be >= 0")
    api_error = APIError(
        code=ErrorCode.VALIDATION_FAILED,
        message="Request payload failed schema validation",
        details=[err_detail],
    )
    response = ErrorResponse(error=api_error, request_id="req-12345", tenant_id="ten-42")

    encoded = msgspec.json.encode(response)
    decoded = msgspec.json.decode(encoded, type=ErrorResponse)

    assert decoded.request_id == "req-12345"
    assert decoded.error.code == ErrorCode.VALIDATION_FAILED
    assert len(decoded.error.details) == 1
    assert decoded.error.details[0].field == "tasks[0].duration"


def test_optimize_schedule_request_contract_roundtrip():
    task = TaskContract(
        id="task-job-1",
        duration=60,
        name="Rough Cut Lathe",
        cost_minor=50000,
        required_resources=["lathe-01"],
        dependencies=[],
        priority=TaskPriority.HIGH,
    )
    resource = ResourceContract(
        id="lathe-01",
        name="Engine Lathe Workstation",
        capacity=1,
        resource_type=ResourceType.MACHINE,
        cost_per_time_unit_minor=1500,
    )
    req = OptimizeScheduleRequest(
        tenant_id="tenant-acme",
        project_id="proj-machining-01",
        tasks=[task],
        resources=[resource],
        horizon=HorizonContract(start=0, end=480),
        strategy=SolveStrategy.BALANCED,
        max_time_seconds=10.0,
        random_seed=42,
    )

    encoded = msgspec.json.encode(req)
    decoder = msgspec.json.Decoder(type=OptimizeScheduleRequest, strict=True)
    decoded = decoder.decode(encoded)

    assert decoded.tenant_id == "tenant-acme"
    assert len(decoded.tasks) == 1
    assert decoded.tasks[0].cost_minor == 50000
    assert decoded.resources[0].resource_type == ResourceType.MACHINE
    assert decoded.horizon.end == 480


def test_simulation_and_disruption_contracts():
    disruption = DisruptionContract(
        disruption_type=DisruptionType.RESOURCE_BREAKDOWN,
        resource_id="press-01",
        blackout_start=120,
        blackout_end=180,
        description="Hydraulic pressure failure",
    )
    baseline = ScheduleResult(status=ScheduleStatus.OPTIMAL, makespan=360)
    req = SimulateDisruptionRequest(
        tenant_id="tenant-fab",
        schedule_id="sched-888",
        baseline_schedule=baseline,
        disruptions=[disruption],
        current_time=60,
    )

    encoded = msgspec.json.encode(req)
    decoded = msgspec.json.decode(encoded, type=SimulateDisruptionRequest)

    assert decoded.schedule_id == "sched-888"
    assert decoded.disruptions[0].disruption_type == DisruptionType.RESOURCE_BREAKDOWN
    assert decoded.disruptions[0].blackout_start == 120


def test_polymorphic_domain_events_tagged_union():
    event_id = uuid4()
    now = datetime.now(UTC)
    meta = EventMetadata(
        event_id=event_id,
        event_type="schedule.optimized",
        event_version=1,
        tenant_id="ten-global",
        correlation_id="corr-999",
        occurred_at=now,
    )

    opt_payload = ScheduleOptimizedPayload(
        schedule_id="sched-101",
        project_id="proj-test",
        tenant_id="ten-global",
        status="optimal",
        makespan=240,
        objective_value=240.0,
        tasks_count=12,
        solve_time_seconds=0.15,
    )
    event1 = ScheduleOptimizedEvent(metadata=meta, data=opt_payload)

    # Encode and decode using polymorphic tagged union
    encoded1 = msgspec.json.encode(event1)
    decoded1 = msgspec.json.decode(encoded1, type=DomainEvent)
    assert isinstance(decoded1, ScheduleOptimizedEvent)
    assert decoded1.data.makespan == 240
    assert decoded1.data.status == "optimal"

    # Test disruption event
    disrupt_meta = EventMetadata(
        event_id=uuid4(),
        event_type="schedule.disruption_injected",
        event_version=1,
        tenant_id="ten-global",
        correlation_id="corr-888",
        occurred_at=now,
    )
    disrupt_payload = DisruptionInjectedPayload(
        schedule_id="sched-101",
        disrupted_task_id="task-5",
        delay_minutes=45,
    )
    event2 = DisruptionInjectedEvent(metadata=disrupt_meta, data=disrupt_payload)
    encoded2 = msgspec.json.encode(event2)
    decoded2 = msgspec.json.decode(encoded2, type=DomainEvent)
    assert isinstance(decoded2, DisruptionInjectedEvent)
    assert decoded2.data.delay_minutes == 45
