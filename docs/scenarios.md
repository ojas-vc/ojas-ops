# Scenarios, Golden Datasets & Benchmarks

Ojas Ops provides a high-performance, data-driven scenario modeling framework under `ojas_ops.scenarios`.

Instead of hardcoding scheduling entities inside Python scripts, real-world operational problems can be defined in structured, portable **JSON** (and **CSV**) files that encode both the **problem configuration** and the **golden expected results / benchmark assertions** in the dataset itself.

```python
from ojas_ops.scenarios import (
    load_scenario,
    save_scenario,
    build_scheduler,
    verify_expected,
    run_scenario,
    generate_benchmark_suite,
)
```

---

## 1. Core Architecture & Data Models

All scenario models are defined as typed `msgspec.Struct` records in `ojas_ops.scenarios.models`, enabling microsecond serialization and C-level decoding speed.

```text
                            ScenarioDefinition (JSON / CSV)
                                          │
       ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
       ▼                  ▼               ▼               ▼                  ▼
 ScenarioMetadata     Resources         Tasks        Transitions        Workloads / Calendar
 (Domain, Scale)  (Capacities, Costs) (Durations) (Setup Matrices)  (Panchang / Shifts)
                                          │
                                          ▼
                                     Objective
                                (Makespan / Cost)
                                          │
                                          ▼
                               ExpectedResult (Golden Assertions)
                       (Status, Bounds, Task Timing & Assignments)
```

### 1.1 Model Reference

| Model                | Description                                                    | Key Fields                                                                                                            |
| :------------------- | :------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| `ScenarioDefinition` | Root specification of a complete operational problem instance. | `metadata`, `resources`, `tasks`, `transitions`, `workloads`, `calendar`, `objective`, `expected`                     |
| `ScenarioMetadata`   | Problem categorization, domain, and scale tagging.             | `name`, `description`, `domain`, `scale` (`small`/`medium`/`large`/`benchmark`), `version`, `tags`                    |
| `ResourceSpec`       | Operational resource declaration.                              | `id`, `name`, `capacity`, `resource_type`, `cost_per_time_unit`, `skills`, `blackout_windows`                         |
| `TaskSpec`           | Activity to be scheduled.                                      | `id`, `duration`, `required_resources`, `candidate_pools`, `dependencies`, `time_window`, `fixed_start`               |
| `TransitionSpec`     | Sequence-dependent changeover / turnaround buffer matrix.      | `resource_id`, `default_buffer`, `matrix` (keyed by `"task_a,task_b"`)                                                |
| `WorkloadSpec`       | Maximum active workload duration and minimum rest recovery.    | `resource_id`, `max_duration`, `min_rest`                                                                             |
| `CalendarSpec`       | Operational or cultural non-Gregorian calendar rules.          | `type` (`cultural`/`standard`), `enable_rahu_kalam`, `enable_yamagandam`, `muhurats`                                  |
| `MuhuratSpec`        | Auspicious target window with optional task attachment.        | `start`, `end`, `task_id`, `label`, `hard`                                                                            |
| `ObjectiveSpec`      | Solver optimization goal.                                      | `type` (`makespan`/`cost`/`idle_time`/`tardiness`/`composite`), `is_maximize`, `weight`, `sub_objectives`             |
| `ExpectedResult`     | Golden benchmark assertions defined directly in the dataset.   | `status`, `is_valid`, `min_makespan`, `max_makespan`, `max_objective_value`, `expected_task_count`, `task_assertions` |
| `ScenarioRunResult`  | Unified outcome of a scenario execution.                       | `scenario`, `result`, `report`, `verification_failures`, `is_success`                                                 |

---

## 2. Complete JSON Dataset Specification

Here is an annotated scenario JSON dataset illustrating all core primitives:

