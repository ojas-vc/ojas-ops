# Dispatch Director: Work Centre Queue & Shift Handover Gate

## Objective

Convert the mathematical schedule into actionable Work Centre Dispatch Queues for shop floor operators. Enforce Human-in-the-Loop review before releasing to production.

## Invariant Rules

- Align queue boundaries with 8-hour operator shifts.
- Include buffer inventory alerts between consecutive work centres.
- Require formal sign-off from the Plant Production Supervisor.

## Output Artifact

`work_centre_dispatch_queue`: Ordered execution list per machine station with operator sign-off blanks.
