"""Basic scheduling example: data-driven scenario loading, solving, and validation."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import sys
from pathlib import Path

from ojas_ops.scenarios import (
    ObjectiveSpec,
    ScenarioDefinition,
    ScenarioMetadata,
    load_resources_from_csv,
    load_tasks_from_csv,
    run_scenario,
)


def main() -> None:
    data_dir = Path(__file__).parent / "data"

    if len(sys.argv) > 1 and sys.argv[1] in ("--csv", "-c"):
        print("=== Ojas Ops: Loading Scheduling Problem from CSV ===")
        tasks = load_tasks_from_csv(data_dir / "tasks.csv")
        resources = load_resources_from_csv(data_dir / "resources.csv")
        scenario = ScenarioDefinition(
            metadata=ScenarioMetadata(
                name="Factory Production Flow (CSV)",
                domain="manufacturing",
                scale="small",
            ),
            resources=resources,
            tasks=tasks,
            objective=ObjectiveSpec(type="makespan"),
        )
        run_scenario(scenario)
    else:
        scenario_path = Path(sys.argv[1]) if len(sys.argv) > 1 else data_dir / "basic_factory.json"
        print(f"=== Ojas Ops: Loading Scheduling Scenario from {scenario_path.name} ===")
        run_scenario(scenario_path)


if __name__ == "__main__":
    main()
