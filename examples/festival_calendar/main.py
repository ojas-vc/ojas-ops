"""Cultural, Panchang, and festival calendar-aware scheduling example."""

from ojas_ops import Scheduler
from ojas_ops.calendars import CulturalCalendarProvider
from ojas_ops.models import ResourceType


def main() -> None:
    print("=== Ojas Ops: Cultural & Astrological Calendar Scheduling ===")
    scheduler = Scheduler()

    # 1. Cultural calendar with Rahu Kalam and Yamagandam blackouts enabled
    cultural_cal = CulturalCalendarProvider(
        horizon_days=7,
        enable_rahu_kalam=True,
        enable_yamagandam=True,
    )

    # 2. Add an auspicious Shubh Muhurat window on Day 0 (e.g. 11:00 to 13:00 = 660 to 780 mins)
    cultural_cal.add_muhurat(
        start=660,
        end=780,
        name="Vedic Shubh Muhurat",
        task_id="inauguration_ceremony",
    )

    scheduler.add_calendar(cultural_cal)

    # 3. Add resources and tasks
    scheduler.add_resource("grand_hall", capacity=1, resource_type=ResourceType.FACILITY)

    scheduler.add_task(
        id="inauguration_ceremony",
        duration=60,
        name="Grand Inauguration & Foundation Stone Laying",
        required_resources=["grand_hall"],
    )

    scheduler.add_task(
        id="public_reception",
        duration=90,
        name="Public Reception & Cultural Performance",
        required_resources=["grand_hall"],
        dependencies=["inauguration_ceremony"],
    )

    scheduler.minimize("makespan")

    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    for tid, st in result.tasks.items():
        print(f" - [{st.start:04d}m - {st.end:04d}m] {tid}: {st.duration} mins")

    # Confirm inauguration falls inside the Muhurat window [660, 780]
    inaug = result.tasks["inauguration_ceremony"]
    print(f"Inauguration executed during: {inaug.start}m - {inaug.end}m (Target: 660m - 780m)")
    assert 660 <= inaug.start and inaug.end <= 780

    print(f"Independent Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()

