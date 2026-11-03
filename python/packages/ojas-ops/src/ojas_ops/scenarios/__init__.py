"""Operational scenarios package for data-driven modeling, benchmarks, and golden assertions."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.scenarios.generator import (
    generate_benchmark_suite,
    generate_film_scenario,
    generate_jobshop_scenario,
    generate_workforce_scenario,
)
from ojas_ops.scenarios.loader import (
    build_scheduler,
    load_resources_from_csv,
    load_scenario,
    load_tasks_from_csv,
    save_resources_to_csv,
    save_scenario,
    save_tasks_to_csv,
    verify_expected,
)
from ojas_ops.scenarios.models import (
    CalendarSpec,
    CandidateRequirementSpec,
    ExpectedResult,
    MuhuratSpec,
    ObjectiveSpec,
    ResourceSpec,
    ScenarioDefinition,
    ScenarioMetadata,
    ScenarioRunResult,
    TaskSpec,
    TransitionSpec,
    WorkloadSpec,
)
from ojas_ops.scenarios.runner import print_scenario_summary, run_scenario

__all__ = [
    "CalendarSpec",
    "CandidateRequirementSpec",
    "ExpectedResult",
    "MuhuratSpec",
    "ObjectiveSpec",
    "ResourceSpec",
    "ScenarioDefinition",
    "ScenarioMetadata",
    "ScenarioRunResult",
    "TaskSpec",
    "TransitionSpec",
    "WorkloadSpec",
    "build_scheduler",
    "generate_benchmark_suite",
    "generate_film_scenario",
    "generate_jobshop_scenario",
    "generate_workforce_scenario",
    "load_resources_from_csv",
    "load_scenario",
    "load_tasks_from_csv",
    "print_scenario_summary",
    "run_scenario",
    "save_resources_to_csv",
    "save_scenario",
    "save_tasks_to_csv",
    "verify_expected",
]
