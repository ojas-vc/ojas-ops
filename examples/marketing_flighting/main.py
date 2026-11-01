"""Multi-channel marketing campaign cadence and budget flighting example."""

from ojas_ops.adapters import MarketingFlightingScheduler


def main() -> None:
    print("=== Ojas Ops: Multi-Channel Marketing Campaign Flighting ===")
    mkt = MarketingFlightingScheduler(total_campaign_days=45)

    # 1. Channels
    mkt.add_channel("meta_paid", name="Meta Social Video", max_concurrent_flights=1)
    mkt.add_channel("google_search", name="Google Intent Search", max_concurrent_flights=2)

    # 2. Sequential campaign flights
    mkt.add_flight(
        id="teaser_video",
        channel_id="meta_paid",
        duration_days=5,
        stage="teaser",
        daily_budget=2000.0,
    )
    mkt.add_flight(
        id="launch_blitz_meta",
        channel_id="meta_paid",
        duration_days=10,
        stage="launch",
        daily_budget=5000.0,
        dependencies=["teaser_video"],
    )
    mkt.add_flight(
        id="search_capture",
        channel_id="google_search",
        duration_days=15,
        stage="sustained",
        daily_budget=3000.0,
        dependencies=["teaser_video"],
    )

    scheduler = mkt.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    print(f"Status: {result.status.value}")
    print(f"Total Campaign Horizon: {result.makespan} days")

    for _tid, st in result.tasks.items():
        print(
            f" - [Day {st.start:02d} to Day {st.end:02d}] {st.task_id} ({st.duration} days) on {st.assigned_resources}"
        )

    print(f"Validation: {'VALID' if validation.is_valid else 'INVALID'}")


if __name__ == "__main__":
    main()
