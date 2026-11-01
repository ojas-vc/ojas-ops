"""Workforce, healthcare, and nurse shift rostering adapter."""

from __future__ import annotations

import msgspec

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.task import ResourceRequirement, TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler


class StaffMember(msgspec.Struct, kw_only=True):
    """A healthcare worker, nurse, or employee."""

    id: str
    name: str = ""
    role: str = "nurse"
    skills: list[str] = msgspec.field(default_factory=list)
    max_work_minutes: int = 40 * 60  # 40 hours standard
    min_rest_minutes: int = 12 * 60  # 12 hours minimum rest between shifts
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)


class ShiftSlot(msgspec.Struct, kw_only=True):
    """A required staffing slot during a specific shift window."""

    id: str
    name: str = ""
    department: str = "general"
    start_minute: int
    duration_minutes: int = 8 * 60  # 8 hours standard
    required_skills: list[str] = msgspec.field(default_factory=list)


class WorkforceScheduler(DomainAdapter):
    """Schedules staff into required shift slots matching qualifications, rest rules, and hours."""

    def __init__(self, *, horizon_minutes: int = 7 * 24 * 60) -> None:
        self.horizon_minutes = horizon_minutes
        self.staff: dict[str, StaffMember] = {}
        self.shifts: dict[str, ShiftSlot] = {}

    def add_staff(
        self,
        id: str,
        name: str = "",
        role: str = "nurse",
        skills: list[str] | None = None,
        max_work_minutes: int = 40 * 60,
        min_rest_minutes: int = 12 * 60,
        blackout_windows: list[IntervalWindow] | None = None,
    ) -> StaffMember:
        member = StaffMember(
            id=id,
            name=name or id,
            role=role,
            skills=skills or [],
            max_work_minutes=max_work_minutes,
            min_rest_minutes=min_rest_minutes,
            blackout_windows=blackout_windows or [],
        )
        self.staff[id] = member
        return member

    def add_shift(
        self,
        id: str,
        start_minute: int,
        duration_minutes: int = 8 * 60,
        name: str = "",
        department: str = "general",
        required_skills: list[str] | None = None,
    ) -> ShiftSlot:
        slot = ShiftSlot(
            id=id,
            name=name or id,
            department=department,
            start_minute=start_minute,
            duration_minutes=duration_minutes,
            required_skills=required_skills or [],
        )
        self.shifts[id] = slot
        return slot

    def build_scheduler(self) -> Scheduler:
        scheduler = Scheduler()
        scheduler.set_horizon(0, self.horizon_minutes)

        # 1. Add staff as resources
        for s_id, member in self.staff.items():
            scheduler.add_resource(
                id=s_id,
                name=member.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
                skills=member.skills,
                blackout_windows=member.blackout_windows,
            )
            # Enforce min rest between shifts
            scheduler.add_min_rest(s_id, member.min_rest_minutes)
            # Enforce max workload
            scheduler.add_max_workload(s_id, member.max_work_minutes)

        # 2. Add shift slots as tasks with candidate pools matching required skills
        for shift_id, shift in self.shifts.items():
            eligible_staff = [
                s_id
                for s_id, s in self.staff.items()
                if all(skill in s.skills for skill in shift.required_skills)
            ]
            if not eligible_staff:
                msg = f"No eligible staff member has required skills {shift.required_skills} for shift '{shift_id}'"
                raise ValueError(msg)

            req = ResourceRequirement(
                resource_id=eligible_staff[0],
                capacity=1,
                candidate_pool=eligible_staff,
            )
            scheduler.add_task(
                id=shift_id,
                duration=shift.duration_minutes,
                name=shift.name,
                fixed_start=shift.start_minute,
                resource_requirements=[req],
                priority=TaskPriority.HIGH,
            )

        # Minimize makespan (or composite)
        scheduler.minimize(MinimizeMakespanObjective())

        return scheduler
