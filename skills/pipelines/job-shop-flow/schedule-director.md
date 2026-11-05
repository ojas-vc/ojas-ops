# Schedule Director: CP-SAT Combinatorial Job Shop Optimization

## Objective

Invoke Google OR-Tools CP-SAT discrete solver via `optimize_job_shop` to find optimal disjunctive machine intervals minimizing makespan and idle times.

## Invariant Rules

- No machine spindle may execute more than one operation simultaneously ($NoOverlap$).
- Precedence ordering $End(Op_A) \le Start(Op_B)$ must be strictly enforced.
- Setup transition times from `sdst_matrix` must separate consecutive operations on the same machine.
- Verify feasibility using `verify_schedule_feasibility`. 0 Hard Violations required.

## Output Artifact

`job_shop_schedule`: Scheduled operations with `machine_id`, `start_time`, `end_time`, and setup intervals.
