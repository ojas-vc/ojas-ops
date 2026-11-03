"""Scenario loader, scheduler builder, and expected outcome verification."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

import msgspec

from ojas_ops.calendars.cultural import CulturalCalendarProvider
from ojas_ops.calendars.standard import StandardCalendarProvider
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import ResourceRequirement
from ojas_ops.objectives.base import Objective
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.cost import MinimizeCostObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.objectives.tardiness import MinimizeTardinessObjective
from ojas_ops.scenarios.models import ResourceSpec, ScenarioDefinition, TaskSpec
from ojas_ops.scheduling.scheduler import Scheduler

if TYPE_CHECKING:
    from ojas_ops.models.schedule import ScheduleResult
    from ojas_ops.validation.report import ValidationReport


def load_scenario(path: str | Path) -> ScenarioDefinition:
    """Load a ScenarioDefinition from a JSON file using msgspec."""
    file_path = Path(path)
    if not file_path.exists():
        msg = f"Scenario file does not exist: {file_path}"
        raise FileNotFoundError(msg)

    raw_bytes = file_path.read_bytes()
    return msgspec.json.decode(raw_bytes, type=ScenarioDefinition)


def save_scenario(scenario: ScenarioDefinition, path: str | Path) -> None:
    """Serialize a ScenarioDefinition to a formatted JSON file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    raw_bytes = msgspec.json.encode(scenario)
    parsed = json.loads(raw_bytes)
    file_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")


def build_scheduler(scenario: ScenarioDefinition) -> Scheduler:
    """Instantiate and configure an operational Scheduler from a scenario dataset."""
    scheduler = Scheduler()
    if scenario.horizon:
        scheduler.set_horizon(
            start=scenario.horizon.start,
            end=scenario.horizon.end,
            granularity=scenario.horizon.granularity,
        )

    # 1. Register Resources
    for r in scenario.resources:
        scheduler.add_resource(
            id=r.id,
            name=r.name or r.id,
            capacity=r.capacity,
            resource_type=r.resource_type,
            cost_per_time_unit=r.cost_per_time_unit,
            regular_capacity_limit=r.regular_capacity_limit,
            skills=r.skills,
            blackout_windows=r.blackout_windows,
            metadata=r.metadata,
        )

    # 2. Register Tasks
    for t in scenario.tasks:
        reqs: list[ResourceRequirement] = []
        for pool in t.candidate_pools:
            reqs.append(
                ResourceRequirement(
                    resource_id=pool.candidate_pool[0] if pool.candidate_pool else "",
                    capacity=pool.capacity,
                    candidate_pool=pool.candidate_pool,
                )
            )

        scheduler.add_task(
            id=t.id,
            duration=t.duration,
            name=t.name or t.id,
            required_resources=t.required_resources,
            resource_requirements=reqs,
            dependencies=t.dependencies,
            priority=t.priority,
            time_window=t.time_window,
            fixed_start=t.fixed_start,
            cost=t.cost,
            metadata=t.metadata,
        )

    # 3. Transitions
    for trans in scenario.transitions:
        matrix: dict[tuple[str, str], int] = {}
        for key, delay in trans.matrix.items():
            if "," in key:
                parts = key.split(",", 1)
                matrix[(parts[0].strip(), parts[1].strip())] = delay
        scheduler.add_transition_matrix(
            resource_id=trans.resource_id,
            transition_matrix=matrix,
            default_buffer=trans.default_buffer,
        )

    # 4. Workloads
    for wl in scenario.workloads:
        if wl.max_duration is not None:
            scheduler.add_max_workload(wl.resource_id, wl.max_duration)
        if wl.min_rest is not None:
            scheduler.add_min_rest(wl.resource_id, wl.min_rest)

    # 5. Calendars
    if scenario.calendar:
        cal_spec = scenario.calendar
        if cal_spec.type == "cultural":
            cal = CulturalCalendarProvider(
                enable_rahu_kalam=cal_spec.enable_rahu_kalam,
                enable_yamagandam=cal_spec.enable_yamagandam,
            )
            for m in cal_spec.muhurats:
                cal.add_muhurat(
                    start=m.start,
                    end=m.end,
                    name=m.label,
                    task_id=m.task_id,
                    hard=m.hard,
                )
            scheduler.add_calendar(cal)
        elif cal_spec.type == "standard":
            std_cal = StandardCalendarProvider()
            scheduler.add_calendar(std_cal)

    # 6. Objectives
    obj_type = scenario.objective.type.lower()
    is_max = scenario.objective.is_maximize
    obj: Objective
    if obj_type == "makespan":
        obj = MinimizeMakespanObjective(weight=scenario.objective.weight, is_maximize=is_max)
    elif obj_type == "cost":
        obj = MinimizeCostObjective(weight=scenario.objective.weight, is_maximize=is_max)
    elif obj_type == "idle_time":
        obj = MinimizeIdleTimeObjective(weight=scenario.objective.weight, is_maximize=is_max)
    elif obj_type == "tardiness":
        obj = MinimizeTardinessObjective(weight=scenario.objective.weight, is_maximize=is_max)
    elif obj_type == "composite":
        sub_objs: list[Objective] = []
        for sub in scenario.objective.sub_objectives:
            sub_type = str(sub.get("type", "makespan")).lower()
            sub_weight = float(sub.get("weight", 1.0))
            sub_max = bool(sub.get("is_maximize", False))
            if sub_type == "makespan":
                sub_objs.append(MinimizeMakespanObjective(weight=sub_weight, is_maximize=sub_max))
            elif sub_type == "cost":
                sub_objs.append(MinimizeCostObjective(weight=sub_weight, is_maximize=sub_max))
            elif sub_type == "idle_time":
                sub_objs.append(MinimizeIdleTimeObjective(weight=sub_weight, is_maximize=sub_max))
            elif sub_type == "tardiness":
                sub_objs.append(MinimizeTardinessObjective(weight=sub_weight, is_maximize=sub_max))
        obj = WeightedCompositeObjective(
            sub_objs, weight=scenario.objective.weight, is_maximize=is_max
        )
    else:
        obj = MinimizeMakespanObjective()

    if is_max:
        scheduler.maximize(obj)
    else:
        scheduler.minimize(obj)

    return scheduler


