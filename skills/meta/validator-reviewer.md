# Deterministic Validator Reviewer

## Purpose

Independent, solver-agnostic quality control. Proves that any generated schedule satisfies all physical, temporal, labor, and contractual constraints before human sign-off.

## Review Protocol

1. **Invoke Deterministic Feasibility Engine**:
   - Run `verify_schedule_feasibility` tool.
   - The validator parses the raw assignments without trusting the solver's internal state.

2. **Hard Violations vs Soft Penalties**:
   - **Hard Violations** (Fatal):
     - Overlapping tasks on disjunctive resources.
     - Encroachment on daily turnaround minimums (e.g., < 12h rest).
     - Encroachment on weekly rest (e.g., < 54h continuous).
     - Missing or overdue meal breaks (> 6 hours).
     - Broken precedence relationships (Task B starting before Task A completes).
     - High-hazard stunt scheduled before the 70% production progress milestone.
     - Interleaved soundstage drop/re-lease.
   - **Soft Penalties** (Tradeoffs):
     - Cast idle hold days.
     - Camera setup rotations ($\Delta \theta > 45^\circ$).
     - Minor deviations from optimal temperature/color changeover sequences.

3. **Gating Rule**:
   - If `hard_violations > 0`:
     - Stage FAILS review.
     - The agent MUST NOT proceed to human approval.
     - Identify the conflicting equations or resources and adjust solver constraints.
   - If `hard_violations == 0`:
     - Stage PASSES review.
     - Compile the Tradeoff Report and present to user.