```json
{
  "metadata": {
    "name": "Industrial Manufacturing Job Shop (12 Operations)",
    "description": "Multi-job sequence-dependent changeover problem across CNC, lathe, and laser cutter.",
    "domain": "manufacturing",
    "scale": "medium",
    "version": "1.0",
    "tags": ["manufacturing", "jobshop", "transitions"]
  },
  "resources": [
    {
      "id": "cutting_station",
      "name": "Laser Cutting Station",
      "capacity": 1,
      "resource_type": "machine",
      "cost_per_time_unit": 45.0
    },
    {
      "id": "cnc_mill",
      "name": "5-Axis CNC Mill",
      "capacity": 1,
      "resource_type": "machine",
      "cost_per_time_unit": 70.0
    }
  ],
  "tasks": [
    {
      "id": "gears_cut",
      "name": "Gears - Laser Profiling",
      "duration": 40,
      "required_resources": ["cutting_station"]
    },
    {
      "id": "gears_mill",
      "name": "Gears - 5-Axis Milling (Steel)",
      "duration": 60,
      "required_resources": ["cnc_mill"],
      "dependencies": ["gears_cut"]
    }
  ],
  "transitions": [
    {
      "resource_id": "cnc_mill",
      "default_buffer": 10,
      "matrix": {
        "gears_mill,brackets_mill": 25,
        "brackets_mill,gears_mill": 30
      }
    }
  ],
  "objective": {
    "type": "makespan",
    "is_maximize": false,
    "weight": 1.0
  },
  "expected": {
    "status": "optimal",
    "is_valid": true,
    "min_makespan": 100,
    "max_makespan": 450,
    "expected_task_count": 2,
    "task_assertions": {
      "gears_mill": {
        "min_start": 40
      }
    }
  }
}
```

---

## 3. Golden Assertions & Independent Verification

The `expected` block allows test suites and CI pipelines to perform automatic regression testing against known good optimization outcomes:

```python
from ojas_ops.scenarios import load_scenario, build_scheduler, verify_expected

scenario = load_scenario("examples/film_production/data/feature_film_production.json")
scheduler = build_scheduler(scenario)

# 1. Solve
result = scheduler.solve()

# 2. Independently validate constraints without solver
report = scheduler.validate(result)

# 3. Verify against golden benchmark assertions
failures = verify_expected(scenario, result, report)
if failures:
    for fail in failures:
        print(f"[FAIL] {fail}")
else:
    print("All golden assertions passed!")
```

### Verification Checks Performed:

1. **Status Verification**: Confirms solver achieved `optimal` (or `feasible` if requested).
2. **Feasibility / Constraint Compliance**: Confirms `report.is_valid == expected.is_valid` with 0 constraint violations.
3. **Makespan Bounds**: Confirms `result.makespan <= expected.max_makespan` and `result.makespan >= expected.min_makespan`.
4. **Objective Value Bounds**: Confirms `result.objective_value <= expected.max_objective_value`.
5. **Task Count**: Confirms all tasks were scheduled.
6. **Task-Level Timing & Resource Assertions**: Checks per-task conditions like `min_start`, `max_end`, and `assigned_resource`.

---

## 4. Running Scenarios via API and CLI

### 4.1 Python API (`run_scenario`)

```python
from ojas_ops.scenarios import run_scenario

run_res = run_scenario("examples/manufacturing/data/industrial_jobshop.json")

print("Valid:", run_res.report.is_valid)
print("Success:", run_res.is_success)
print("Makespan:", run_res.result.makespan)
```

The runner displays a formatted operational report:

```text
====================================================================
 SCENARIO: Industrial Job Shop (4 Jobs, 12 Operations, 3 Work Centers)
 Description: Job shop scheduling with sequence-dependent setup times.
 Domain: manufacturing | Scale: MEDIUM | Version: 1.0
 Resources: 3 | Tasks: 12
--------------------------------------------------------------------
 Solver Status:     OPTIMAL
 Total Makespan:    330 time units
 Objective Value:   330.0
 Solve Time:        0.0193s (wall: 0.0233s)
 Metadata:          {'num_branches': '66', 'best_objective_bound': '330.0000'}
--------------------------------------------------------------------
 Validation:        VALID (Passed all constraints)
--------------------------------------------------------------------
 Golden Assertions: PASSED (All expected bounds and conditions met)
--------------------------------------------------------------------
 Scheduled Tasks Breakdown:
   - [0000 -> 0025] housings_cut (25u) on [cutting_station]
   - [0025 -> 0065] gears_cut (40u) on [cutting_station]
   - [0025 -> 0095] housings_mill (70u) on [cnc_mill]
   - [0065 -> 0095] brackets_cut (30u) on [cutting_station]
   ...
====================================================================
```

### 4.2 CLI Execution

All example directories support passing custom scenario files directly from the command line:

```bash
# Run default dataset
uv run python examples/film_production/main.py

# Run custom or large dataset
uv run python examples/film_production/main.py examples/film_production/data/small_shoot.json
uv run python examples/manufacturing/main.py examples/manufacturing/data/large_aerospace_jobshop.json
```

