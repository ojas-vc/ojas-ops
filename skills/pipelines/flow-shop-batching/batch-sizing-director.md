# Batch Sizing Director: Campaign Sizing & Cleanroom Batching

## Objective
Group customer formulation orders into optimal campaign batch sizes honoring Clean-in-Place (CIP) limits and minimum economic batch quantities.

## Invariant Rules
- Campaign batches must not exceed cleanroom tank volumetric capacity.
- Minimize cross-contamination risks by sequencing from light colors/neutral formulas to dark/active formulations.

## Output Artifact
`production_batch_manifest`: Ordered batch sizes with formulation codes and cleaning requirements.
