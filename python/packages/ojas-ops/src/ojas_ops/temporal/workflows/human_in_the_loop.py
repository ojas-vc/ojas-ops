"""Human-in-the-Loop review and approval workflow for production schedules."""

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


@workflow.defn(name="FilmScheduleApprovalWorkflow")
class FilmScheduleApprovalWorkflow:
    """Workflow requiring human approval before finalizing high-cost or disrupted schedules."""

    def __init__(self) -> None:
        self.decision: str | None = None
        self.reviewer_notes: str | None = None
        self.result: OptimizeScheduleResponse | None = None
        self.status = "INITIALIZING"

    @workflow.run
    async def run(
        self,
        request: OptimizeScheduleRequest,
        approval_timeout_hours: int = 24,
    ) -> dict[str, Any]:
        self.status = "OPTIMIZING"

        time_limit = request.max_time_seconds or 30.0
        start_to_close = timedelta(seconds=max(60.0, time_limit * 2.0))

        self.result = await workflow.execute_activity(
            run_cp_sat_solver_activity,
            request,
            task_queue=SOLVER_TASK_QUEUE,
            start_to_close_timeout=start_to_close,
            heartbeat_timeout=timedelta(seconds=15),
        )

        self.status = "AWAITING_HUMAN_APPROVAL"

        # Wait for human signal or timeout
        try:
            await workflow.wait_condition(
                lambda: self.decision is not None,
                timeout=timedelta(hours=approval_timeout_hours),
            )
        except TimeoutError:
            self.status = "TIMED_OUT"
            return {
                "status": "TIMED_OUT",
                "action": "AUTO_REJECTED",
                "schedule_id": request.schedule_id,
            }

        if self.decision == "APPROVED":
            self.status = "APPROVED"
            await workflow.execute_activity(
                persist_schedule_run_activity,
                self.result,
                start_to_close_timeout=timedelta(minutes=1),
            )
            return {
                "status": "APPROVED",
                "notes": self.reviewer_notes,
                "schedule_id": request.schedule_id,
                "makespan": self.result.makespan,
            }
        else:
            self.status = "REJECTED"
            return {
                "status": "REJECTED",
                "notes": self.reviewer_notes,
                "schedule_id": request.schedule_id,
            }

    @workflow.signal
    def submit_review_decision(self, decision: str, notes: str | None = None) -> None:
        """Signal method called by human reviewer (e.g. Line Producer)."""
        self.decision = decision
        self.reviewer_notes = notes

    @workflow.query
    def get_review_state(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "decision": self.decision,
            "notes": self.reviewer_notes,
            "has_solution": self.result is not None,
        }
