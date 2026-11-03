"""Synthetic scenario generators for large-scale benchmarks and stress testing."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import random
from pathlib import Path

from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import Horizon
from ojas_ops.scenarios.loader import save_scenario
from ojas_ops.scenarios.models import (
    CandidateRequirementSpec,
    ExpectedResult,
    ObjectiveSpec,
    ResourceSpec,
    ScenarioDefinition,
    ScenarioMetadata,
    TaskSpec,
    TransitionSpec,
    WorkloadSpec,
)


def generate_jobshop_scenario(
    num_jobs: int = 10,
    num_machines: int = 5,
    operations_per_job: int = 4,
    *,
    setup_matrix_enabled: bool = True,
    seed: int = 42,
) -> ScenarioDefinition:
    """Generate an industrial Job Shop Scheduling Problem (JSSP) scenario.

    Each job consists of a strict linear sequence of operations visiting different machines.
    """
    rng = random.Random(seed)
    machines = [
        ResourceSpec(
            id=f"machine_{m + 1:02d}",
            name=f"Workstation {m + 1:02d}",
            capacity=1,
            resource_type=ResourceType.MACHINE,
            cost_per_time_unit=round(rng.uniform(20.0, 80.0), 2),
        )
        for m in range(num_machines)
    ]

    tasks: list[TaskSpec] = []
    transitions: list[TransitionSpec] = []

    for j in range(num_jobs):
        job_id = f"job_{j + 1:03d}"
        machine_order = list(range(num_machines))
        rng.shuffle(machine_order)
        # Select operations_per_job machines
        selected_machines = machine_order[:operations_per_job]

        prev_op_id: str | None = None
        for step, m_idx in enumerate(selected_machines):
            op_id = f"{job_id}_op_{step + 1:02d}"
            dur = rng.randint(15, 60)
            deps = [prev_op_id] if prev_op_id else []
            tasks.append(
                TaskSpec(
                    id=op_id,
                    name=f"Job {j + 1:03d} Step {step + 1} (M{m_idx + 1:02d})",
                    duration=dur,
                    required_resources=[machines[m_idx].id],
                    dependencies=deps,
                    priority=TaskPriority.NORMAL,
                )
            )
            prev_op_id = op_id

    # Optional sequence-dependent setups on each machine
    if setup_matrix_enabled:
        for m in machines:
            m_tasks = [t.id for t in tasks if m.id in t.required_resources]
            if len(m_tasks) > 1:
                matrix: dict[str, int] = {}
                for t1 in m_tasks:
                    for t2 in m_tasks:
                        if t1 != t2:
                            matrix[f"{t1},{t2}"] = rng.choice([5, 10, 15, 20])
                transitions.append(
                    TransitionSpec(resource_id=m.id, default_buffer=10, matrix=matrix)
                )

    scale_label = "small" if len(tasks) <= 20 else "medium" if len(tasks) <= 100 else "large"
    return ScenarioDefinition(
        metadata=ScenarioMetadata(
            name=f"Job Shop Benchmark ({num_jobs} jobs x {operations_per_job} ops on {num_machines} machines)",
            description="Synthetic sequence-dependent job shop scheduling benchmark.",
            domain="manufacturing",
            scale=scale_label,
            tags=["jobshop", "manufacturing", "transitions", "benchmark"],
        ),
        resources=machines,
        tasks=tasks,
        transitions=transitions,
        objective=ObjectiveSpec(type="makespan", is_maximize=False, weight=1.0),
        expected=ExpectedResult(status="optimal", is_valid=True, expected_task_count=len(tasks)),
    )


def generate_workforce_scenario(
    num_staff: int = 15,
    num_shifts: int = 24,
    horizon_hours: int = 48,
    *,
    seed: int = 42,
    num_nurses: int | None = None,
    num_days: int | None = None,
) -> ScenarioDefinition:
    """Generate a healthcare or workforce shift-rostering scenario with skill qualification pools."""
    if num_nurses is not None:
        num_staff = num_nurses
    if num_days is not None:
        horizon_hours = num_days * 24
    rng = random.Random(seed)
    all_skills = ["icu", "triage", "emergency", "pediatric", "general"]

    staff_resources: list[ResourceSpec] = []
    workloads: list[WorkloadSpec] = []

    for i in range(num_staff):
        s_id = f"staff_{i + 1:03d}"
        # Assign 1 to 3 skills
        s_skills = rng.sample(all_skills, k=rng.randint(1, 3))
        if "general" not in s_skills:
            s_skills.append("general")
        staff_resources.append(
            ResourceSpec(
                id=s_id,
                name=f"Nurse {i + 1:03d}",
                capacity=1,
                resource_type=ResourceType.PERSON,
                skills=s_skills,
                cost_per_time_unit=round(rng.uniform(35.0, 75.0), 2),
            )
        )
        max_allowed_mins = int(max(1, (horizon_hours // 24)) * 12 * 60)
        workloads.append(
            WorkloadSpec(
                resource_id=s_id,
                max_duration=max_allowed_mins,
                min_rest=8 * 60,  # Min 8 hours rest between shifts
            )
        )

    tasks: list[TaskSpec] = []
    shift_duration = 8 * 60  # 8 hours = 480 mins
    slots_per_day = 3  # morning (0-8h), evening (8-16h), night (16-24h)

    for s in range(num_shifts):
        shift_idx = s % (slots_per_day * (horizon_hours // 24))
        day = shift_idx // slots_per_day
        slot = shift_idx % slots_per_day
        start_minute = (day * 24 + slot * 8) * 60
        required_skill = rng.choice(all_skills)

        # Candidate pool is staff who possess required_skill
        qualified_staff = [r.id for r in staff_resources if required_skill in r.skills]
        if not qualified_staff:
            qualified_staff = [staff_resources[0].id]

        tasks.append(
            TaskSpec(
                id=f"shift_{s + 1:03d}",
                name=f"Shift {s + 1:03d} ({required_skill.upper()} - Day {day + 1} Slot {slot + 1})",
                duration=shift_duration,
                fixed_start=start_minute,
                candidate_pools=[
                    CandidateRequirementSpec(candidate_pool=qualified_staff, capacity=1)
                ],
                priority=TaskPriority.NORMAL,
            )
        )

    scale_label = "small" if len(tasks) <= 15 else "medium" if len(tasks) <= 60 else "large"
    return ScenarioDefinition(
        metadata=ScenarioMetadata(
            name=f"Healthcare Rostering ({num_staff} staff across {num_shifts} shifts over {horizon_hours}h)",
            description="Synthetic workforce qualification and minimum rest rest-rostering scenario.",
            domain="healthcare",
            scale=scale_label,
            tags=["workforce", "rostering", "candidate_pools", "rest_constraint"],
        ),
        horizon=Horizon(start=0, end=horizon_hours * 60, granularity=1),
        resources=staff_resources,
        tasks=tasks,
        workloads=workloads,
        objective=ObjectiveSpec(type="cost", is_maximize=False, weight=1.0),
        expected=ExpectedResult(status="feasible", is_valid=True, expected_task_count=len(tasks)),
    )


def generate_film_scenario(
    num_scenes: int = 25,
    num_cast: int = 8,
    num_locations: int = 4,
    *,
    seed: int = 42,
    num_actors: int | None = None,
) -> ScenarioDefinition:
    """Generate a media/film production shooting schedule scenario with cast and location turnaround."""
    if num_actors is not None:
        num_cast = num_actors
    rng = random.Random(seed)

    cast_resources = [
        ResourceSpec(
            id=f"cast_{c + 1:02d}",
            name=f"Actor {c + 1:02d}",
            capacity=1,
            resource_type=ResourceType.PERSON,
            cost_per_time_unit=round(rng.uniform(500.0, 2500.0), 2),
        )
        for c in range(num_cast)
    ]

    location_resources = [
        ResourceSpec(
            id=f"loc_{loc_idx + 1:02d}",
            name=f"Location {loc_idx + 1:02d}",
            capacity=1,
            resource_type=ResourceType.LOCATION,
            cost_per_time_unit=round(rng.uniform(100.0, 400.0), 2),
        )
        for loc_idx in range(num_locations)
    ]

    tasks: list[TaskSpec] = []
    transitions: list[TransitionSpec] = []

    for s in range(num_scenes):
        scene_id = f"scene_{s + 1:03d}"
        dur = rng.randint(45, 120)
        loc = rng.choice(location_resources)
        # Select 1 to 3 cast members
        cast_count = min(len(cast_resources), rng.randint(1, 3))
        selected_cast = rng.sample(cast_resources, k=cast_count)

        req_resources = [loc.id] + [c.id for c in selected_cast]

        # Optional narrative dependency on an earlier scene
        deps = []
        if s > 0 and rng.random() < 0.25:
            deps.append(f"scene_{s:03d}")

        tasks.append(
            TaskSpec(
                id=scene_id,
                name=f"Scene {s + 1:03d} at {loc.name}",
                duration=dur,
                required_resources=req_resources,
                dependencies=deps,
                priority=TaskPriority.NORMAL,
            )
        )

    # Location turnaround transitions
    for loc in location_resources:
        loc_tasks = [t.id for t in tasks if loc.id in t.required_resources]
        if len(loc_tasks) > 1:
            matrix: dict[str, int] = {}
            turnaround = rng.choice([20, 30, 45])
            for t1 in loc_tasks:
                for t2 in loc_tasks:
                    if t1 != t2:
                        matrix[f"{t1},{t2}"] = turnaround
            transitions.append(
                TransitionSpec(resource_id=loc.id, default_buffer=turnaround, matrix=matrix)
            )

    scale_label = "small" if len(tasks) <= 15 else "medium" if len(tasks) <= 60 else "large"
    return ScenarioDefinition(
        metadata=ScenarioMetadata(
            name=f"Film Production ({num_scenes} scenes, {num_cast} cast, {num_locations} locations)",
            description="Synthetic film schedule minimizing shoot duration and turnaround transitions.",
            domain="film_production",
            scale=scale_label,
            tags=["film", "media", "transitions", "locations"],
        ),
        resources=cast_resources + location_resources,
        tasks=tasks,
        transitions=transitions,
        objective=ObjectiveSpec(type="makespan", is_maximize=False, weight=1.0),
        expected=ExpectedResult(status="optimal", is_valid=True, expected_task_count=len(tasks)),
    )


def generate_benchmark_suite(
    output_dir: str | Path,
    scales: list[str] | None = None,
) -> list[Path]:
    """Generate and write a suite of synthetic scenarios across scales (small, medium, large)."""
    scales = scales or ["small", "medium", "large"]
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    configs = {
        "small": {"jobs": 6, "machines": 3, "ops": 3, "staff": 8, "shifts": 12, "scenes": 12},
        "medium": {"jobs": 15, "machines": 5, "ops": 4, "staff": 18, "shifts": 36, "scenes": 30},
        "large": {"jobs": 30, "machines": 8, "ops": 5, "staff": 35, "shifts": 72, "scenes": 60},
    }

    for scale in scales:
        cfg = configs.get(scale, configs["medium"])
        # Job shop
        js_sc = generate_jobshop_scenario(
            num_jobs=cfg["jobs"],
            num_machines=cfg["machines"],
            operations_per_job=cfg["ops"],
            seed=42,
        )
        js_path = out_path / f"jobshop_{scale}.json"
        save_scenario(js_sc, js_path)
        generated.append(js_path)

        # Workforce
        wf_sc = generate_workforce_scenario(
            num_staff=cfg["staff"],
            num_shifts=cfg["shifts"],
            horizon_hours=48 if scale != "large" else 96,
            seed=42,
        )
        wf_path = out_path / f"workforce_{scale}.json"
        save_scenario(wf_sc, wf_path)
        generated.append(wf_path)

        # Film
        film_sc = generate_film_scenario(
            num_scenes=cfg["scenes"],
            num_cast=min(cfg["scenes"] // 2, 12),
            num_locations=max(3, cfg["machines"] - 1),
            seed=42,
        )
        film_path = out_path / f"film_{scale}.json"
        save_scenario(film_sc, film_path)
        generated.append(film_path)

    return generated
