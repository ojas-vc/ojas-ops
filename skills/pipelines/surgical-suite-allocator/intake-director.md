# Intake Director: Surgical Case Queue & Surgeon Block Entitlements

## Objective
Ingest elective surgical case requests, surgeon block time allocations, specialty equipment needs (da Vinci robotic system, fluoroscopy C-arm), and anesthesia team schedules.

## Invariant Rules
- Every surgical case must specify procedure code, expected duration, specialty requirements, and surgeon ID.
- Emergent and urgent add-on cases must have guaranteed dedicated buffer capacity.

## Output Artifact
`elective_case_queue`: Prioritized queue of surgical procedures ready for suite bin-packing.
