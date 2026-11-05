# QA Director: Quality Inspection & Release Docket

## Objective

Schedule mandatory inline CMM (Coordinate Measuring Machine) inspections and calibrate preventive maintenance windows.

## Invariant Rules

- Every first piece of a new setup batch must include a 20-minute inspection hold.
- Verify tool cycle counter does not exceed manufacturer threshold before next cycle.
- Produce verified production dispatch docket.

## Output Artifact

`quality_inspection_docket`: Audit report certifying tolerances, tool wear, and release authorization.
