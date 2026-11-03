"""Temporal activity executing CPU-bound CP-SAT schedule optimization with solution heartbeating."""

import time

from ortools.sat.python import cp_model
from temporalio import activity

from ojas_ops.schemas.scheduling import (
    OptimizeScheduleRequest,
    OptimizeScheduleResponse,
)
from ojas_ops.services.optimizer import solve_schedule_service


class TemporalHeartbeatCallback(cp_model.CpSolverSolutionCallback):
    """Callback providing real-time bound heartbeats back to Temporal server."""

    def __init__(self, heartbeat_interval_seconds: float = 5.0) -> None:
        super().__init__()
        self.interval = heartbeat_interval_seconds
        self.last_heartbeat = time.time()
        self.solution_found_count = 0

    def on_solution_callback(self) -> None:
        self.solution_found_count += 1
        now = time.time()
        if now - self.last_heartbeat >= self.interval:
            try:
                activity.heartbeat(
                    {
                        "incumbent_objective": int(self.ObjectiveValue()),
                        "best_bound": int(self.BestObjectiveBound()),
                        "solutions_found": self.solution_found_count,
                        "wall_time": self.WallTime(),
                    }
                )
                self.last_heartbeat = now
            except Exception:
                # May be running outside Temporal activity context (e.g. testing)
                pass


@activity.defn(name="run_cp_sat_solver_activity")
async def run_cp_sat_solver_activity(
    request: OptimizeScheduleRequest,
) -> OptimizeScheduleResponse:
    """Activity executing CP-SAT combinatorial solve with heartbeat progress."""
    sched_id = f"sched-{request.project_id}"
    activity.heartbeat({"status": "STARTED", "schedule_id": sched_id})
    response = await solve_schedule_service(request)
    activity.heartbeat({"status": "COMPLETED", "schedule_id": sched_id})
    return response
