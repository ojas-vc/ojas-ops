# Setup Matrix Director: SDST Formulation

## Objective

Construct the Sequence-Dependent Setup Time (SDST) matrix across parts, tooling fixtures, and materials.

## Invariant Rules

- Setup time $S(i, j)$ represents duration to switch from part family $i$ to part family $j$.
- Tool cleanout or material alloy changes require strict minimum changeover windows.
- Symmetrical or asymmetrical transition times must satisfy triangle inequality wherever physical tooling permits.

## Output Artifact

`sdst_matrix`: Dense matrix of changeover delays in minutes.
