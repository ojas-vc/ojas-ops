# System Architecture & Design

Ojas Ops is engineered around the principle that **combinatorial scheduling requires deterministic mathematical optimization rather than probabilistic AI generation**.

While Large Language Models (LLMs) and agentic workflows are powerful for natural-language ingestion and human coordination, core scheduling decisions (task start times, resource allocations, precedence adherence, capacity bounds) must be guaranteed by constraint programming.

---

## 1. Architectural Topology

```text
                        Client Applications & Agentic AI
                                       │
                                       ▼
                         Scheduler (Fluent Orchestrator)
                                       │
          ┌────────────────────────────┴────────────────────────────┐
          ▼                                                         ▼
Domain Adapters (Use Cases)                               Scenario Simulator
- Film Shooting Schedules                                 - Disruption Modeling
- Manufacturing Job Shop                                  - Impact Analysis
- Healthcare Rostering                                    - Schedule Stability Metrics
- Academic Timetables                                     - Dual-Objective Rescheduling
- Conference Run-Sheets                                                 │
- Marketing Campaign Cadence                                            │
          │                                                             │
          └────────────────────────────┬────────────────────────────────┘
                                       ▼
                       Typed Domain Models (msgspec.Struct)
               (Task, Resource, IntervalWindow, TimeWindow, Horizon)
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          ▼                            ▼                            ▼
Constraint Formulations       Calendar Providers           Optimization Goals
- Precedence (FS, SS, FF, SF) - Standard Working Hours     - Makespan
- No-Overlap (Disjunctive)    - Shift Rotations            - Lateness / Tardiness
- Cumulative Capacities       - Panchang / Muhurats        - Idle Time & Cost
- Blackout / Target Windows   - Rahu Kalam Inauspicious    - Baseline Stability
- Setup Transition Matrices   - Lunar / Tithi Offsets      - Weighted Composite
          │                            │                            │
          └────────────────────────────┼────────────────────────────┘
                                       ▼
                             Solver Bridge Interface
                                       │
                                       ▼
                       Google OR-Tools CP-SAT Backend
                                       │
                                       ▼
                          ScheduleResult & Metrics
                     (Optimal / Feasible Assignment Map)
                                       │
                                       ▼
                   Independent Deterministic Validator
                  (Verifies all constraints without solver)
```

---

## 2. Core Architectural Principles

### 2.1 Domain Independence & Extensibility

The optimization engine, constraint formulations, calendar handlers, and validation engine are completely agnostic of any particular industry. All domain-specific concepts (e.g. film scenes, machine changeovers, nurse rest hours) translate into standard mathematical primitives:

- **Tasks** with integer duration and optional time windows.
- **Resources** with unitary or cumulative capacity.
- **Intervals** defining temporal domains.
- **Constraints** expressing linear equalities or disjunctions.

### 2.2 Microsecond Data Modeling via `msgspec`

Every domain model (`Task`, `Resource`, `ScheduledTask`, `ValidationReport`, etc.) is implemented using `msgspec.Struct`. This delivers:

- Microsecond JSON and messagepack encoding/decoding.
- Minimal heap memory footprint for thousands of task variables.
- Strict typing and validation at boundary interfaces.

### 2.3 Independent Deterministic Validation Seam

A solver can find a solution, but how do we prove it satisfies real-world rules without trusting the solver's internal state?
Ojas Ops enforces an **independent validation engine** (`ScheduleValidator`). The validator parses the raw `ScheduleResult` using pure Python logic, checks every precedence arc, resource overlap, capacity ceiling, blackout window, and setup buffer, and generates a structured `ValidationReport`.
This enables:

- Golden-dataset regression testing.
- Independent auditing for regulated industries (healthcare, aviation, logistics).
- Failure diagnosis when manual overrides are attempted.

### 2.4 Data-Driven Scenarios & Golden Assertions

Complex operational systems require reproducible regression datasets. Ojas Ops provides a dedicated `scenarios` infrastructure (`ScenarioDefinition` with embedded `ExpectedResult` assertions):

- **Declarative Formats:** High-speed JSON schemas decoded via `msgspec`, alongside flat CSV tabular loaders.
- **Embedded Golden Assertions:** Datasets contain their own acceptance criteria (expected status, makespan bounds, objective ceilings, task timing windows).
- **Automated Verification:** Verified deterministically via `verify_expected()` and executed via `run_scenario()`.
- **Synthetic Generators:** Algorithmic generators create multi-scale benchmarks (small, medium, large, stress) for performance evaluation.

