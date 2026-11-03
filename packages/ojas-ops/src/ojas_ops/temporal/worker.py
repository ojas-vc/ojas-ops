"""Temporal worker runner with process-separated workflow and activity pools."""

import asyncio
import concurrent.futures
import multiprocessing
from typing import Literal

from temporalio.client import Client
from temporalio.worker import Worker

from ojas_ops.temporal.activities import (
    persist_schedule_run_activity,
    run_cp_sat_solver_activity,
    validate_schedule_activity,
)
from ojas_ops.temporal.converter import get_ojas_ops_data_converter
from ojas_ops.temporal.workflows import (
    FilmScheduleApprovalWorkflow,
    ScheduleOptimizationWorkflow,
)

WORKFLOW_TASK_QUEUE = "ojas-ops-workflows"
SOLVER_ACTIVITY_TASK_QUEUE = "ojas-ops-solver-activities"


async def start_worker(
    worker_type: Literal["workflow", "activity", "all"],
    *,
    host: str = "localhost:7233",
    namespace: str = "default",
    worker_id: int = 0,
) -> None:
    """Connects to Temporal server and runs workers on designated queues."""
    data_converter = get_ojas_ops_data_converter()
    client = await Client.connect(
        host,
        namespace=namespace,
        data_converter=data_converter,
    )

    workers: list[Worker] = []

    if worker_type in ("workflow", "all"):
        wf_worker = Worker(
            client,
            task_queue=WORKFLOW_TASK_QUEUE,
            workflows=[ScheduleOptimizationWorkflow, FilmScheduleApprovalWorkflow],
            identity=f"ojas-ops-wf-worker-{worker_id}",
        )
        workers.append(wf_worker)

    if worker_type in ("activity", "all"):
        act_worker = Worker(
            client,
            task_queue=SOLVER_ACTIVITY_TASK_QUEUE,
            activities=[
                run_cp_sat_solver_activity,
                validate_schedule_activity,
                persist_schedule_run_activity,
            ],
            identity=f"ojas-ops-act-worker-{worker_id}",
        )
        workers.append(act_worker)

    await asyncio.gather(*(w.run() for w in workers))


def _process_worker_entry(
    worker_type: Literal["workflow", "activity"],
    worker_id: int,
    host: str,
    namespace: str,
) -> None:
    """Subprocess target executing a single isolated worker loop."""
    asyncio.run(start_worker(worker_type, host=host, namespace=namespace, worker_id=worker_id))


def run_worker_cluster(
    *,
    host: str = "localhost:7233",
    namespace: str = "default",
    num_wf_workers: int = 2,
    num_act_workers: int = 2,
) -> None:
    """Launches dedicated workflow and multi-core activity worker pools."""
    total_workers = num_wf_workers + num_act_workers
    mp_ctx = multiprocessing.get_context("spawn")

    with concurrent.futures.ProcessPoolExecutor(total_workers, mp_context=mp_ctx) as executor:
        futures = [
            executor.submit(_process_worker_entry, "workflow", i, host, namespace)
            for i in range(num_wf_workers)
        ]
        futures.extend(
            [
                executor.submit(_process_worker_entry, "activity", j, host, namespace)
                for j in range(num_act_workers)
            ]
        )
        concurrent.futures.wait(futures)
