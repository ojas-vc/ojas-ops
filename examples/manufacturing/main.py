"""Industrial job shop scheduling with machine changeovers."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.adapters import ManufacturingScheduler


def main() -> None:
    print("=== Ojas Ops: Industrial Manufacturing Scheduling ===")
    mfg = ManufacturingScheduler()

    # 1. Machines
    mfg.add_machine("cutting_station", name="Laser Cutting Station")
    mfg.add_machine("cnc_mill", name="5-Axis CNC Mill")

    # Sequence-dependent setup matrix between material families on CNC mill
    mfg.set_family_setup_time("cnc_mill", "steel", "aluminum", setup_minutes=25)
    mfg.set_family_setup_time("cnc_mill", "aluminum", "steel", setup_minutes=30)

    # 2. Jobs
    mfg.add_job("order_gears", name="Job: Precision Gears", due_date=240)
    mfg.add_operation("order_gears", "cut_gears", "cutting_station", duration_minutes=40)
    mfg.add_operation(
        "order_gears", "mill_gears", "cnc_mill", duration_minutes=60, product_family="steel"
    )

    mfg.add_job("order_brackets", name="Job: Aerospace Brackets", due_date=240)
    mfg.add_operation("order_brackets", "cut_brackets", "cutting_station", duration_minutes=30)
    mfg.add_operation(
        "order_brackets",
        "mill_brackets",
        "cnc_mill",
        duration_minutes=50,
        product_family="aluminum",
    )

    scheduler = mfg.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    print(f"Makespan: {result.makespan} mins")

    for tid, st in result.tasks.items():
        print(f" - [{st.start:03d}m - {st.end:03d}m] {tid} on {st.assigned_resources}")

    print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
