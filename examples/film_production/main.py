"""Film and media shooting schedule optimization example."""

from ojas_ops.adapters import FilmProductionScheduler


def main() -> None:
    print("=== Ojas Ops: Film Production Scheduling ===")
    film = FilmProductionScheduler()

    # 1. Cast
    film.add_cast_member("lead_actor", name="Lead Star", day_rate=10000.0)
    film.add_cast_member("supporting_actor", name="Supporting Artist", day_rate=3000.0)

    # 2. Locations
    film.add_location("palace_courtyard", name="Palace Courtyard", turnaround_minutes=30)
    film.add_location("studio_stage_b", name="Soundstage B", turnaround_minutes=20)

    # 3. Scenes
    film.add_scene(
        id="scene_01",
        scene_number="Scene 1 (Intro)",
        duration_minutes=90,
        character_ids=["lead_actor"],
        location_id="palace_courtyard",
    )
    film.add_scene(
        id="scene_02",
        scene_number="Scene 2 (Dialogue)",
        duration_minutes=120,
        character_ids=["lead_actor", "supporting_actor"],
        location_id="palace_courtyard",
        dependencies=["scene_01"],
    )
    film.add_scene(
        id="scene_03",
        scene_number="Scene 3 (Studio Action)",
        duration_minutes=150,
        character_ids=["supporting_actor"],
        location_id="studio_stage_b",
    )

    scheduler = film.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    print(f"Total Shooting Duration: {result.makespan} mins")

    for _tid, st in result.tasks.items():
        print(f" - [{st.start:03d}m - {st.end:03d}m] {st.task_id}: {st.assigned_resources}")

    print(f"Independent Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
