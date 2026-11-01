# Independent Validation Engine

A key architectural principle of Ojas Ops is **decoupling solution generation from solution verification**.

While Google OR-Tools CP-SAT generates schedules, the **Validation Engine** (`ScheduleValidator`) independently and deterministically verifies that the resulting schedule satisfies all operational rules without invoking the solver.

```python
from ojas_ops.validation import ScheduleValidator, ValidationReport, ConstraintViolation, Severity
```

---

## 1. Why Independent Validation Matters

1. **Auditability & Compliance:** Regulated operational environments (aviation, clinical healthcare, industrial manufacturing) require provable constraint checks that do not depend on proprietary solver state.
2. **Defensive Programming:** Protects against bugs or unexpected interactions in model compilation, custom user constraints, or manual schedule edits.
3. **Diagnostic Clarity:** When a schedule is modified by a human operator, the validatorPinpoints the exact task, resource, and time of any resulting violation.

---

## 2. Validation Checklist

The `ScheduleValidator` evaluates 10 independent verification gates:

```text
                           ScheduleResult
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
1. Status Feasibility       2. Task Integrity          3. Precedence Check
   (OPTIMAL or FEASIBLE)       (duration, time window,    (FS, SS, FF, SF lags)
                                fixed start)
     │                           │                           │
     ├───────────────────────────┼───────────────────────────┤
     ▼                           ▼                           ▼
4. Resource Collisions      5. Cumulative Demand       6. Blackout Windows
   (No two tasks overlap       (Active load never         (Tasks strictly outside
    on capacity=1 resources)    exceeds capacity)          unavailable intervals)
     │                           │                           │
     ├───────────────────────────┼───────────────────────────┤
     ▼                           ▼                           ▼
7. Target Windows           8. Setup Transitions       9. Rest & Duty Limits
   (Tasks fall completely      (Buffer gaps between       (Min rest intervals
    inside allowed windows)     adjacent tasks)            & max hours respected)
                                 │
                                 ▼
                     10. Custom Constraints
```

---

## 3. Usage Example

```python
validator = scheduler.validate(result)

if not validator.is_valid:
    print(f"Validation FAILED: {validator.error_count} errors discovered.")
    for violation in validator.violations:
        print(
            f"[{violation.severity.value.upper()}] {violation.constraint_name}: {violation.message}"
        )
        if violation.task_id:
            print(f"  Affected Task: {violation.task_id}")
        if violation.resource_id:
            print(f"  Affected Resource: {violation.resource_id}")
else:
    print("Schedule passed all independent verification gates.")
```

---

## 4. Reporting Models

### `ValidationReport`
```python
class ValidationReport(msgspec.Struct, kw_only=True):
    is_valid: bool
    violations: list[ConstraintViolation] = []
    summary: str = ""

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)
```

### `ConstraintViolation`
```python
class ConstraintViolation(msgspec.Struct, kw_only=True):
    constraint_name: str
    task_id: str | None = None
    resource_id: str | None = None
    message: str = ""
    severity: Severity = Severity.ERROR
    details: dict[str, str] = {}
```

