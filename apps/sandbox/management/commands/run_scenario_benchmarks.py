"""Django management command to execute scenario benchmarks and store results in Django models."""

import json
import time

import msgspec
from django.core.management.base import BaseCommand
from ojas_ops.adapters.film_production import ProductionDataset, optimize_production_schedule
from ojas_ops.models.scenario_record import ScenarioRecord
from ojas_ops.models.schedule_run import ScheduleRun

BASE_BENCHMARK_DATA = {
    "project_title": "Sandbox Benchmark Film",
    "talents": [
        {
            "id": 1,
            "name": "Marcus Vance",
            "character_name": "Commander Reyes",
            "daily_rate": 8000.0,
            "is_minor": False,
            "max_daily_hours": 12.0,
            "hmu_duration_minutes": 60,
            "wardrobe_duration_minutes": 30,
            "travel_duration_minutes": 45,
            "blackout_days": [],
        },
        {
            "id": 2,
            "name": "Elena Rostova",
            "character_name": "Dr. Aris",
            "daily_rate": 5500.0,
            "is_minor": False,
            "max_daily_hours": 12.0,
            "hmu_duration_minutes": 45,
            "wardrobe_duration_minutes": 20,
            "travel_duration_minutes": 30,
            "blackout_days": [],
        },
    ],
    "locations": [
        {
            "id": 1,
            "name": "Soundstage 4",
            "location_type": "SOUNDSTAGE",
            "permitted_days": [1, 2, 3, 4, 5],
            "noise_curfew_hour": None,
            "allows_sync_sound": True,
            "daily_rental_cost": 2500.0,
            "prep_days_required": 1,
            "strike_days_required": 1,
        },
        {
            "id": 2,
            "name": "Desert Outpost",
            "location_type": "PRACTICAL_EXT",
            "permitted_days": [1, 2, 5],
            "noise_curfew_hour": 22,
            "allows_sync_sound": False,
            "daily_rental_cost": 1200.0,
            "prep_days_required": 0,
            "strike_days_required": 0,
        },
    ],
    "props": [],
    "costumes": [],
    "specialty_equipments": [],
    "stunt_packages": [],
    "calendar_days": [
        {"day_number": 1, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 2, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 3, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 4, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
        {"day_number": 5, "is_work_day": True, "weather": "CLEAR", "is_holiday": False},
    ],
    "production_units": [
        {"id": 1, "name": "Main Unit", "unit_type": "FIRST_UNIT", "max_operating_hours": 12.0}
    ],
    "camera_setups": [],
    "location_travel_matrix": [],
    "max_shooting_days": 5,
    "max_hours_per_day": 12.0,
}


def build_scenes(count: int) -> list[dict]:
    scenes = []
    for i in range(1, count + 1):
        scenes.append(
            {
                "id": i,
                "scene_number": str(i),
                "script_day": 1,
                "pages_eighths": 16,
                "setting": "INT" if i % 2 == 0 else "EXT",
                "time_of_day": "DAY" if i % 4 != 0 else "NIGHT",
                "location_id": 1 if i % 2 == 0 else 2,
                "required_talent_ids": [1] if i % 3 == 0 else [1, 2],
                "required_prop_ids": [],
                "required_costume_ids": [],
                "required_equipment_ids": [],
                "stunt_package_id": None,
                "camera_setup_ids": [],
                "preferred_unit": "FIRST_UNIT",
                "weather_requirement": "ANY",
                "sound_recording": "SYNC_SOUND",
                "estimated_minutes": 120,
                "sequence_dependent_setup_minutes": 15,
                "is_locked": False,
                "locked_day": None,
                "earliest_day": 1,
                "latest_day": 5,
            }
        )
    return scenes


class Command(BaseCommand):
    help = "Executes benchmark combinatorial optimization scenarios and logs results."

    def add_arguments(self, parser):
        parser.add_argument(
            "--scale",
            choices=["small", "medium", "large"],
            default="small",
            help="Scale of benchmark scenario to execute",
        )
        parser.add_argument(
            "--time-limit",
            type=int,
            default=10,
            help="CP-SAT solver time limit in seconds",
        )

    def handle(self, *args, **options):
        scale = options["scale"]
        time_limit = options["time_limit"]

        num_scenes = 4 if scale == "small" else (8 if scale == "medium" else 14)

        self.stdout.write(
            self.style.NOTICE(
                f"Running '{scale}' Film Production Benchmark with {num_scenes} scenes (time_limit={time_limit}s)..."
            )
        )

        dataset = dict(BASE_BENCHMARK_DATA)
        dataset["scenes"] = build_scenes(num_scenes)
        dataset_json = json.dumps(dataset)
        dataset_struct = msgspec.json.decode(dataset_json.encode(), type=ProductionDataset)

        start_time = time.perf_counter()
        result = optimize_production_schedule(dataset_struct, max_time_in_seconds=float(time_limit))
        duration_s = time.perf_counter() - start_time

        total_days = result.stripboard.total_shoot_days if result.stripboard else 0
        total_cost = result.objective_cost

        self.stdout.write(
            self.style.SUCCESS(
                f"Benchmark Complete:\n"
                f"  Status: {result.status.value}\n"
                f"  Total Days: {total_days}\n"
                f"  Total Cost: ${total_cost:,.2f}\n"
                f"  Wall Time: {duration_s:.3f}s"
            )
        )

        scenario = ScenarioRecord.objects.create(
            name=f"film_benchmark_{scale}",
            domain="film_production",
            scale=scale,
            definition_json={
                "scene_count": num_scenes,
                "talent_count": len(dataset["talents"]),
                "location_count": len(dataset["locations"]),
            },
            golden_expected_json={
                "status": result.status.value,
                "total_days": total_days,
                "total_cost": total_cost,
                "wall_time_seconds": duration_s,
            },
        )

        ScheduleRun.objects.create(
            tenant_id="benchmark",
            scenario_name=f"film_benchmark_{scale}",
            status=result.status.value,
            makespan=total_days,
            objective_value=int(total_cost * 100),
            solver_status=result.status.value,
            solve_time_seconds=duration_s,
            metadata={
                "scenario_record_id": scenario.id,
                "is_feasible": result.is_feasible,
                "tasks_count": num_scenes,
                "resources_count": len(dataset["talents"]) + len(dataset["locations"]),
            },
        )
        self.stdout.write(
            self.style.SUCCESS(f"Recorded ScenarioRecord #{scenario.id} and ScheduleRun in DB.")
        )
