"""Durable Schedule Optimization Workflow."""

from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ojas_ops.schemas.scheduling import (
        OptimizeScheduleRequest,
        OptimizeScheduleResponse,
    )
    from ojas_ops.temporal.activities.persist_activity import (
        persist_schedule_run_activity,
    )
    from ojas_ops.temporal.activities.solve_activity import (
        run_cp_sat_solver_activity,
    )

SOLVER_TASK_QUEUE = "ojas-ops-solver-activities"


@workflow.defn(name="ScheduleOptimizationWorkflow")
class ScheduleOptimizationWorkflow:
    """Durable workflow orchestrating CP-SAT schedule optimization."""

    def __init__(self) -> None:
        self.status = "INITIALIZING"
        self.current_schedule_id: str | None = None
        self.result: OptimizeScheduleResponse | None = None
        self.is_cancelled = False

    @workflow.run
    async def run(
        self,
        request: OptimizeScheduleRequest,
    ) -> OptimizeScheduleResponse:
        self.current_schedule_id = request.schedule_id
        self.status = "SOLVING"

        time_limit = request.max_time_seconds or 30.0
        start_to_close = timedelta(seconds=max(60.0, time_limit * 2.0))

        # Invoke CPU-bound CP-SAT solver activity on dedicated solver queue
        self.result = await workflow.execute_activity(
            run_cp_sat_solver_activity,
            request,
            task_queue=SOLVER_TASK_QUEUE,
            start_to_close_timeout=start_to_close,
            heartbeat_timeout=timedelta(seconds=15),
        )

        self.status = "PERSISTING"
        await workflow.execute_activity(
            persist_schedule_run_activity,
            self.result,
            start_to_close_timeout=timedelta(minutes=1),
        )

        self.status = "COMPLETED"
        return self.result

    @workflow.query
    def get_status(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "schedule_id": self.current_schedule_id,
            "is_cancelled": self.is_cancelled,
            "has_result": self.result is not None,
        }

    @workflow.signal
    def cancel_solve(self) -> None:
        self.is_cancelled = True
        self.status = "CANCELLING"
