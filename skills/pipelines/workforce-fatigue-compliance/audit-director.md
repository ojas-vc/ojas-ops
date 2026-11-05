# Audit Director: Labor Fatigue & Statutory Violation Detection

## Objective
Audit existing workforce schedules against union agreements, labor standards, and fatigue models to detect rest breaches, illegal consecutive shifts, and forced turnaround calls.

## Invariant Rules
- Flag any shift assignment where turnaround rest is under contractual minimum (12 hours daily, 54 hours weekly).
- Highlight nurses, pilots, or technicians assigned beyond maximum continuous duty ceilings.

## Output Artifact
`violation_register`: Comprehensive ledger of identified compliance violations with severity classifications and penalty cost estimates.
