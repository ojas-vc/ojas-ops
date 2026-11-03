"""Request and response schemas for domain optimization adapters."""

from typing import Any

import msgspec

from ojas_ops.adapters.academic import Classroom, CourseClass, Instructor, StudentCohort
from ojas_ops.adapters.event_run_sheets import EventSession, EventSpeaker, VenueHall
from ojas_ops.adapters.manufacturing import Machine, ProductionJob
from ojas_ops.adapters.marketing_flighting import MarketingChannel, MediaFlight
from ojas_ops.adapters.workforce import ShiftSlot, StaffMember


# --- Manufacturing ---
class SetupMatrixEntry(msgspec.Struct, kw_only=True):
    machine_id: str
    from_family: str
    to_family: str
    setup_minutes: int


class ManufacturingOptimizeRequest(msgspec.Struct, kw_only=True):
    machines: list[Machine]
    jobs: list[ProductionJob]
    setup_matrix: list[SetupMatrixEntry] = msgspec.field(default_factory=list)
    max_time_seconds: float = 10.0


class ManufacturingOptimizeResponse(msgspec.Struct, kw_only=True):
    status: str
    makespan: int
    solve_time_seconds: float
    tasks: dict[str, Any]


# --- Workforce ---
class WorkforceOptimizeRequest(msgspec.Struct, kw_only=True):
    staff: list[StaffMember]
    shifts: list[ShiftSlot]
    horizon_minutes: int = 10080
    max_time_seconds: float = 10.0


class WorkforceOptimizeResponse(msgspec.Struct, kw_only=True):
    status: str
    makespan: int
    solve_time_seconds: float
    assignments: dict[str, list[str]]


# --- Marketing Flighting ---
class MarketingOptimizeRequest(msgspec.Struct, kw_only=True):
    channels: list[MarketingChannel]
    flights: list[MediaFlight]
    horizon_days: int = 30
    max_time_seconds: float = 10.0


class MarketingOptimizeResponse(msgspec.Struct, kw_only=True):
    status: str
    makespan: int
    total_spend_cents: int
    flights: dict[str, Any]
    solve_time_seconds: float


# --- Academic Timetabling ---
class AcademicOptimizeRequest(msgspec.Struct, kw_only=True):
    cohorts: list[StudentCohort]
    instructors: list[Instructor]
    classrooms: list[Classroom]
    classes: list[CourseClass]
    horizon_minutes: int = 2400
    max_time_seconds: float = 10.0


class AcademicOptimizeResponse(msgspec.Struct, kw_only=True):
    status: str
    makespan: int
    schedule: dict[str, Any]
    solve_time_seconds: float


# --- Event Run Sheets ---
class EventsOptimizeRequest(msgspec.Struct, kw_only=True):
    halls: list[VenueHall]
    speakers: list[EventSpeaker]
    sessions: list[EventSession]
    event_duration_minutes: int = 720
    max_time_seconds: float = 10.0


class EventsOptimizeResponse(msgspec.Struct, kw_only=True):
    status: str
    makespan: int
    session_assignments: dict[str, Any]
    solve_time_seconds: float
