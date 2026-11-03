"""Scenario execution engine, validation harness, and summary reporter."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from pathlib import Path

from ojas_ops.scenarios.loader import build_scheduler, load_scenario, verify_expected
from ojas_ops.scenarios.models import ScenarioDefinition, ScenarioRunResult
from ojas_ops.solvers.config import SolverConfig


def run_scenario(
    scenario: str | Path | ScenarioDefinition,
    config: SolverConfig | None = None,
    *,
    print_summary: bool = True,
) -> ScenarioRunResult:
    """Execute an end-to-end scenario run: load, solve, validate, and verify golden assertions."""
    if isinstance(scenario, (str, Path)):
        scenario_def = load_scenario(scenario)
    else:
        scenario_def = scenario

    scheduler = build_scheduler(scenario_def)
    result = scheduler.solve(config=config)
    report = scheduler.validate(result)
    verification_failures = verify_expected(scenario_def, result, report)

    run_result = ScenarioRunResult(
        scenario=scenario_def,
        result=result,
        report=report,
        verification_failures=verification_failures,
    )

    if print_summary:
        print_scenario_summary(run_result)

    return run_result


def print_scenario_summary(run_result: ScenarioRunResult) -> None:
    """Display a formatted operational summary of a scenario run."""
    sc = run_result.scenario
    res = run_result.result
    val = run_result.report
    failures = run_result.verification_failures

    print("=" * 68)
    print(f" SCENARIO: {sc.metadata.name}")
    if sc.metadata.description:
        print(f" Description: {sc.metadata.description}")
    print(
        f" Domain: {sc.metadata.domain} | Scale: {sc.metadata.scale.upper()} | Version: {sc.metadata.version}"
    )
    print(f" Resources: {len(sc.resources)} | Tasks: {len(sc.tasks)}")
    print("-" * 68)
    print(f" Solver Status:     {res.status.value.upper()}")
    print(f" Total Makespan:    {res.makespan} time units")
    print(f" Objective Value:   {res.objective_value}")
    print(f" Solve Time:        {res.solve_time_seconds:.4f}s (wall: {res.wall_time:.4f}s)")
    if res.metadata:
        print(f" Metadata:          {res.metadata}")
    print("-" * 68)
    val_status = (
        "VALID (Passed all constraints)"
        if val.is_valid
        else f"INVALID ({val.error_count} error(s))"
    )
    print(f" Validation:        {val_status}")
    if not val.is_valid:
        for violation in val.violations:
            print(f"   [!] {violation.constraint_name}: {violation.message}")

    print("-" * 68)
    if sc.expected:
        if not failures:
            print(" Golden Assertions: PASSED (All expected bounds and conditions met)")
        else:
            print(f" Golden Assertions: FAILED ({len(failures)} mismatch(es))")
            for failure in failures:
                print(f"   [FAIL] {failure}")
    else:
        print(" Golden Assertions: None defined")

    print("-" * 68)
    print(" Scheduled Tasks Breakdown:")
    task_items = list(res.tasks.items())
    task_items.sort(key=lambda item: (item[1].start, item[0]))

    show_limit = 24
    if len(task_items) <= show_limit:
        for tid, st in task_items:
            res_str = ", ".join(st.assigned_resources) if st.assigned_resources else "none"
            print(f"   - [{st.start:04d} -> {st.end:04d}] {tid} ({st.duration}u) on [{res_str}]")
    else:
        for tid, st in task_items[:12]:
            res_str = ", ".join(st.assigned_resources) if st.assigned_resources else "none"
            print(f"   - [{st.start:04d} -> {st.end:04d}] {tid} ({st.duration}u) on [{res_str}]")
        print(f"   ... ({len(task_items) - 20} tasks omitted for brevity) ...")
        for tid, st in task_items[-8:]:
            res_str = ", ".join(st.assigned_resources) if st.assigned_resources else "none"
            print(f"   - [{st.start:04d} -> {st.end:04d}] {tid} ({st.duration}u) on [{res_str}]")
    print("=" * 68)
