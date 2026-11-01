"""Multi-channel marketing campaign cadence and budget flighting adapter."""

from __future__ import annotations

import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import TimeWindow
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler


class MediaFlight(msgspec.Struct, kw_only=True):
    """An advertising flight on a specific channel during a campaign stage."""

    id: str
    name: str = ""
    channel_id: str
    stage: str = "launch"  # teaser, launch, sustained, countdown
    duration_days: int = 7
    daily_budget: float = 1000.0
    projected_leads_per_day: int = 50
    earliest_day: int | None = None
    latest_day: int | None = None
    dependencies: list[str] = msgspec.field(default_factory=list)


class MarketingChannel(msgspec.Struct, kw_only=True):
    """An advertising channel with budget boundaries and audience fatigue limits."""

    id: str
    name: str = ""
    max_concurrent_flights: int = 1
    daily_budget_cap: float = 50000.0


class MarketingFlightingScheduler(DomainAdapter):
    """Schedules synchronized multi-channel advertising flights with lead absorption smoothing."""

    def __init__(self, *, total_campaign_days: int = 60) -> None:
        self.total_campaign_days = total_campaign_days
        self.channels: dict[str, MarketingChannel] = {}
        self.flights: dict[str, MediaFlight] = {}

    def add_channel(
        self,
        id: str,
        name: str = "",
        max_concurrent_flights: int = 1,
        daily_budget_cap: float = 50000.0,
    ) -> MarketingChannel:
        ch = MarketingChannel(
            id=id,
            name=name or id,
            max_concurrent_flights=max_concurrent_flights,
            daily_budget_cap=daily_budget_cap,
        )
        self.channels[id] = ch
        return ch

    def add_flight(
        self,
        id: str,
        channel_id: str,
        duration_days: int,
        name: str = "",
        stage: str = "launch",
        daily_budget: float = 1000.0,
        projected_leads_per_day: int = 50,
        earliest_day: int | None = None,
        latest_day: int | None = None,
        dependencies: list[str] | None = None,
    ) -> MediaFlight:
        fl = MediaFlight(
            id=id,
            name=name or id,
            channel_id=channel_id,
            stage=stage,
            duration_days=duration_days,
            daily_budget=daily_budget,
            projected_leads_per_day=projected_leads_per_day,
            earliest_day=earliest_day,
            latest_day=latest_day,
            dependencies=dependencies or [],
        )
        self.flights[id] = fl
        return fl

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()
        scheduler.set_horizon(0, self.total_campaign_days)

        # 1. Add channels as resources (capacity = max_concurrent_flights)
        for ch_id, ch in self.channels.items():
            scheduler.add_resource(
                id=f"channel:{ch_id}",
                name=ch.name,
                capacity=ch.max_concurrent_flights,
                resource_type=ResourceType.CHANNEL,
            )

        # 2. Add flights as tasks
        for f_id, fl in self.flights.items():
            tw = None
            if fl.earliest_day is not None or fl.latest_day is not None:
                tw = TimeWindow(
                    earliest_start=fl.earliest_day,
                    latest_end=fl.latest_day,
                )

            scheduler.add_task(
                id=f_id,
                duration=fl.duration_days,
                name=f"[{fl.stage.upper()}] {fl.name}",
                required_resources=[f"channel:{fl.channel_id}"],
                dependencies=fl.dependencies,
                time_window=tw,
                priority=TaskPriority.HIGH if fl.stage == "launch" else TaskPriority.NORMAL,
                cost=fl.daily_budget * fl.duration_days,
            )

        # 3. Minimize total makespan
        scheduler.minimize(MinimizeMakespanObjective())

        return scheduler