---

## 5. CSV Tabular Ingestion

For organizations maintaining production workflows in Excel or tabular databases, Ojas Ops provides flat CSV ingestion:

```python
from ojas_ops.scenarios import (
    load_tasks_from_csv,
    load_resources_from_csv,
    ScenarioDefinition,
    ScenarioMetadata,
    ObjectiveSpec,
    run_scenario,
)

tasks = load_tasks_from_csv("examples/basic_scheduling/data/tasks.csv")
resources = load_resources_from_csv("examples/basic_scheduling/data/resources.csv")

scenario = ScenarioDefinition(
    metadata=ScenarioMetadata(name="Factory Flow (CSV)", domain="manufacturing"),
    resources=resources,
    tasks=tasks,
    objective=ObjectiveSpec(type="makespan"),
)

run_result = run_scenario(scenario)
```

Run directly via the example CLI flag:

```bash
uv run python examples/basic_scheduling/main.py --csv
```

---

## 6. Synthetic Benchmark Suite Generators

Ojas Ops includes algorithmic generators in `ojas_ops.scenarios.generator` to synthesize large-scale stress tests and benchmark suites:

```python
from ojas_ops.scenarios import (
    generate_jobshop_scenario,
    generate_workforce_scenario,
    generate_film_scenario,
    generate_benchmark_suite,
)

# 1. Generate a 10-job, 40-operation Job Shop benchmark with sequence-dependent changeovers
js_scenario = generate_jobshop_scenario(
    num_jobs=10,
    num_machines=5,
    operations_per_job=4,
    seed=42,
)

# 2. Generate a 20-nurse, 45-shift hospital rostering problem with qualification pools
wf_scenario = generate_workforce_scenario(
    num_staff=20,
    num_shifts=45,
    horizon_hours=120,
    seed=42,
)

# 3. Generate a complete benchmark suite (small, medium, large) saved directly to disk
paths = generate_benchmark_suite("benchmarks/generated", scales=["small", "medium", "large"])
```

---

## 7. Catalog of Example Scenario Datasets

The repository ships with ready-to-solve datasets in `examples/**/data/`:

| Dataset Path                                                     | Domain        | Tasks | Resources | Special Characteristics                                                   |
| :--------------------------------------------------------------- | :------------ | :---- | :-------- | :------------------------------------------------------------------------ |
| `examples/film_production/data/feature_film_production.json`     | Film          | 15    | 7         | Actor blackout windows, location turnarounds, precedence chains           |
| `examples/film_production/data/small_shoot.json`                 | Film          | 5     | 4         | Compact commercial shoot                                                  |
| `examples/manufacturing/data/industrial_jobshop.json`            | Manufacturing | 12    | 3         | CNC/Laser/Lathe sequence-dependent family setup matrices                  |
| `examples/manufacturing/data/large_aerospace_jobshop.json`       | Manufacturing | 40    | 5         | Multi-machine Job Shop benchmark solved to optimality in <2s              |
| `examples/nurse_rostering/data/hospital_shifts.json`             | Healthcare    | 14    | 8         | ICU/triage qualification pools, max workload, min 8h rest                 |
| `examples/nurse_rostering/data/monthly_ward_roster.json`         | Healthcare    | 45    | 20        | 5-day round-the-clock ward coverage                                       |
| `examples/basic_scheduling/data/basic_factory.json`              | General       | 3     | 2         | Cleaning blackout windows, auspicious launch window                       |
| `examples/basic_scheduling/data/tasks.csv` & `resources.csv`     | General       | 5     | 5         | Flat CSV tabular benchmark                                                |
| `examples/academic_timetabling/data/university_timetable.json`   | Academic      | 10    | 9         | Room collision avoidance, computer lab restrictions, faculty meetings     |
| `examples/event_run_sheets/data/tech_conference.json`            | Events        | 9     | 6         | Multi-track conference sessions, fixed plenary keynotes, hall turnarounds |
| `examples/festival_calendar/data/temple_festival.json`           | Cultural      | 5     | 4         | Rahu Kalam & Yamagandam blackouts, Vedic Shubh Muhurat window             |
| `examples/marketing_flighting/data/q4_omnichannel_campaign.json` | Marketing     | 8     | 4         | Multi-channel advertising cadence, budget flighting                       |
