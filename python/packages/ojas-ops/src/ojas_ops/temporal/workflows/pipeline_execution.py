"""Durable Temporal Workflow orchestrating multi-stage instruction-driven pipelines with HITL gates."""

from datetime import timedelta
from typing import Any, Optional

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ojas_ops.pipelines.checkpoint import (
        get_completed_stages,
        read_checkpoint,
        write_checkpoint,
    )
    from ojas_ops.pipelines.loader import load_pipeline_manifest
    from ojas_ops.temporal.activities.agent_activity import (
        execute_agent_stage_activity,
    )

WORKFLOW_TASK_QUEUE = "ojas-ops-workflows"


@workflow.defn(name="PipelineExecutionWorkflow")
class PipelineExecutionWorkflow:
    """Orchestrates instruction-driven stages, Claude director reasoning, and durable HITL sign-offs."""

    def __init__(self) -> None:
        self.status = "INITIALIZING"
        self.current_stage: Optional[str] = None
        self.completed_stages: list[str] = []
        self.approval_decision: Optional[str] = None
        self.approval_notes: Optional[str] = None
        self.approval_overrides: Optional[dict[str, Any]] = None
        self.project_id: str = ""
        self.tenant_id: str = "default"
        self.pipeline_name: str = ""
        self.error_message: Optional[str] = None

    @workflow.run
    async def run(
        self,
        payload: dict[str, Any],
        approval_timeout_hours: int = 72,
    ) -> dict[str, Any]:
        self.tenant_id = payload.get("tenant_id", "default")
        self.project_id = payload.get("project_id", "")
        self.pipeline_name = payload.get("pipeline_name", "")
        ruleset_name = payload.get("ruleset_name")
        initial_inputs = payload.get("initial_inputs", {})

        manifest = load_pipeline_manifest(self.pipeline_name)
        stages = manifest.get("stages", [])
        context_data = dict(initial_inputs)

        # Check existing completed checkpoints to support workflow resume / replay
        completed = set(get_completed_stages(self.tenant_id, self.project_id, self.pipeline_name))
        self.completed_stages = list(completed)

        for stage_def in stages:
            stage_name = stage_def.get("name", "")
            if stage_name in completed:
                # Merge existing artifacts into context
                existing_cp = read_checkpoint(self.tenant_id, self.project_id, stage_name)
                if existing_cp and "artifacts" in existing_cp:
                    context_data.update(existing_cp["artifacts"])
                continue

            self.current_stage = stage_name
            self.status = f"RUNNING_{stage_name.upper()}"

            stage_payload = {
                "tenant_id": self.tenant_id,
                "project_id": self.project_id,
                "pipeline_name": self.pipeline_name,
                "stage_name": stage_name,
                "stage_def": stage_def,
                "ruleset_name": ruleset_name,
                "context_data": context_data,
                "revision_notes": None,
            }

            # Loop for stage execution & potential revision cycles
            while True:
                stage_result = await workflow.execute_activity(
                    execute_agent_stage_activity,
                    stage_payload,
                    task_queue=WORKFLOW_TASK_QUEUE,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=workflow.RetryPolicy(maximum_attempts=3),
                )

                # Merge newly produced artifacts into running context
                produced_artifacts = stage_result.get("artifacts", {})
                context_data.update(produced_artifacts)

                # Check if human approval gate is required
                if stage_result.get("status") == "awaiting_human":
                    self.status = "AWAITING_HUMAN_APPROVAL"
                    self.approval_decision = None

                    try:
                        await workflow.wait_condition(
                            lambda: self.approval_decision is not None,
                            timeout=timedelta(hours=approval_timeout_hours),
                        )
                    except TimeoutError:
                        self.status = "TIMED_OUT"
                        self.error_message = f"Approval for stage {stage_name} timed out after {approval_timeout_hours} hours"
                        return {
                            "status": "TIMED_OUT",
                            "stage": stage_name,
                            "project_id": self.project_id,
                            "completed_stages": self.completed_stages,
                        }

                    if self.approval_decision == "APPROVED":
                        # Record human approval in checkpoint
                        write_checkpoint(
                            tenant_id=self.tenant_id,
                            project_id=self.project_id,
                            stage=stage_name,
                            status="completed",
                            artifacts=produced_artifacts,
                            pipeline_type=self.pipeline_name,
                            ruleset=ruleset_name,
                            human_approval_required=True,
                            human_approved=True,
                            metadata={"approval_notes": self.approval_notes or ""},
                        )
                        self.completed_stages.append(stage_name)
                        break
                    elif self.approval_decision == "REVISED":
                        # Prepare payload with revision notes and retry stage
                        stage_payload["revision_notes"] = self.approval_notes
                        self.approval_decision = None
                        self.status = f"REVISING_{stage_name.upper()}"
                        continue
                    else:
                        self.status = "REJECTED"
                        return {
                            "status": "REJECTED",
                            "stage": stage_name,
                            "project_id": self.project_id,
                            "notes": self.approval_notes,
                            "completed_stages": self.completed_stages,
                        }
                else:
                    self.completed_stages.append(stage_name)
                    break

        self.status = "COMPLETED"
        return {
            "status": "COMPLETED",
            "project_id": self.project_id,
            "tenant_id": self.tenant_id,
            "pipeline": self.pipeline_name,
            "completed_stages": self.completed_stages,
        }

    @workflow.signal
    def submit_human_approval(
        self,
        decision: str,
        notes: Optional[str] = None,
        overrides: Optional[dict[str, Any]] = None,
    ) -> None:
        """Signal invoked by human operator (Approve, Revise, Reject)."""
        self.approval_decision = decision.upper()
        self.approval_notes = notes
        self.approval_overrides = overrides

    @workflow.signal
    def request_stage_revision(self, notes: str) -> None:
        """Convenience signal to trigger immediate stage revision with directives."""
        self.approval_decision = "REVISED"
        self.approval_notes = notes

    @workflow.query
    def get_workflow_state(self) -> dict[str, Any]:
        """Query returning live workflow state for UI and client inspection."""
        return {
            "status": self.status,
            "project_id": self.project_id,
            "tenant_id": self.tenant_id,
            "pipeline": self.pipeline_name,
            "current_stage": self.current_stage,
            "completed_stages": self.completed_stages,
            "error_message": self.error_message,
        }

