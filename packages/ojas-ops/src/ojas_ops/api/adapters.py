"""Class-Based ViewSet for Domain Adapter optimization operations."""

import asyncio

from django_bolt import ViewSet, action

from ojas_ops.adapters.academic import AcademicTimetableScheduler
from ojas_ops.adapters.event_run_sheets import EventRunSheetScheduler
from ojas_ops.adapters.film_production import (
    FilmScheduleResult,
    ProductionDataset,
    optimize_production_schedule,
)
from ojas_ops.adapters.manufacturing import ManufacturingScheduler
from ojas_ops.adapters.marketing_flighting import MarketingFlightingScheduler
from ojas_ops.adapters.workforce import WorkforceScheduler
from ojas_ops.schemas.adapters import (
    AcademicOptimizeRequest,
    AcademicOptimizeResponse,
    EventsOptimizeRequest,
    EventsOptimizeResponse,
    ManufacturingOptimizeRequest,
    ManufacturingOptimizeResponse,
    MarketingOptimizeRequest,
    MarketingOptimizeResponse,
    WorkforceOptimizeRequest,
    WorkforceOptimizeResponse,
)
from ojas_ops.solvers.config import SolverConfig


class AdaptersViewSet(ViewSet):
    """Class-Based ViewSet managing multi-domain specialized optimization adapters."""

    @action(methods=["POST"], detail=False, path="film/optimize")
    async def optimize_film(
        self,
        request,
        payload: ProductionDataset,
    ) -> FilmScheduleResult:
        """Optimize film production shooting schedule with Day Out of Days (DOOD) cast minimization."""
        return await asyncio.to_thread(optimize_production_schedule, payload)

    @action(methods=["POST"], detail=False, path="manufacturing/optimize")
    async def optimize_manufacturing(
        self,
        request,
        payload: ManufacturingOptimizeRequest,
    ) -> ManufacturingOptimizeResponse:
        """Optimize industrial job-shop sequence with family changeover setup matrices."""

        def _solve() -> ManufacturingOptimizeResponse:
            mfg = ManufacturingScheduler()
            for m in payload.machines:
                mfg.machines[m.id] = m
            for j in payload.jobs:
                mfg.jobs[j.id] = j
            for s in payload.setup_matrix:
                mfg.set_family_setup_time(s.machine_id, s.from_family, s.to_family, s.setup_minutes)
            sched = mfg.build_scheduler()
            config = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config)
            tasks_dict = {
                t_id: {
                    "start": st.start,
                    "end": st.end,
                    "resources": st.assigned_resources,
                }
                for t_id, st in res.tasks.items()
            }
            return ManufacturingOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                solve_time_seconds=res.solve_time_seconds,
                tasks=tasks_dict,
            )

        return await asyncio.to_thread(_solve)

    @action(methods=["POST"], detail=False, path="workforce/optimize")
    async def optimize_workforce(
        self,
        request,
        payload: WorkforceOptimizeRequest,
    ) -> WorkforceOptimizeResponse:
        """Optimize staff shift rostering with qualification matching and rest requirements."""

        def _solve() -> WorkforceOptimizeResponse:
            wf = WorkforceScheduler(horizon_minutes=payload.horizon_minutes)
            for s in payload.staff:
                wf.staff[s.id] = s
            for sh in payload.shifts:
                wf.shifts[sh.id] = sh
            sched = wf.build_scheduler()
            config = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config)
            assignments: dict[str, list[str]] = {
                t_id: st.assigned_resources for t_id, st in res.tasks.items()
            }
            return WorkforceOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                solve_time_seconds=res.solve_time_seconds,
                assignments=assignments,
            )

        return await asyncio.to_thread(_solve)

    @action(methods=["POST"], detail=False, path="marketing/optimize")
    async def optimize_marketing(
        self,
        request,
        payload: MarketingOptimizeRequest,
    ) -> MarketingOptimizeResponse:
        """Optimize multi-channel marketing campaign cadence and budget flighting."""

        def _solve() -> MarketingOptimizeResponse:
            mktg = MarketingFlightingScheduler(total_campaign_days=payload.horizon_days)
            for c in payload.channels:
                mktg.channels[c.id] = c
            for f in payload.flights:
                mktg.flights[f.id] = f
            sched = mktg.build_scheduler()
            config = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config)
            flights_dict = {
                t_id: {
                    "start_minute": st.start,
                    "end_minute": st.end,
                    "channel": st.assigned_resources[0] if st.assigned_resources else None,
                }
                for t_id, st in res.tasks.items()
            }
            total_spend = sum(f.budget_cents for f in payload.flights)
            return MarketingOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                total_spend_cents=total_spend,
                flights=flights_dict,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)

    @action(methods=["POST"], detail=False, path="academic/optimize")
    async def optimize_academic(
        self,
        request,
        payload: AcademicOptimizeRequest,
    ) -> AcademicOptimizeResponse:
        """Optimize conflict-free academic timetables for classrooms, faculty, and student cohorts."""

        def _solve() -> AcademicOptimizeResponse:
            acad = AcademicTimetableScheduler(horizon_minutes=payload.horizon_minutes)
            for c in payload.cohorts:
                acad.cohorts[c.id] = c
            for inst in payload.instructors:
                acad.instructors[inst.id] = inst
            for r in payload.classrooms:
                acad.classrooms[r.id] = r
            for cls in payload.classes:
                acad.classes[cls.id] = cls
            sched = acad.build_scheduler()
            config = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config)
            sched_dict = {
                t_id: {
                    "start": st.start,
                    "end": st.end,
                    "assigned_resources": st.assigned_resources,
                }
                for t_id, st in res.tasks.items()
            }
            return AcademicOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                schedule=sched_dict,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)

    @action(methods=["POST"], detail=False, path="events/optimize")
    async def optimize_events(
        self,
        request,
        payload: EventsOptimizeRequest,
    ) -> EventsOptimizeResponse:
        """Optimize multi-track event agendas and conference run sheets with hall turnaround buffers."""

        def _solve() -> EventsOptimizeResponse:
            events = EventRunSheetScheduler(event_duration_minutes=payload.event_duration_minutes)
            for h in payload.halls:
                events.halls[h.id] = h
            for sp in payload.speakers:
                events.speakers[sp.id] = sp
            for s in payload.sessions:
                events.sessions[s.id] = s
            sched = events.build_scheduler()
            config = SolverConfig(time_limit_seconds=payload.max_time_seconds)
            res = sched.solve(config)
            assignments = {
                t_id: {
                    "start": st.start,
                    "end": st.end,
                    "hall_and_speakers": st.assigned_resources,
                }
                for t_id, st in res.tasks.items()
            }
            return EventsOptimizeResponse(
                status=res.status.value,
                makespan=res.makespan,
                session_assignments=assignments,
                solve_time_seconds=res.solve_time_seconds,
            )

        return await asyncio.to_thread(_solve)
