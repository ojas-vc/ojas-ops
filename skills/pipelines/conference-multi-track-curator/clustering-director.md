# Clustering Director: Topic Clustering & Room Capacity Allocation

## Objective
Analyze submitted talks, keynote abstracts, and panel descriptions to form topical affinity clusters and map expected audience volume to hall capacities.

## Invariant Rules
- High-affinity sessions within the same track must be scheduled sequentially or in non-conflicting parallel slots.
- Room seating capacity must exceed historical registration interest with a 20% safety margin.

## Output Artifact
`topical_clusters`: Categorized track groupings with speaker lists and room allocations.
