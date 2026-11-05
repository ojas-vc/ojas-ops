# Routing Director: BOM Precedence & Machine Routing

## Objective

Ingest raw work orders, CAD/CAM bill of materials (BOM), and machine tool specifications into a canonical operations precedence DAG.

## Invariant Rules

- Every operation must specify: `id`, `part_id`, `machine_group`, `duration_minutes`, and `predecessors`.
- Machine groups must map to available CNC mills, lathes, EDM, or inspection stations.
- Precedence graph must be strictly acyclic (DAG).

## Output Artifact

`operations_bom`: Canonical list of operations with assigned compatible machines.
