# Optimization Objectives

Ojas Ops allows developers to configure single-goal or weighted multi-objective functions to direct solver search toward the most operationally desirable schedule.

Import root:

```python
from ojas_ops.objectives import (
    MinimizeMakespanObjective,
    MinimizeTardinessObjective,
    MinimizeIdleTimeObjective,
    MinimizeCostObjective,
    ScheduleStabilityObjective,
    WeightedCompositeObjective,
)
```

---

## 1. Single Optimization Objectives

### 1.1 `MinimizeMakespanObjective`

Minimizes the overall completion time of the entire project or shift:
$$\min \max_{i \in T} (e_i)$$

```python
scheduler.minimize("makespan")
# Or explicitly:
scheduler.minimize(MinimizeMakespanObjective(weight=1.0))
```

### 1.2 `MinimizeTardinessObjective`

Penalizes tasks that finish beyond their operational due dates or deadlines:
$$\min \sum_{i \in T} \max(0, e_i - \text{deadline}_i)$$

```python
scheduler.minimize(
    MinimizeTardinessObjective(
        deadlines={"job_1": 180, "job_2": 240},
        weight=2.0,
    )
)
```

### 1.3 `MinimizeIdleTimeObjective`

Minimizes dead gap-time between tasks on high-value resources (e.g., expensive actors, rented equipment, production lines):
$$\min \sum_{r} \left( \max_{i \in T_r}(e_i) - \min_{i \in T_r}(s_i) - \sum_{i \in T_r} d_i \right)$$

```python
scheduler.minimize(
    MinimizeIdleTimeObjective(
        resource_ids=["lead_actor", "soundstage_1"],
        weight=0.5,
    )
)
```

### 1.4 `MinimizeCostObjective`

Minimizes financial expenditure, aggregating task fixed costs, resource hourly rates, and overtime penalties:
$$\min \sum_{i \in T} \text{cost}_i + \sum_{r} (\text{rate}_r \cdot \text{duration}_r + \text{overtime\_rate}_r \cdot \text{overtime}_r)$$

```python
scheduler.minimize(MinimizeCostObjective(weight=1.0))
```

### 1.5 `ScheduleStabilityObjective`

Used during **rescheduling and disruption simulation**. Minimizes deviation from an approved baseline schedule, preventing unnecessary reorganization of unaffected tasks:
$$\min \sum_{i \in T} |s_i - s_i^{\text{baseline}}|$$

```python
scheduler.minimize(
    ScheduleStabilityObjective(
        baseline_starts={"scene_1": 0, "scene_2": 90, "scene_3": 210},
        weight=1.5,
    )
)
```

---

## 2. Multi-Objective Optimization: `WeightedCompositeObjective`

In real operations, objectives compete: for example, minimizing total duration vs. minimizing overtime costs vs. preserving baseline stability.

`WeightedCompositeObjective` scales floating-point weights into integer terms for CP-SAT and evaluates combined fitness:

$$\min \sum_{k} w_k \cdot f_k(s, e)$$

```python
from ojas_ops.objectives import (
    MinimizeMakespanObjective,
    MinimizeTardinessObjective,
    MinimizeIdleTimeObjective,
    WeightedCompositeObjective,
)

composite = WeightedCompositeObjective(
    [
        MinimizeMakespanObjective(weight=1.0),
        MinimizeTardinessObjective(weight=3.0),  # 3x priority on meeting deadlines
        MinimizeIdleTimeObjective(resource_ids=["actor_1"], weight=0.4),
    ]
)

scheduler.minimize(composite)
```