def verify_expected(
    scenario: ScenarioDefinition,
    result: ScheduleResult,
    report: ValidationReport,
) -> list[str]:
    """Check solved schedule against golden expected assertions defined in the scenario."""
    failures: list[str] = []
    if not scenario.expected:
        return failures

    expected = scenario.expected

    # Status check
    if expected.status:
        exp_status = expected.status.lower()
        act_status = result.status.value.lower()
        if exp_status == "feasible":
            if act_status not in ("feasible", "optimal"):
                failures.append(
                    f"Expected feasible status, but solver returned '{result.status.value}'"
                )
        elif act_status != exp_status:
            failures.append(
                f"Expected status '{expected.status}', but solver returned '{result.status.value}'"
            )

    # Feasibility / validity check
    if expected.is_valid is not None and report.is_valid != expected.is_valid:
        failures.append(
            f"Expected validation validity '{expected.is_valid}', but got '{report.is_valid}' ({report.summary})"
        )

    # Makespan bounds
    if expected.max_makespan is not None and result.makespan > expected.max_makespan:
        failures.append(
            f"Makespan {result.makespan} exceeded expected maximum of {expected.max_makespan}"
        )
    if expected.min_makespan is not None and result.makespan < expected.min_makespan:
        failures.append(
            f"Makespan {result.makespan} below expected minimum of {expected.min_makespan}"
        )

    # Objective value bounds
    if (
        expected.max_objective_value is not None
        and result.objective_value > expected.max_objective_value
    ):
        failures.append(
            f"Objective value {result.objective_value} exceeded expected maximum of {expected.max_objective_value}"
        )

    # Task count
    if expected.expected_task_count is not None:
        actual_count = len(result.tasks)
        if actual_count != expected.expected_task_count:
            failures.append(
                f"Expected {expected.expected_task_count} tasks, but got {actual_count}"
            )

    # Detailed task assertions
    for tid, asserts in expected.task_assertions.items():
        st = result.tasks.get(tid)
        if not st:
            failures.append(f"Task '{tid}' named in task_assertions was not scheduled")
            continue
        if "max_end" in asserts and st.end > int(asserts["max_end"]):
            failures.append(
                f"Task '{tid}' end {st.end} exceeded expected max_end {asserts['max_end']}"
            )
        if "min_start" in asserts and st.start < int(asserts["min_start"]):
            failures.append(
                f"Task '{tid}' start {st.start} below expected min_start {asserts['min_start']}"
            )
        if (
            "assigned_resource" in asserts
            and asserts["assigned_resource"] not in st.assigned_resources
        ):
            failures.append(
                f"Task '{tid}' assigned {st.assigned_resources}, expected {asserts['assigned_resource']}"
            )

    return failures


