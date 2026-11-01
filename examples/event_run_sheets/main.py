"""Event conference agenda and occasion run-sheet example."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.adapters import EventRunSheetScheduler


def main() -> None:
    print("=== Ojas Ops: Multi-Track Conference & Run-Sheet Scheduling ===")
    event = EventRunSheetScheduler(event_duration_minutes=9 * 60)

    # 1. Halls
    event.add_hall("main_auditorium", name="Grand Plenary Hall", turnaround_minutes=20)
    event.add_hall("workshop_hall", name="Track B Tech Hall", turnaround_minutes=15)

    # 2. Speakers
    event.add_speaker("keynote_speaker", name="Dr. A. Turing", min_prep_buffer_minutes=30)
    event.add_speaker("panel_chair", name="Prof. J. McCarthy", min_prep_buffer_minutes=15)

    # 3. Sessions
    event.add_session(
        id="opening_keynote",
        title="Opening Keynote Address",
        duration_minutes=60,
        speaker_ids=["keynote_speaker"],
        hall_id="main_auditorium",
        fixed_start=0,
    )
    event.add_session(
        id="ai_panel",
        title="Future of Intelligence Panel",
        duration_minutes=75,
        speaker_ids=["keynote_speaker", "panel_chair"],
        hall_id="main_auditorium",
    )
    event.add_session(
        id="hands_on_lab",
        title="Hands-on Workshop",
        duration_minutes=90,
        speaker_ids=["panel_chair"],
        hall_id="workshop_hall",
    )

    scheduler = event.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    for _tid, st in result.tasks.items():
        print(f" - [{st.start:03d}m - {st.end:03d}m] {st.task_id} in {st.assigned_resources}")

    print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
