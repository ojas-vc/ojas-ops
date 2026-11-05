# Checkpoint Protocol & Governance Contract

## Purpose

Enforces the resumable state machine contract across all operational pipelines in `ojas-ops`.

## Checkpoint Rules

1. **Every Stage Emits a Checkpoint**:
   - Upon completing a stage, the agent or Temporal activity MUST call `write_checkpoint()`.
   - The checkpoint records stage name, status, timestamp, artifacts produced, review results, and metrics.

2. **Hard Gate Enforcement (`human_approval_default: true`)**:
   - If a stage defines `human_approval_default: true` in its pipeline manifest, it is a **GATED STAGE**.
   - The agent MUST NOT write `status: "completed"` without explicit evidence of approval (`human_approved=True`).
   - Gated protocol:
     1. Solve and validate the stage.
     2. Write checkpoint with `status: "awaiting_human"`, `human_approval_required=True`, `human_approved=False`.
     3. Present the executive summary and tradeoff matrix to the human user.
     4. Wait for approval.
     5. Only after the user confirms, rewrite checkpoint with `status: "completed"`, `human_approved=True`.

3. **Atomic Writes & Replay History**:
   - Checkpoints write to a temporary file before renaming to prevent corrupted half-writes.
   - Any superseded checkpoint is archived into `projects/<tenant_id>/<project_id>/history/` with a UTC timestamp for audit and replay.

4. **Resumption Protocol**:
   - When resuming an existing project:
     ```python
     from ojas_ops.pipelines.checkpoint import get_completed_stages, get_next_stage
     completed = get_completed_stages(tenant_id, project_id, pipeline_type)
     next_stage = get_next_stage(tenant_id, project_id, all_stages, pipeline_type)
     ```
   - Never re-execute completed stages unless a revision was explicitly requested by the user.