def load_tasks_from_csv(csv_path: str | Path) -> list[TaskSpec]:
    """Helper to parse task specifications from a flat CSV file."""
    path = Path(csv_path)
    tasks: list[TaskSpec] = []
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row["id"].strip()
            duration = int(row["duration"])
            name = row.get("name", tid).strip()
            resources = [
                r.strip() for r in row.get("required_resources", "").split(";") if r.strip()
            ]
            dependencies = [d.strip() for d in row.get("dependencies", "").split(";") if d.strip()]
            cost = float(row.get("cost", 0.0) or 0.0)
            fixed_start = int(row["fixed_start"]) if row.get("fixed_start") else None
            tasks.append(
                TaskSpec(
                    id=tid,
                    duration=duration,
                    name=name,
                    required_resources=resources,
                    dependencies=dependencies,
                    cost=cost,
                    fixed_start=fixed_start,
                )
            )
    return tasks


def save_tasks_to_csv(tasks: list[TaskSpec], csv_path: str | Path) -> None:
    """Export tasks to a flat CSV file."""
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "name", "duration", "required_resources", "dependencies", "cost", "fixed_start"]
        )
        for t in tasks:
            writer.writerow(
                [
                    t.id,
                    t.name,
                    t.duration,
                    ";".join(t.required_resources),
                    ";".join(t.dependencies),
                    t.cost,
                    t.fixed_start if t.fixed_start is not None else "",
                ]
            )


def load_resources_from_csv(csv_path: str | Path) -> list[ResourceSpec]:
    """Helper to parse resource specifications from a flat CSV file."""
    path = Path(csv_path)
    resources: list[ResourceSpec] = []
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row["id"].strip()
            name = row.get("name", rid).strip()
            capacity = int(row.get("capacity", 1))
            res_type_str = row.get("resource_type", "machine").strip().lower()
            try:
                res_type = ResourceType(res_type_str)
            except ValueError:
                res_type = ResourceType.MACHINE
            cost = float(row.get("cost_per_time_unit", 0.0) or 0.0)
            skills = [s.strip() for s in row.get("skills", "").split(";") if s.strip()]
            resources.append(
                ResourceSpec(
                    id=rid,
                    name=name,
                    capacity=capacity,
                    resource_type=res_type,
                    cost_per_time_unit=cost,
                    skills=skills,
                )
            )
    return resources


def save_resources_to_csv(resources: list[ResourceSpec], csv_path: str | Path) -> None:
    """Export resources to a flat CSV file."""
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "capacity", "resource_type", "cost_per_time_unit", "skills"])
        for r in resources:
            writer.writerow(
                [
                    r.id,
                    r.name,
                    r.capacity,
                    r.resource_type.value,
                    r.cost_per_time_unit,
                    ";".join(r.skills),
                ]
            )
