"""Temporal workflow request and response DTO schemas."""

import msgspec


class WorkflowSignalRequest(msgspec.Struct, kw_only=True):
    """Review decision signal sent to a running Human-in-the-Loop workflow."""

    decision: str = "APPROVED"  # APPROVED or REJECTED
    notes: str | None = None


class WorkflowSignalResponse(msgspec.Struct, kw_only=True):
    """Result of signaling a Temporal workflow."""

    workflow_id: str
    status: str
    signal_sent: bool
    error: str | None = None


class WorkflowJobSummary(msgspec.Struct, kw_only=True):
    """Summary of an optimization job record."""

    id: int
    tenant_id: str
    workflow_id: str
    status: str
    progress_basis_points: int = 0
    incumbent_objective: int | None = None
    created_at: str


class ListWorkflowJobsResponse(msgspec.Struct, kw_only=True):
    """List of active or recent workflow jobs."""

    jobs: list[WorkflowJobSummary]
    total: int
