# Line Balancing Director: Takt Time & Workstation Balancing

## Objective
Distribute discrete assembly tasks across sequential assembly line workstations to match customer demand takt time while eliminating line starvation and bottleneck pileups.

## Invariant Rules
- Total workstation task duration must strictly remain below line takt time.
- Assembly precedence dependencies must be preserved across stations.

## Output Artifact
`takt_time_assignments`: Station-by-station task distribution with line efficiency metrics.
