# Recovery Director: Reactive Rescheduling & Schedule Stability

## Objective
When an incident occurs (talent illness, weather shutdown, camera breakdown), formulate the stability-constrained rescheduling optimization:
$\min \alpha \cdot \text{Makespan} + \beta \cdot \text{Cost} + \gamma \cdot \sum |t_i^{new} - t_i^{orig}|$

## Invariant Rules
- Minimize displacement of already confirmed location permits and talent flights.
- Require Line Producer sign-off on cost variance.