---

## 3. Mathematical CP-SAT Formulation

### 3.1 Interval Variables and Precedence

For each task $i \in T$ with duration $d_i$, we define:

- Start variable: $s_i \in [0, H]$
- End variable: $e_i \in [d_i, H]$
- Interval variable: $I_i = \text{IntervalVar}(s_i, d_i, e_i)$
- Equality relation: $s_i + d_i = e_i$

For a precedence dependency where task $i$ precedes task $j$ with minimum lag $L_{min}$ and maximum lag $L_{max}$:
$$s_j \ge e_i + L_{min}$$
$$s_j \le e_i + L_{max} \quad (\text{if } L_{max} \text{ specified})$$

### 3.2 Resource Disjunction (No-Overlap)

For a unitary resource $r$ with capacity $C_r = 1$ and assigned tasks $T_r \subseteq T$:
$$\text{NoOverlap}(\{I_i \mid i \in T_r\})$$
This ensures that for any two distinct tasks $i, j \in T_r$:
$$e_i \le s_j \quad \lor \quad e_j \le s_i$$

### 3.3 Cumulative Resource Capacity

For a resource $r$ with capacity $C_r > 1$, where each task $i$ requires integer demand $c_{i, r}$:
$$\text{Cumulative}(\{I_i\}_{i \in T_r}, \{c_{i, r}\}_{i \in T_r}, C_r)$$
Guaranteeing that at any time instant $t$:
$$\sum_{i \in T_r \mid s_i \le t < e_i} c_{i, r} \le C_r$$

### 3.4 Sequence-Dependent Setup and Transition Matrices

When switching from task $i$ to task $j$ on resource $r$ requires setup time $\Delta_{i, j}$:
Ojas Ops uses Google OR-Tools CP-SAT's specialized Hamiltonian path / circuit constraint (`model.add_circuit(arcs)`) augmented with a dummy root node:

- For each ordered pair $(i, j)$, an arc literal $l_{i, j}$ is instantiated.
- If $l_{i, j} = 1$, the linear transition timing relation is enforced:
  $$s_j \ge e_i + \Delta_{i, j}$$
- `model.add_circuit` strictly prevents sub-tours and enforces a single valid chronological sequence across tasks sharing the resource.

### 3.5 Blackout Windows and Target Windows

For an unavailable blackout window $[W_{start}, W_{end}]$:

- When assigned to a **resource**, Ojas Ops compiles the blackout as a native fixed interval variable $I_{\text{blackout}} = \text{IntervalVar}(W_{start}, W_{end} - W_{start}, W_{end})$. This fixed interval is injected directly into `model.add_no_overlap()` (or `model.add_cumulative()`), leveraging CP-SAT's highly optimized interval propagation engine.
- When bound to a specific **task**, the solver enforces non-overlap between the task interval and the blackout interval:
  $$e_i \le W_{start} \quad \lor \quad s_i \ge W_{end}$$

For an auspicious target window $[T_{start}, T_{end}]$ (e.g. Shubh Muhurat):
$$s_i \ge T_{start} \quad \land \quad e_i \le T_{end}$$

---

## 4. Rescheduling and Simulation Mechanics

When operational reality diverges from a planned schedule (e.g., equipment breaks down, flight delayed, actor absent):

```text
Original Schedule ──► Operational Disruption ──► Freeze Elapsed Tasks (t < t_now)
                             │
                             ▼
               Identify Impacted Subtree
                             │
                             ▼
         Dual-Objective Mathematical Optimization:
         Minimize: α · Makespan + β · Total_Displacement
                             │
                             ▼
              Minimally-Disruptive Revised Plan
```

### 4.1 Dual-Objective Stability Formulation

Rather than regenerating a completely new schedule that reorganizes all unrelated tasks, the `ScenarioSimulator` optimizes for **stability**:
$$\min \sum_{i \in T} \beta_i \cdot |s_i - s_i^{\text{baseline}}| + \alpha \cdot \text{Makespan}$$
In CP-SAT, absolute deviations $|s_i - s_i^{\text{baseline}}|$ are linearized using `model.add_abs_equality(abs_diff, s_i - s_i^{\text{baseline}})`.
Tasks completed before the current time $t_{current}$ are automatically pinned with $s_i = s_i^{\text{baseline}}$.
