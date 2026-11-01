"""Academic course and classroom timetabling adapter."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import ResourceRequirement, TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler


class CourseClass(msgspec.Struct, kw_only=True):
    """A lecture, seminar, or laboratory session requiring instructor, room, and student group."""

    id: str
    code: str
    name: str = ""
    duration_minutes: int = 60
    instructor_id: str
    cohort_ids: list[str] = msgspec.field(default_factory=list)
    is_lab: bool = False


class Instructor(msgspec.Struct, kw_only=True):
    """Faculty member or teacher."""

    id: str
    name: str = ""
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class Classroom(msgspec.Struct, kw_only=True):
    """Physical lecture hall or laboratory."""

    id: str
    name: str = ""
    capacity: int = 40
    is_lab: bool = False


class StudentCohort(msgspec.Struct, kw_only=True):
    """Batch, class, or group of students enrolled in common courses."""

    id: str
    name: str = ""


class AcademicTimetableScheduler(DomainAdapter):
    """Schedules conflict-free academic timetables for instructors, classrooms, and student cohorts."""

    def __init__(self, *, horizon_minutes: int = 5 * 8 * 60) -> None:  # 5 days, 8h/day
        self.horizon_minutes = horizon_minutes
        self.instructors: dict[str, Instructor] = {}
        self.classrooms: dict[str, Classroom] = {}
        self.cohorts: dict[str, StudentCohort] = {}
        self.classes: dict[str, CourseClass] = {}

    def add_instructor(
        self,
        id: str,
        name: str = "",
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> Instructor:
        inst = Instructor(id=id, name=name or id, blackout_windows=blackout_windows or [])
        self.instructors[id] = inst
        return inst

    def add_classroom(
        self,
        id: str,
        name: str = "",
        capacity: int = 40,
        is_lab: bool = False,
    ) -> Classroom:
        room = Classroom(id=id, name=name or id, capacity=capacity, is_lab=is_lab)
        self.classrooms[id] = room
        return room

    def add_cohort(self, id: str, name: str = "") -> StudentCohort:
        cohort = StudentCohort(id=id, name=name or id)
        self.cohorts[id] = cohort
        return cohort

    def add_class(
        self,
        id: str,
        code: str,
        duration_minutes: int = 60,
        name: str = "",
        instructor_id: str = "",
        cohort_ids: list[str] | None = None,
        is_lab: bool = False,
    ) -> CourseClass:
        cc = CourseClass(
            id=id,
            code=code,
            name=name or code,
            duration_minutes=duration_minutes,
            instructor_id=instructor_id,
            cohort_ids=cohort_ids or [],
            is_lab=is_lab,
        )
        self.classes[id] = cc
        return cc

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()
        scheduler.set_horizon(0, self.horizon_minutes)

        # 1. Add instructors as resources (capacity=1)
        for inst_id, inst in self.instructors.items():
            scheduler.add_resource(
                id=f"inst:{inst_id}",
                name=inst.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
                blackout_windows=inst.blackout_windows,
            )

        # 2. Add classrooms as resources (capacity=1)
        for room_id, room in self.classrooms.items():
            scheduler.add_resource(
                id=f"room:{room_id}",
                name=room.name,
                capacity=1,
                resource_type=ResourceType.LOCATION,
            )

        # 3. Add student cohorts as resources (capacity=1 to guarantee conflict-free schedules)
        for cohort_id, cohort in self.cohorts.items():
            scheduler.add_resource(
                id=f"cohort:{cohort_id}",
                name=cohort.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
            )

        # 4. Add course classes as tasks
        for c_id, cc in self.classes.items():
            req_resources = [f"inst:{cc.instructor_id}"]
            for ch_id in cc.cohort_ids:
                req_resources.append(f"cohort:{ch_id}")

            # Assign matching room from candidate pool
            eligible_rooms = [
                f"room:{r_id}" for r_id, r in self.classrooms.items() if r.is_lab == cc.is_lab
            ]
            if not eligible_rooms:
                msg = f"No eligible classroom for class '{c_id}' (is_lab={cc.is_lab})"
                raise ValueError(msg)

            req_list = [ResourceRequirement(resource_id=rid, capacity=1) for rid in req_resources]
            req_list.append(
                ResourceRequirement(
                    resource_id=eligible_rooms[0],
                    capacity=1,
                    candidate_pool=eligible_rooms,
                )
            )

            scheduler.add_task(
                id=c_id,
                duration=cc.duration_minutes,
                name=f"{cc.code} - {cc.name}",
                resource_requirements=req_list,
                priority=TaskPriority.NORMAL,
            )

        # 5. Minimize timetable span and gaps
        objectives = [
            MinimizeMakespanObjective(weight=1.0),
            MinimizeIdleTimeObjective(
                resource_ids=[f"cohort:{ch}" for ch in self.cohorts],
                weight=0.5,
            ),
        ]
        scheduler.minimize(WeightedCompositeObjective(objectives))

        return scheduler
