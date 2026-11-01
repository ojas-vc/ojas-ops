"""Academic course and classroom timetabling example."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.adapters import AcademicTimetableScheduler


def main() -> None:
    print("=== Ojas Ops: Academic Timetable Optimization ===")
    acad = AcademicTimetableScheduler(horizon_minutes=8 * 60)

    # 1. Faculty
    acad.add_instructor("prof_shannon", name="Prof. Claude Shannon")
    acad.add_instructor("prof_hopper", name="Prof. Grace Hopper")

    # 2. Classrooms
    acad.add_classroom("lecture_hall_a", name="Lecture Hall A", capacity=100, is_lab=False)
    acad.add_classroom("computer_lab_1", name="Computing Lab 1", capacity=30, is_lab=True)

    # 3. Student Batches
    acad.add_cohort("cs_seniors", name="CS Seniors Batch")

    # 4. Classes
    acad.add_class(
        id="info_theory_lec",
        code="CS401",
        name="Information Theory",
        duration_minutes=90,
        instructor_id="prof_shannon",
        cohort_ids=["cs_seniors"],
    )
    acad.add_class(
        id="compiler_lab",
        code="CS402",
        name="Compiler Systems Lab",
        duration_minutes=120,
        instructor_id="prof_hopper",
        cohort_ids=["cs_seniors"],
        is_lab=True,
    )

    scheduler = acad.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    for tid, st in result.tasks.items():
        print(f" - [{st.start:03d}m - {st.end:03d}m] {tid} Resources: {st.assigned_resources}")

    print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
