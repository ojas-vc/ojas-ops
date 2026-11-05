# Roster Optimization Director: CP-SAT Nurse Scheduling

## Objective

Solve the integer programming nurse rostering formulation matching qualified nurses to required shifts while honoring contracts and blackout requests.

## Invariant Rules

- Hard Rest: Max 3 consecutive 12-hour shifts; min 48h rest post-night blocks.
- Minimum 12 hours rest turnaround between consecutive calls.
- Skill Match: Ensure advanced life support (ACLS) and ECMO certified nurses on every ICU shift.
- Zero overlapping shifts for the same nurse.

## Output Artifact

`clinical_shift_roster`: Master 28-day shift assignments for all nursing personnel.
