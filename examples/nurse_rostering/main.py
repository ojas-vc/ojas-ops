"""Healthcare and nurse shift rostering example."""

from ojas_ops.adapters import WorkforceScheduler


def main() -> None:
    print("=== Ojas Ops: Healthcare Workforce Rostering ===")
    wf = WorkforceScheduler(horizon_minutes=24 * 60)

    # 1. Staff
    wf.add_staff(
        "nurse_sarah", name="Sarah (ICU Specialist)", skills=["icu", "triage"], min_rest_minutes=120
    )
    wf.add_staff(
        "nurse_david", name="David (General + ICU)", skills=["general", "icu"], min_rest_minutes=120
    )
    wf.add_staff(
        "nurse_elena", name="Elena (Triage)", skills=["general", "triage"], min_rest_minutes=120
    )

    # 2. Shift Slots
    wf.add_shift(
        "shift_01_morn_icu",
        start_minute=0,
        duration_minutes=8 * 60,
        name="Morning ICU",
        required_skills=["icu"],
    )
    wf.add_shift(
        "shift_02_morn_triage",
        start_minute=0,
        duration_minutes=8 * 60,
        name="Morning Triage",
        required_skills=["triage"],
    )
    wf.add_shift(
        "shift_03_eve_icu",
        start_minute=8 * 60,
        duration_minutes=8 * 60,
        name="Evening ICU",
        required_skills=["icu"],
    )

    scheduler = wf.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    for _tid, st in result.tasks.items():
        print(
            f" - [{st.start // 60:02d}:00 - {st.end // 60:02d}:00] {st.task_id} Assigned: {st.assigned_resources}"
        )

    print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
