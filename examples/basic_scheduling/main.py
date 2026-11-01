"""Basic scheduling example demonstrating core flow: modeling, solving, and validation."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops import Scheduler
from ojas_ops.models import IntervalWindow, ResourceType


def main() -> None:
    print("=== Ojas Ops: Basic Scheduling Example ===")
    scheduler = Scheduler()

    # 1. Add resource (e.g. main auditorium)
    scheduler.add_resource(
        id="main-auditorium",
        capacity=1,
        resource_type=ResourceType.FACILITY,
    )

    # 2. Add tasks
    scheduler.add_task(
        id="sound-check",
        duration=30,
        required_resources=["main-auditorium"],
    )
    scheduler.add_task(
        id="keynote-launch",
        duration=60,
        required_resources=["main-auditorium"],
        dependencies=["sound-check"],
    )

    # 3. Add blackout window (e.g. cleaning window)
    scheduler.add_blackout_window(
        resource_id="main-auditorium",
        window=IntervalWindow(start=40, end=90, label="cleaning_and_reset"),
    )

    # 4. Set target window for keynote (e.g. auspicious launch window)
    scheduler.add_target_window(
        task_id="keynote-launch",
        window=IntervalWindow(start=100, end=200, label="auspicious_window"),
        hard=True,
    )

    scheduler.minimize("makespan")

    # 5. Solve using Google OR-Tools CP-SAT
    result = scheduler.solve()
    print(f"Solver Status: {result.status.value}")
    print(f"Makespan: {result.makespan} minutes")

    for tid, task in result.tasks.items():
        print(f" - [{task.start:03d} - {task.end:03d}] {tid} (Duration: {task.duration}m)")

    # 6. Independent validation
    validation = scheduler.validate(result)
    print(f"Validation: {'PASSED' if validation.is_valid else 'FAILED'} - {validation.summary}")


if __name__ == "__main__":
    main()
