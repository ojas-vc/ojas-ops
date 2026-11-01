"""Film and media production shooting schedule adapter."""

from __future__ import annotations

import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler


class Scene(msgspec.Struct, kw_only=True):
    """A screenplay scene requiring actors, location, and specific lighting."""

    id: str
    scene_number: str
    duration_minutes: int
    character_ids: list[str]
    location_id: str
    is_night: bool = False
    is_exterior: bool = False
    dependencies: list[str] = msgspec.field(default_factory=list)


class CastMember(msgspec.Struct, kw_only=True):
    """An actor or artist with daily availability and rate."""

    id: str
    name: str
    day_rate: float = 0.0
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class ShootingLocation(msgspec.Struct, kw_only=True):
    """A film set or practical location."""

    id: str
    name: str
    turnaround_minutes: int = 60
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class FilmProductionScheduler(DomainAdapter):
    """Generates optimized film shooting schedules minimizing shoot days, location moves, and cast idle time."""

    def __init__(
        self,
        *,
        shoot_day_hours: int = 10,
        day_start_hour: int = 8,
        night_start_hour: int = 19,
    ) -> None:
        self.shoot_day_hours = shoot_day_hours
        self.day_start_hour = day_start_hour
        self.night_start_hour = night_start_hour

        self.scenes: dict[str, Scene] = {}
        self.cast: dict[str, CastMember] = {}
        self.locations: dict[str, ShootingLocation] = {}
        self.location_travel_times: dict[tuple[str, str], int] = {}

    def add_cast_member(
        self,
        id: str,
        name: str = "",
        day_rate: float = 0.0,
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> CastMember:
        member = CastMember(
            id=id,
            name=name or id,
            day_rate=day_rate,
            blackout_windows=blackout_windows or [],
        )
        self.cast[id] = member
        return member

    def add_location(
        self,
        id: str,
        name: str = "",
        turnaround_minutes: int = 60,
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> ShootingLocation:
        loc = ShootingLocation(
            id=id,
            name=name or id,
            turnaround_minutes=turnaround_minutes,
            blackout_windows=blackout_windows or [],
        )
        self.locations[id] = loc
        return loc

    def add_scene(
        self,
        id: str,
        scene_number: str,
        duration_minutes: int,
        character_ids: list[str],
        location_id: str,
        is_night: bool = False,
        is_exterior: bool = False,
        dependencies: list[str] | None = None,
    ) -> Scene:
        scene = Scene(
            id=id,
            scene_number=scene_number,
            duration_minutes=duration_minutes,
            character_ids=character_ids,
            location_id=location_id,
            is_night=is_night,
            is_exterior=is_exterior,
            dependencies=dependencies or [],
        )
        self.scenes[id] = scene
        return scene

    def set_location_travel(self, loc1: str, loc2: str, travel_minutes: int) -> None:
        self.location_travel_times[(loc1, loc2)] = travel_minutes
        self.location_travel_times[(loc2, loc1)] = travel_minutes

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()

        # 1. Add cast resources (capacity = 1)
        for cast_id, member in self.cast.items():
            scheduler.add_resource(
                id=f"cast:{cast_id}",
                name=member.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
                blackout_windows=member.blackout_windows,
            )

        # 2. Add location resources (capacity = 1)
        for loc_id, loc in self.locations.items():
            scheduler.add_resource(
                id=f"loc:{loc_id}",
                name=loc.name,
                capacity=1,
                resource_type=ResourceType.LOCATION,
                blackout_windows=loc.blackout_windows,
            )

        # 3. Add scenes as tasks
        for scene_id, scene in self.scenes.items():
            required_resources = [f"loc:{scene.location_id}"]
            for cid in scene.character_ids:
                if cid in self.cast:
                    required_resources.append(f"cast:{cid}")

            scheduler.add_task(
                id=scene_id,
                duration=scene.duration_minutes,
                name=f"Scene {scene.scene_number}",
                required_resources=required_resources,
                dependencies=scene.dependencies,
                priority=TaskPriority.NORMAL,
            )

        # 4. Add location turnaround transitions
        for loc_id, loc in self.locations.items():
            loc_scenes = [s_id for s_id, s in self.scenes.items() if s.location_id == loc_id]
            if len(loc_scenes) > 1:
                matrix: dict[tuple[str, str], int] = {}
                for s1 in loc_scenes:
                    for s2 in loc_scenes:
                        if s1 != s2:
                            matrix[(s1, s2)] = loc.turnaround_minutes
                scheduler.add_transition_matrix(
                    resource_id=f"loc:{loc_id}",
                    transition_matrix=matrix,
                    default_buffer=loc.turnaround_minutes,
                )

        # 5. Composite objective: minimize total shoot duration + cast idle time
        objectives = [
            MinimizeMakespanObjective(weight=1.0),
            MinimizeIdleTimeObjective(
                resource_ids=[f"cast:{cid}" for cid in self.cast],
                weight=0.3,
            ),
        ]
        scheduler.minimize(WeightedCompositeObjective(objectives))

        return scheduler
