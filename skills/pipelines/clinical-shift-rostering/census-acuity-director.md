# Census Acuity Director: Patient Load & Acuity Classification

## Objective

Ingest clinical census projections, emergency admissions forecasts, and surgery schedule intakes to generate hourly patient acuity tiers across hospital units.

## Invariant Rules

- Every bed must have an assigned acuity tier (ICU Level 1/2, Step-Down, Telemetry, Med-Surg).
- High-acuity ventilator patients require 1:1 or 1:2 dedicated RN coverage.

## Output Artifact

`patient_acuity_census`: Bed-by-bed acuity time series across the 28-day scheduling horizon.
