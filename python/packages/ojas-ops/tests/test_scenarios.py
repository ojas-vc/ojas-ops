"""Unit and regression tests for scenario loading, execution, golden assertions, and generators."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from pathlib import Path

from ojas_ops.scenarios import (
    ExpectedResult,
    ObjectiveSpec,
    ScenarioDefinition,
    ScenarioMetadata,
    generate_benchmark_suite,
    generate_film_scenario,
    generate_jobshop_scenario,
    generate_workforce_scenario,
    load_resources_from_csv,
    load_scenario,
    load_tasks_from_csv,
    run_scenario,
    save_scenario,
    verify_expected,
)


def test_all_example_json_scenarios() -> None:
    """Every scenario JSON in examples/**/data/*.json must solve, validate, and pass golden assertions."""
    repo_root = Path(__file__).resolve().parents[3]
    json_files = list(repo_root.glob("examples/**/data/*.json"))
    assert len(json_files) >= 8, f"Expected at least 8 scenario JSONs, found {len(json_files)}"

    for json_file in json_files:
        run_res = run_scenario(json_file, print_summary=False)
        assert run_res.report.is_valid, (
            f"Scenario {json_file.name} failed independent validation: {run_res.report.summary}"
        )
        assert len(run_res.verification_failures) == 0, (
            f"Scenario {json_file.name} failed golden assertions: {run_res.verification_failures}"
        )
        assert run_res.is_success, f"Scenario {json_file.name} was not marked as successful"


def test_csv_scenario_loading_and_solving() -> None:
    """Flat CSV task and resource loading must correctly construct a valid solvable scenario."""
    repo_root = Path(__file__).resolve().parents[3]
    tasks_csv = repo_root / "examples" / "basic_scheduling" / "data" / "tasks.csv"
    resources_csv = repo_root / "examples" / "basic_scheduling" / "data" / "resources.csv"

    assert tasks_csv.exists()
    assert resources_csv.exists()

    tasks = load_tasks_from_csv(tasks_csv)
    resources = load_resources_from_csv(resources_csv)

    assert len(tasks) == 5
    assert len(resources) == 5

    scenario = ScenarioDefinition(
        metadata=ScenarioMetadata(name="CSV Factory Test", domain="manufacturing", scale="small"),
        resources=resources,
        tasks=tasks,
        objective=ObjectiveSpec(type="makespan"),
        expected=ExpectedResult(
            status="optimal", is_valid=True, max_makespan=250, min_makespan=100
        ),
    )

    run_res = run_scenario(scenario, print_summary=False)
    assert run_res.is_success
    assert run_res.result.makespan == 170


def test_scenario_serialization_roundtrip(tmp_path: Path) -> None:
    """Saving and loading a ScenarioDefinition must produce an identical model."""
    sc = generate_jobshop_scenario(num_jobs=3, num_machines=2, operations_per_job=2, seed=7)
    target_file = tmp_path / "test_jobshop.json"

    save_scenario(sc, target_file)
    assert target_file.exists()

    loaded = load_scenario(target_file)
    assert loaded.metadata.name == sc.metadata.name
    assert len(loaded.tasks) == len(sc.tasks)
    assert len(loaded.resources) == len(sc.resources)
    assert len(loaded.transitions) == len(sc.transitions)


def test_golden_assertion_failures() -> None:
    """verify_expected must accurately detect when solver output violates golden bounds."""
    sc = generate_jobshop_scenario(num_jobs=2, num_machines=2, operations_per_job=2, seed=1)
    run_res = run_scenario(sc, print_summary=False)
    actual_makespan = run_res.result.makespan

    # Artificially set impossible expected bounds
    sc.expected = ExpectedResult(
        status="optimal",
        is_valid=True,
        max_makespan=actual_makespan - 10,  # Unattainable makespan
        expected_task_count=999,  # Wrong task count
        task_assertions={"job_001_op_01": {"max_end": -5}},  # Negative end impossible
    )

    failures = verify_expected(sc, run_res.result, run_res.report)
    assert len(failures) == 3
    assert any("exceeded expected maximum" in f for f in failures)
    assert any("Expected 999 tasks" in f for f in failures)
    assert any("exceeded expected max_end" in f for f in failures)


def test_synthetic_scenario_generators(tmp_path: Path) -> None:
    """Synthetic benchmark generators must produce valid, solvable scenarios across scales."""
    # 1. Job shop
    js_sc = generate_jobshop_scenario(num_jobs=4, num_machines=3, operations_per_job=2, seed=10)
    assert len(js_sc.tasks) == 8
    res_js = run_scenario(js_sc, print_summary=False)
    assert res_js.is_success

    # 2. Workforce
    wf_sc = generate_workforce_scenario(num_staff=8, num_shifts=12, horizon_hours=48, seed=10)
    assert len(wf_sc.tasks) == 12
    res_wf = run_scenario(wf_sc, print_summary=False)
    assert res_wf.is_success

    # 3. Film
    film_sc = generate_film_scenario(num_scenes=10, num_cast=4, num_locations=2, seed=10)
    assert len(film_sc.tasks) == 10
    res_film = run_scenario(film_sc, print_summary=False)
    assert res_film.is_success

    # 4. Suite generation
    suite_files = generate_benchmark_suite(tmp_path, scales=["small"])
    assert len(suite_files) == 3
    for sf in suite_files:
        assert sf.exists()
