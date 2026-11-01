"""Multi-track conference, wedding occasion, and event run-sheet scheduling adapter."""

from __future__ import annotations

import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import ResourceRequirement, TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler


class EventSession(msgspec.Struct, kw_only=True):
    """A conference keynote, panel, workshop, or occasion ceremony milestone."""

    id: str
    title: str
    track: str = "main"
    duration_minutes: int = 45
    speaker_ids: list[str] = msgspec.field(default_factory=list)
    hall_id: str | None = None
    fixed_start: int | None = None
    priority: TaskPriority = TaskPriority.NORMAL


class VenueHall(msgspec.Struct, kw_only=True):
    """An auditorium, stage, banquet space, or breakout room."""

    id: str
    name: str = ""
    capacity: int = 200
    turnaround_minutes: int = 15
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class EventSpeaker(msgspec.Struct, kw_only=True):
    """A keynote speaker, panelist, VIP, or officiant."""

    id: str
    name: str = ""
    min_prep_buffer_minutes: int = 15
    availability_windows: list[IntervalWindow] = msgspec.field(default_factory=list)
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class EventRunSheetScheduler(DomainAdapter):
    """Generates tight, conflict-free multi-track agendas and occasion run-sheets with venue turnaround buffers."""

    def __init__(self, *, event_duration_minutes: int = 12 * 60) -> None:
        self.event_duration_minutes = event_duration_minutes
        self.halls: dict[str, VenueHall] = {}
        self.speakers: dict[str, EventSpeaker] = {}
        self.sessions: dict[str, EventSession] = {}

    def add_hall(
        self,
        id: str,
        name: str = "",
        capacity: int = 200,
        turnaround_minutes: int = 15,
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> VenueHall:
        hall = VenueHall(
            id=id,
            name=name or id,
            capacity=capacity,
            turnaround_minutes=turnaround_minutes,
            blackout_windows=blackout_windows or [],
        )
        self.halls[id] = hall
        return hall

    def add_speaker(
        self,
        id: str,
        name: str = "",
        min_prep_buffer_minutes: int = 15,
        availability_windows: list[IntervalWindow] | None = None,
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> EventSpeaker:
        spk = EventSpeaker(
            id=id,
            name=name or id,
            min_prep_buffer_minutes=min_prep_buffer_minutes,
            availability_windows=availability_windows or [],
            blackout_windows=blackout_windows or [],
        )
        self.speakers[id] = spk
        return spk

    def add_session(
        self,
        id: str,
        title: str,
        duration_minutes: int = 45,
        track: str = "main",
        speaker_ids: list[str] | None = None,
        hall_id: str | None = None,
        fixed_start: int | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> EventSession:
        session = EventSession(
            id=id,
            title=title,
            track=track,
            duration_minutes=duration_minutes,
            speaker_ids=speaker_ids or [],
            hall_id=hall_id,
            fixed_start=fixed_start,
            priority=priority,
        )
        self.sessions[id] = session
        return session

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()
        scheduler.set_horizon(0, self.event_duration_minutes)

        # 1. Add halls as resources
        for h_id, hall in self.halls.items():
            scheduler.add_resource(
                id=f"hall:{h_id}",
                name=hall.name,
                capacity=1,
                resource_type=ResourceType.FACILITY,
                blackout_windows=hall.blackout_windows,
            )

        # 2. Add speakers as resources with prep buffer rest constraints
        for spk_id, spk in self.speakers.items():
            scheduler.add_resource(
                id=f"spk:{spk_id}",
                name=spk.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
                blackout_windows=spk.blackout_windows,
            )
            if spk.min_prep_buffer_minutes > 0:
                scheduler.add_min_rest(f"spk:{spk_id}", spk.min_prep_buffer_minutes)

        # 3. Add sessions as tasks
        for s_id, s in self.sessions.items():
            req_resources = []
            for spk_id in s.speaker_ids:
                if spk_id in self.speakers:
                    req_resources.append(f"spk:{spk_id}")

            req_list = [ResourceRequirement(resource_id=rid, capacity=1) for rid in req_resources]

            # Hall assignment: explicit or from eligible halls
            if s.hall_id:
                req_list.append(ResourceRequirement(resource_id=f"hall:{s.hall_id}", capacity=1))
            else:
                candidate_halls = [f"hall:{h_id}" for h_id in self.halls]
                if candidate_halls:
                    req_list.append(
                        ResourceRequirement(
                            resource_id=candidate_halls[0],
                            capacity=1,
                            candidate_pool=candidate_halls,
                        )
                    )

            scheduler.add_task(
                id=s_id,
                duration=s.duration_minutes,
                name=s.title,
                resource_requirements=req_list,
                fixed_start=s.fixed_start,
                priority=s.priority,
            )

        # 4. Add hall turnaround buffers
        for h_id, hall in self.halls.items():
            relevant_sessions = [
                s_id for s_id, s in self.sessions.items() if s.hall_id == h_id or s.hall_id is None
            ]
            if len(relevant_sessions) > 1 and hall.turnaround_minutes > 0:
                trans_matrix: dict[tuple[str, str], int] = {}
                for s1 in relevant_sessions:
                    for s2 in relevant_sessions:
                        if s1 != s2:
                            trans_matrix[(s1, s2)] = hall.turnaround_minutes
                scheduler.add_transition_matrix(
                    resource_id=f"hall:{h_id}",
                    transition_matrix=trans_matrix,
                    default_buffer=hall.turnaround_minutes,
                )

        # 5. Minimize makespan and speaker idle time
        objectives = [
            MinimizeMakespanObjective(weight=1.0),
            MinimizeIdleTimeObjective(
                resource_ids=[f"hall:{h_id}" for h_id in self.halls],
                weight=0.2,
            ),
        ]
        scheduler.minimize(WeightedCompositeObjective(objectives))

        return scheduler
