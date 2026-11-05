# Envelope Director: Sales Intake Capacity & Budget Envelopes

## Objective
Establish daily and weekly lead handling capacities across SDR teams, sales representatives, and onboarding queues to bound marketing spend.

## Invariant Rules
- Maximum daily inbound leads must not exceed CRM processing bandwidth by more than 15%.
- Budget envelopes must honor contractual monthly channel minimums and maximum spend ceilings.

## Output Artifact
`sales_intake_capacity`: Time-series bounds of daily lead acceptance thresholds and target cost-per-acquisition (CPA).
