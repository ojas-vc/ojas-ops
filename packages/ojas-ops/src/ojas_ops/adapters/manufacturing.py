"""Manufacturing and industrial job shop scheduling adapter."""

from __future__ import annotations

import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import TimeWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.objectives.tardiness import MinimizeTardinessObjective
from ojas_ops.scheduling.scheduler import Scheduler


class Operation(msgspec.Struct, kw_only=True):
    """A processing step on a specific machine."""

    id: str
    job_id: str
    sequence_index: int
    machine_id: str
    duration_minutes: int
    product_family: str = "default"


class ProductionJob(msgspec.Struct, kw_only=True):
    """An order or job comprising ordered sequential operations."""

    id: str
    name: str = ""
    due_date: int | None = None
    priority: TaskPriority = TaskPriority.NORMAL
    operations: list[Operation] = msgspec.field(default_factory=list)


class Machine(msgspec.Struct, kw_only=True):
    """A production machine or workstation."""

    id: str
    name: str = ""
    capacity: int = 1
    hourly_rate: float = 0.0


class ManufacturingScheduler(DomainAdapter):
    """Job shop and flow shop production scheduler with sequence-dependent changeovers."""

    def __init__(self) -> None:
        self.machines: dict[str, Machine] = {}
        self.jobs: dict[str, ProductionJob] = {}
        self.setup_matrix: dict[
            tuple[str, str, str], int
        ] = {}  # (machine_id, from_fam, to_fam) -> setup_time

    def add_machine(
        self,
        id: str,
        name: str = "",
        capacity: int = 1,
        hourly_rate: float = 0.0,
    ) -> Machine:
        m = Machine(id=id, name=name or id, capacity=capacity, hourly_rate=hourly_rate)
        self.machines[id] = m
        return m

    def add_job(
        self,
        id: str,
        name: str = "",
        due_date: int | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> ProductionJob:
        job = ProductionJob(id=id, name=name or id, due_date=due_date, priority=priority)
        self.jobs[id] = job
        return job

    def add_operation(
        self,
        job_id: str,
        operation_id: str,
        machine_id: str,
        duration_minutes: int,
        product_family: str = "default",
    ) -> Operation:
        if job_id not in self.jobs:
            msg = f"Job '{job_id}' does not exist"
            raise ValueError(msg)

        job = self.jobs[job_id]
        op = Operation(
            id=operation_id,
            job_id=job_id,
            sequence_index=len(job.operations),
            machine_id=machine_id,
            duration_minutes=duration_minutes,
            product_family=product_family,
        )
        job.operations.append(op)
        return op

    def set_family_setup_time(
        self,
        machine_id: str,
        from_family: str,
        to_family: str,
        setup_minutes: int,
    ) -> None:
        self.setup_matrix[(machine_id, from_family, to_family)] = setup_minutes

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()

        # 1. Add machines as resources
        for m_id, machine in self.machines.items():
            scheduler.add_resource(
                id=m_id,
                name=machine.name,
                capacity=machine.capacity,
                resource_type=ResourceType.MACHINE,
                cost_per_time_unit=machine.hourly_rate / 60.0 if machine.hourly_rate else 0.0,
            )

        # 2. Add operations as tasks with within-job precedence
        all_ops: dict[str, Operation] = {}
        for _job_id, job in self.jobs.items():
            time_window = TimeWindow(deadline=job.due_date) if job.due_date else None
            prev_op_id: str | None = None

            for op in job.operations:
                all_ops[op.id] = op
                deps = [prev_op_id] if prev_op_id else []
                scheduler.add_task(
                    id=op.id,
                    duration=op.duration_minutes,
                    name=f"{job.name} - Op {op.sequence_index + 1}",
                    required_resources=[op.machine_id],
                    dependencies=deps,
                    priority=job.priority,
                    time_window=time_window if op == job.operations[-1] else None,
                )
                prev_op_id = op.id

        # 3. Add sequence-dependent family setup times on each machine
        for m_id in self.machines:
            m_ops = [op for op in all_ops.values() if op.machine_id == m_id]
            if len(m_ops) > 1:
                trans_matrix: dict[tuple[str, str], int] = {}
                for op1 in m_ops:
                    for op2 in m_ops:
                        if op1.id != op2.id:
                            setup = self.setup_matrix.get(
                                (m_id, op1.product_family, op2.product_family), 0
                            )
                            if setup > 0:
                                trans_matrix[(op1.id, op2.id)] = setup
                if trans_matrix:
                    scheduler.add_transition_matrix(
                        resource_id=m_id,
                        transition_matrix=trans_matrix,
                        default_buffer=0,
                    )

        # 4. Objective: minimize makespan and tardiness
        objectives = [
            MinimizeMakespanObjective(weight=1.0),
            MinimizeTardinessObjective(weight=2.0),
        ]
        scheduler.minimize(WeightedCompositeObjective(objectives))

        return scheduler
