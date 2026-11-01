"""Unit tests for all 6 domain adapters and industry use cases."""

from ojas_ops.adapters import (
    AcademicTimetableScheduler,
    EventRunSheetScheduler,
    FilmProductionScheduler,
    ManufacturingScheduler,
    MarketingFlightingScheduler,
    WorkforceScheduler,
)
from ojas_ops.models import ScheduleStatus


def test_film_production_adapter() -> None:
    film = FilmProductionScheduler()
    film.add_cast_member("lead_actor", name="Lead Actor", day_rate=5000.0)
    film.add_cast_member("supporting_actor", name="Supporting Actor", day_rate=2000.0)
    film.add_location("palace", name="Royal Palace", turnaround_minutes=30)
    film.add_location("forest", name="Deep Woods", turnaround_minutes=45)

    film.add_scene(
        id="scene_1",
        scene_number="1A",
        duration_minutes=90,
        character_ids=["lead_actor"],
        location_id="palace",
    )
    film.add_scene(
        id="scene_2",
        scene_number="2B",
        duration_minutes=120,
        character_ids=["lead_actor", "supporting_actor"],
        location_id="palace",
        dependencies=["scene_1"],
    )
    film.add_scene(
        id="scene_3",
        scene_number="3A",
        duration_minutes=60,
        character_ids=["supporting_actor"],
        location_id="forest",
    )

    scheduler = film.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    assert len(result.tasks) == 3
    # Scene 2 must follow Scene 1
    assert result.tasks["scene_2"].start >= result.tasks["scene_1"].end


def test_manufacturing_adapter() -> None:
    mfg = ManufacturingScheduler()
    mfg.add_machine("cnc_mill", name="CNC Milling Machine")
    mfg.add_machine("laser_cutter", name="Laser Cutter")

    # Product family changeover on cnc_mill
    mfg.set_family_setup_time("cnc_mill", "steel", "aluminum", setup_minutes=20)
    mfg.set_family_setup_time("cnc_mill", "aluminum", "steel", setup_minutes=25)

    mfg.add_job("gear_batch", name="Gears Batch", due_date=200)
    mfg.add_operation("gear_batch", "g_cut", "laser_cutter", duration_minutes=30)
    mfg.add_operation(
        "gear_batch", "g_mill", "cnc_mill", duration_minutes=45, product_family="steel"
    )

    mfg.add_job("bracket_batch", name="Brackets Batch", due_date=200)
    mfg.add_operation("bracket_batch", "b_cut", "laser_cutter", duration_minutes=25)
    mfg.add_operation(
        "bracket_batch", "b_mill", "cnc_mill", duration_minutes=40, product_family="aluminum"
    )

    scheduler = mfg.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    # g_mill must follow g_cut
    assert result.tasks["g_mill"].start >= result.tasks["g_cut"].end
    # b_mill must follow b_cut
    assert result.tasks["b_mill"].start >= result.tasks["b_cut"].end


def test_workforce_rostering_adapter() -> None:
    wf = WorkforceScheduler(horizon_minutes=24 * 60)
    wf.add_staff("nurse_alice", name="Alice", skills=["icu", "triage"], min_rest_minutes=60)
    wf.add_staff("nurse_bob", name="Bob", skills=["general", "icu"], min_rest_minutes=60)

    wf.add_shift("shift_morn", start_minute=0, duration_minutes=8 * 60, required_skills=["icu"])
    wf.add_shift("shift_eve", start_minute=8 * 60, duration_minutes=8 * 60, required_skills=["icu"])

    scheduler = wf.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    assert len(result.tasks) == 2


def test_academic_timetabling_adapter() -> None:
    acad = AcademicTimetableScheduler(horizon_minutes=8 * 60)
    acad.add_instructor("prof_turing", name="Prof Turing")
    acad.add_classroom("hall_101", name="Room 101", capacity=50, is_lab=False)
    acad.add_cohort("cs_year_1", name="CS Year 1")

    acad.add_class(
        id="cs101_lec1",
        code="CS101",
        duration_minutes=60,
        instructor_id="prof_turing",
        cohort_ids=["cs_year_1"],
    )
    acad.add_class(
        id="cs101_lec2",
        code="CS101",
        duration_minutes=60,
        instructor_id="prof_turing",
        cohort_ids=["cs_year_1"],
    )

    scheduler = acad.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    # The two lectures cannot overlap because same instructor and same cohort
    t1 = result.tasks["cs101_lec1"]
    t2 = result.tasks["cs101_lec2"]
    assert not t1.overlaps(t2)


def test_event_run_sheet_adapter() -> None:
    event = EventRunSheetScheduler(event_duration_minutes=8 * 60)
    event.add_hall("main_stage", name="Main Auditorium", turnaround_minutes=15)
    event.add_speaker("keynote_spk", name="VIP Keynote Speaker", min_prep_buffer_minutes=15)

    event.add_session(
        id="opening_keynote",
        title="Opening Keynote",
        duration_minutes=60,
        speaker_ids=["keynote_spk"],
        hall_id="main_stage",
    )
    event.add_session(
        id="product_showcase",
        title="Product Showcase",
        duration_minutes=45,
        hall_id="main_stage",
    )

    scheduler = event.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    # Turnaround buffer between opening_keynote and product_showcase must be >= 15
    tasks = sorted(
        [result.tasks["opening_keynote"], result.tasks["product_showcase"]], key=lambda t: t.start
    )
    assert tasks[1].start >= tasks[0].end + 15


def test_marketing_flighting_adapter() -> None:
    mkt = MarketingFlightingScheduler(total_campaign_days=30)
    mkt.add_channel("meta_ads", name="Meta Social", max_concurrent_flights=1)
    mkt.add_channel("google_search", name="Google Ads", max_concurrent_flights=2)

    mkt.add_flight(
        id="meta_teaser",
        channel_id="meta_ads",
        duration_days=5,
        stage="teaser",
    )
    mkt.add_flight(
        id="meta_launch",
        channel_id="meta_ads",
        duration_days=10,
        stage="launch",
        dependencies=["meta_teaser"],
    )

    scheduler = mkt.build_scheduler()
    result = scheduler.solve()
    validation = scheduler.validate(result)

    assert result.status == ScheduleStatus.OPTIMAL
    assert validation.is_valid
    assert result.tasks["meta_launch"].start >= result.tasks["meta_teaser"].end
