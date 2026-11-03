"""Comprehensive tests for extended film production scheduling framework."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

import msgspec
from ojas_ops.adapters.film_production import (
    CalendarDay,
    DOODStatusCode,
    FilmProductionScheduler,
    Location,
    ProductionDataset,
    ProductionUnitType,
    Scene,
    Talent,
    TimeOfDay,
    WeatherType,
    optimize_production_schedule,
)
from ojas_ops.models import ScheduleStatus

SAMPLE_DATASET_JSON = """
{
    "project_title": "The Chronicles of Eternity (Parts 1 & 2)",
    "talents": [
        {"id": 1, "name": "Marcus Vance", "character_name": "Commander Reyes", "daily_rate": 8000.0, "is_minor": false, "max_daily_hours": 12.0, "hmu_duration_minutes": 60, "wardrobe_duration_minutes": 30, "travel_duration_minutes": 45, "blackout_days": []},
        {"id": 2, "name": "Elena Rostova", "character_name": "Dr. Aris", "daily_rate": 5500.0, "is_minor": false, "max_daily_hours": 12.0, "hmu_duration_minutes": 45, "wardrobe_duration_minutes": 20, "travel_duration_minutes": 30, "blackout_days": []},
        {"id": 3, "name": "Leo Sterling", "character_name": "Young Toby", "daily_rate": 2000.0, "is_minor": true, "max_daily_hours": 5.0, "hmu_duration_minutes": 30, "wardrobe_duration_minutes": 15, "travel_duration_minutes": 30, "blackout_days": []}
    ],
    "locations": [
        {"id": 1, "name": "Soundstage 4 (Palace)", "location_type": "SOUNDSTAGE", "permitted_days": [1, 2, 3, 4, 5], "noise_curfew_hour": null, "allows_sync_sound": true, "daily_rental_cost": 2500.0, "prep_days_required": 1, "strike_days_required": 1},
        {"id": 2, "name": "Dune Practical Ridge", "location_type": "PRACTICAL_EXT", "permitted_days": [1, 2, 5], "noise_curfew_hour": 22, "allows_sync_sound": false, "daily_rental_cost": 1200.0, "prep_days_required": 0, "strike_days_required": 0},
        {"id": 3, "name": "Municipal Bank Vault", "location_type": "PRACTICAL_INT", "permitted_days": [5], "noise_curfew_hour": 20, "allows_sync_sound": true, "daily_rental_cost": 3000.0, "prep_days_required": 1, "strike_days_required": 1}
    ],
    "props": [
        {"id": 1, "name": "Laser Map", "category": "HERO", "total_quantity": 2, "is_destructible": false, "requires_armorer": false, "reset_duration_minutes": 0},
        {"id": 2, "name": "Stunt Glass Bottle", "category": "BREAKAWAY", "total_quantity": 4, "is_destructible": true, "requires_armorer": false, "reset_duration_minutes": 15},
        {"id": 3, "name": "Plasma Blaster", "category": "WEAPON", "total_quantity": 3, "is_destructible": false, "requires_armorer": true, "reset_duration_minutes": 0}
    ],
    "costumes": [
        {"id": 1, "character_id": 1, "costume_code": "REYES_PRISTINE", "distress_stage": 1, "available_duplicates": 2, "requires_specialist_dresser": false},
        {"id": 2, "character_id": 1, "costume_code": "REYES_DAMAGED",  "distress_stage": 3, "available_duplicates": 1, "requires_specialist_dresser": true}
    ],
    "equipment": [
        {"id": 1, "name": "50ft Technocrane", "equipment_type": "TECHNOCRANE", "daily_rental_cost": 3500.0, "rental_start_day": 1, "rental_end_day": 3, "requires_certified_technician": true}
    ],
    "stunts": [
        {"id": 1, "has_wirework": true, "has_pyrotechnics": false, "has_squibs": true, "pre_rigging_hours_required": 4.0, "mandatory_medic_count": 1}
    ],
    "calendar": [
        {"day_number": 1, "calendar_date": "2026-11-03", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:12", "sunset_time": "18:22", "is_weekend": false},
        {"day_number": 2, "calendar_date": "2026-11-04", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:13", "sunset_time": "18:21", "is_weekend": false},
        {"day_number": 3, "calendar_date": "2026-11-05", "is_statutory_holiday": false, "is_inauspicious": true,  "expected_weather": "CLEAR", "sunrise_time": "06:14", "sunset_time": "18:20", "is_weekend": false},
        {"day_number": 4, "calendar_date": "2026-11-06", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "RAIN",  "sunrise_time": "06:15", "sunset_time": "18:19", "is_weekend": false},
        {"day_number": 5, "calendar_date": "2026-11-07", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:16", "sunset_time": "18:18", "is_weekend": true}
    ],
    "scenes": [
        {"id": 1, "scene_number": "10A", "part": 1, "location_id": 1, "setting": "INT", "time_of_day": "DAY", "page_eighths": 14, "duration_hours": 3.5, "required_cast": [1, 3], "required_prop_ids": [1], "required_costume_ids": [1], "required_equipment_ids": [1], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
        {"id": 2, "scene_number": "10B", "part": 2, "location_id": 1, "setting": "INT", "time_of_day": "DAY", "page_eighths": 10, "duration_hours": 2.5, "required_cast": [1], "required_prop_ids": [1], "required_costume_ids": [1], "required_equipment_ids": [1], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
        {"id": 3, "scene_number": "22",  "part": 1, "location_id": 2, "setting": "EXT", "time_of_day": "DAY", "page_eighths": 22, "duration_hours": 4.0, "required_cast": [1, 2], "required_prop_ids": [3], "required_costume_ids": [1], "required_equipment_ids": [], "stunt_sfx_package_id": null, "weather_requirement": "NO_RAIN", "sound_recording": "MOS", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
        {"id": 4, "scene_number": "45",  "part": 2, "location_id": 1, "setting": "INT", "time_of_day": "NIGHT", "page_eighths": 18, "duration_hours": 4.5, "required_cast": [1, 2], "required_prop_ids": [2], "required_costume_ids": [2], "required_equipment_ids": [], "stunt_sfx_package_id": 1, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
        {"id": 5, "scene_number": "80",  "part": 1, "location_id": 3, "setting": "INT", "time_of_day": "DAY", "page_eighths": 16, "duration_hours": 3.5, "required_cast": [2], "required_prop_ids": [], "required_costume_ids": [], "required_equipment_ids": [], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 5, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null}
    ],
    "max_shooting_days": 5,
    "max_hours_per_day": 10.0
}
"""


def test_production_dataset_json_decoding_and_solving() -> None:
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)

    assert dataset.project_title == "The Chronicles of Eternity (Parts 1 & 2)"
    assert len(dataset.talents) == 3
    assert len(dataset.locations) == 3
    assert len(dataset.props) == 3
    assert len(dataset.costumes) == 2
    assert len(dataset.equipment) == 1
    assert len(dataset.scenes) == 5
    assert len(dataset.calendar) == 5

    # Run discrete optimization
    result = optimize_production_schedule(dataset)

    assert result.status == ScheduleStatus.OPTIMAL
    assert result.is_feasible
    assert result.solve_time_seconds > 0.0
    assert result.objective_cost > 0.0

    # Master Stripboard assertions
    stripboard = result.stripboard
    assert stripboard.project_title == dataset.project_title
    assert stripboard.total_shoot_days == 4  # Day 3 is inauspicious, so 4 shooting days
    assert len(stripboard.days) == 5

    # Day 3 must be rest day because of is_inauspicious
    day_3 = next(d for d in stripboard.days if d.day_number == 3)
    assert day_3.is_rest_day
    assert len(day_3.strips) == 0

    # All 5 non-cover scenes must be scheduled
    scheduled_scene_ids = {s.scene_id for day in stripboard.days for s in day.strips}
    assert scheduled_scene_ids == {1, 2, 3, 4, 5}

    # DOOD report assertions
    assert len(result.dood_reports) == 3
    reyes_dood = next(r for r in result.dood_reports if r.talent_id == 1)
    aris_dood = next(r for r in result.dood_reports if r.talent_id == 2)
    toby_dood = next(r for r in result.dood_reports if r.talent_id == 3)

    assert reyes_dood.total_paid_days == 4
    assert aris_dood.total_paid_days == 4
    assert toby_dood.total_paid_days == 1
    assert toby_dood.daily_codes[1] == DOODStatusCode.START_WORK_FINISH

    # Call Sheet assertions
    assert 1 in result.call_sheets
    call_sheet_d1 = result.call_sheets[1]
    assert call_sheet_d1.day_number == 1
    assert call_sheet_d1.general_crew_call == "07:00 AM"
    assert call_sheet_d1.shooting_call == "08:00 AM"
    assert call_sheet_d1.first_meal_due == "01:00 PM"
    assert len(call_sheet_d1.character_calls) >= 2


def test_costume_distress_linear_progression() -> None:
    """Ensure earlier distress stages are scheduled on or before later distress stages."""
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)

    # Costume 1 is Pristine (stage 1) used in scenes 1, 2, 3
    # Costume 2 is Damaged (stage 3) used in scene 4
    result = optimize_production_schedule(dataset)
    assert result.is_feasible

    day_s1 = result.scene_day_assignments["1"]
    day_s2 = result.scene_day_assignments["2"]
    day_s3 = result.scene_day_assignments["3"]
    day_s4 = result.scene_day_assignments["4"]

    assert day_s1 <= day_s4
    assert day_s2 <= day_s4
    assert day_s3 <= day_s4


def test_breakaway_prop_daily_exhaustion_limit() -> None:
    """Ensure scenes using breakaway props respect total daily quantity."""
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)

    # Prop 2 is Stunt Glass Bottle with quantity = 4
    # Scene 4 uses Prop 2
    result = optimize_production_schedule(dataset)
    assert result.is_feasible

    # Verify no day has more breakaway props consumed than available
    for day in result.stripboard.days:
        breakaway_scenes = [
            strip for strip in day.strips if "Stunt Glass Bottle" in strip.prop_names
        ]
        assert len(breakaway_scenes) <= 4


def test_location_company_move_limits() -> None:
    """Ensure at most 2 distinct locations are accessed per shoot day."""
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)
    result = optimize_production_schedule(dataset)

    assert result.is_feasible
    for day in result.stripboard.days:
        assert len(day.location_names) <= 2


def test_minor_child_labor_cap() -> None:
    """Ensure that on any day a minor talent works, total daily hours do not exceed minor max."""
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)
    # Young Toby (id: 3) has max_daily_hours = 5.0 and is in scene 1 (duration = 3.5 hrs)
    result = optimize_production_schedule(dataset)
    assert result.is_feasible

    toby_dood = next(r for r in result.dood_reports if r.talent_id == 3)
    toby_work_days = [
        d for d, code in toby_dood.daily_codes.items() if code in ("SW", "W", "WF", "SWF")
    ]

    for d in toby_work_days:
        day_info = next(day for day in result.stripboard.days if day.day_number == d)
        assert day_info.total_hours <= 5.0


def test_weather_and_sync_sound_compatibility() -> None:
    """Ensure exterior scenes avoid rain and sync sound avoids noisy rain locations."""
    dataset = msgspec.json.decode(SAMPLE_DATASET_JSON.encode("utf-8"), type=ProductionDataset)
    # Day 4 has expected_weather = "RAIN"
    # Location 2 (Dune Practical Ridge) allows_sync_sound = False
    # Scene 3 (scene 22) is EXT DAY and NO_RAIN
    result = optimize_production_schedule(dataset)
    assert result.is_feasible

    day_s3 = result.scene_day_assignments["3"]
    # Scene 3 cannot shoot on Day 4 (rain) or Day 3 (inauspicious)
    assert day_s3 != 4
    assert day_s3 != 3


def test_adapter_fluent_api_and_rescheduling() -> None:
    """Test FilmProductionScheduler fluent API, from_dataset, and reschedule_production."""
    scheduler = FilmProductionScheduler(
        project_title="Action Feature",
        shoot_day_hours=10,
        max_shooting_days=3,
    )
    scheduler.add_cast_member(1, name="Hero", daily_rate=5000.0)
    scheduler.add_cast_member(2, name="Sidekick", daily_rate=2500.0)
    scheduler.add_location(1, name="Studio 1", permitted_days=[1, 2, 3])
    scheduler.add_calendar_day(1, "2026-11-10", expected_weather="CLEAR")
    scheduler.add_calendar_day(2, "2026-11-11", expected_weather="CLEAR")
    scheduler.add_calendar_day(3, "2026-11-12", expected_weather="CLEAR")

    scheduler.add_scene(
        id=1,
        scene_number="1",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
    )
    scheduler.add_scene(
        id=2,
        scene_number="2",
        duration_hours=5.0,
        required_cast=[1, 2],
        location_id=1,
        dependencies=["1"],
    )

    res = scheduler.optimize()
    assert res.is_feasible
    assert res.scene_day_assignments["1"] < res.scene_day_assignments["2"]

    # Reschedule with weather disruption on day 2
    rescheduled = scheduler.reschedule(
        weather_disruptions={2: WeatherType.RAIN},
        completed_days=[1],
    )
    assert rescheduled.is_feasible


def test_sag_aftra_drop_and_pickup_10_day_rule() -> None:
    """Test SAG-AFTRA 10-day hiatus drop-and-pickup logic and DOOD notation."""
    scheduler = FilmProductionScheduler(
        project_title="Epic 14-Day Production",
        shoot_day_hours=10,
        max_shooting_days=14,
    )
    scheduler.add_cast_member(1, name="Movie Star", daily_rate=10000.0)
    scheduler.add_location(1, name="Studio Main", permitted_days=list(range(1, 15)))

    for d in range(1, 15):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    # Scene 1 locked to Day 1, Scene 2 locked to Day 14
    scheduler.add_scene(
        id=1,
        scene_number="1",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
    )
    scheduler.add_scene(
        id=2,
        scene_number="2",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
    )

    # 1. With enable_drop_pickup=False (standard continuous hold span)
    res_no_drop = scheduler.optimize(
        fixed_assignments={1: 1, 2: 14},
        enable_drop_pickup=False,
    )
    assert res_no_drop.is_feasible
    dood_no_drop = res_no_drop.dood_reports[0]
    # Without drop, Star is held for 12 intervening days: paid for all 14 days
    assert dood_no_drop.total_paid_days == 14
    assert dood_no_drop.total_cost == 140000.0
    assert dood_no_drop.daily_codes[1] == DOODStatusCode.START_WORK
    assert dood_no_drop.daily_codes[7] == DOODStatusCode.HOLD
    assert dood_no_drop.daily_codes[14] == DOODStatusCode.WORK_FINISH

    # 2. With enable_drop_pickup=True (SAG-AFTRA 10-day hiatus applied)
    res_drop = scheduler.optimize(
        fixed_assignments={1: 1, 2: 14},
        enable_drop_pickup=True,
    )
    assert res_drop.is_feasible
    dood_drop = res_drop.dood_reports[0]
    # Dropped between Day 1 and Day 14 (12 intervening days >= 10 hiatus limit)
    # Paid days = 2 (Day 1 + Day 14), savings = 120,000!
    assert dood_drop.total_work_days == 2
    assert dood_drop.total_hold_days == 0
    assert dood_drop.total_paid_days == 2
    assert dood_drop.total_cost == 20000.0
    assert dood_drop.daily_codes[1] == DOODStatusCode.START_WORK
    assert dood_drop.daily_codes[2] == DOODStatusCode.DROP
    assert dood_drop.daily_codes[7] == DOODStatusCode.DROP
    assert dood_drop.daily_codes[13] == DOODStatusCode.DROP
    assert dood_drop.daily_codes[14] == DOODStatusCode.WORK_FINISH


def test_precedence_min_lag_grooming_continuity() -> None:
    """Test min_lag_days enforcement for grooming continuity (e.g. beard shaved)."""
    scheduler = FilmProductionScheduler(
        project_title="Grooming Continuity Test",
        shoot_day_hours=10,
        max_shooting_days=5,
    )
    scheduler.add_cast_member(1, name="Character", daily_rate=2000.0)
    scheduler.add_location(1, name="Stage 1", permitted_days=[1, 2, 3, 4, 5])
    for d in range(1, 6):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    # Scene 1 (full beard) must precede Scene 2 (clean shaven) by at least 2 days
    scheduler.add_scene(
        id=1,
        scene_number="10",
        duration_hours=3.0,
        required_cast=[1],
        location_id=1,
        requires_precedence_over=2,
        min_lag_days=2,
    )
    scheduler.add_scene(
        id=2,
        scene_number="11",
        duration_hours=3.0,
        required_cast=[1],
        location_id=1,
    )

    res = scheduler.optimize()
    assert res.is_feasible
    day_s1 = res.scene_day_assignments["1"]
    day_s2 = res.scene_day_assignments["2"]
    # min_lag_days=2 requires day_s2 >= day_s1 + 2
    assert day_s2 >= day_s1 + 2


def test_call_sheet_second_meal_calculation() -> None:
    """Test second meal calculation on daily call sheet for long shoot days."""
    dataset = ProductionDataset(
        project_title="Long Day Production",
        talents=[Talent(id=1, name="Actor", character_name="Lead", daily_rate=1000.0)],
        locations=[Location(id=1, name="Studio")],
        calendar=[CalendarDay(day_number=1, calendar_date="2026-11-01")],
        scenes=[
            Scene(
                id=1,
                scene_number="1",
                duration_hours=7.0,
                required_cast=[1],
                location_id=1,
            )
        ],
        max_shooting_days=1,
        max_hours_per_day=12.0,
    )

    res = optimize_production_schedule(dataset)
    assert res.is_feasible
    call_sheet = res.call_sheets[1]
    assert call_sheet.first_meal_due == "01:00 PM"
    assert call_sheet.second_meal_due == "07:00 PM"


def test_soundstage_continuous_lease_holding() -> None:
    """Test soundstage lease holding cost minimization across prep, shoot, and strike."""
    scheduler = FilmProductionScheduler(
        project_title="Stage Lease Test",
        shoot_day_hours=10,
        max_shooting_days=5,
    )
    scheduler.add_cast_member(1, name="Lead", daily_rate=1000.0)
    scheduler.add_location(
        1,
        name="Soundstage A",
        location_type="SOUNDSTAGE",
        daily_rental_cost=5000.0,
        prep_days_required=1,
        strike_days_required=1,
        permitted_days=[1, 2, 3, 4, 5],
    )
    for d in range(1, 6):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    scheduler.add_scene(
        id=1, scene_number="1", duration_hours=3.0, required_cast=[1], location_id=1
    )
    scheduler.add_scene(
        id=2, scene_number="2", duration_hours=3.0, required_cast=[1], location_id=1
    )

    res = scheduler.optimize(enable_soundstage_lease_tracking=True)
    assert res.is_feasible
    # With lease tracking, both scenes should be clustered on adjacent days or same day
    d1 = res.scene_day_assignments["1"]
    d2 = res.scene_day_assignments["2"]
    assert abs(d2 - d1) <= 1


def test_soundstage_facility_disjunction() -> None:
    """Ensure two distinct set builds sharing the same physical stage do not overlap."""
    scheduler = FilmProductionScheduler(
        project_title="Stage Disjunction Test",
        shoot_day_hours=10,
        max_shooting_days=8,
    )
    scheduler.add_cast_member(1, name="Actor", daily_rate=1000.0)

    # Set 1 on Stage 4
    loc1 = scheduler.add_location(
        1,
        name="Stage 4 (Palace)",
        daily_rental_cost=2000.0,
        prep_days_required=1,
        strike_days_required=1,
        permitted_days=list(range(1, 9)),
    )
    loc1.soundstage_facility_id = "FACILITY_STAGE_4"

    # Set 2 on Stage 4 (must be built after Set 1 is struck, or before Set 1 preps)
    loc2 = scheduler.add_location(
        2,
        name="Stage 4 (Dungeon)",
        daily_rental_cost=2000.0,
        prep_days_required=1,
        strike_days_required=1,
        permitted_days=list(range(1, 9)),
    )
    loc2.soundstage_facility_id = "FACILITY_STAGE_4"

    for d in range(1, 9):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    scheduler.add_scene(
        id=1, scene_number="1", duration_hours=4.0, required_cast=[1], location_id=1
    )
    scheduler.add_scene(
        id=2, scene_number="2", duration_hours=4.0, required_cast=[1], location_id=2
    )

    res = scheduler.optimize(enable_soundstage_lease_tracking=True)
    assert res.is_feasible
    d1 = res.scene_day_assignments["1"]
    d2 = res.scene_day_assignments["2"]

    # If Set 1 shoots on d1, its lease is [d1-1, d1+1]
    # If Set 2 shoots on d2, its lease is [d2-1, d2+1]
    # Disjunction requires (d1 + 1 < d2 - 1) or (d2 + 1 < d1 - 1) => |d1 - d2| >= 3
    assert abs(d1 - d2) >= 3


def test_multi_unit_concurrency_and_cast_exclusivity() -> None:
    """Ensure lead talent is not scheduled on multiple camera units on the same shoot day."""
    scheduler = FilmProductionScheduler(
        project_title="Multi-Unit Production",
        shoot_day_hours=10,
        max_shooting_days=3,
    )
    scheduler.add_cast_member(1, name="Star", daily_rate=5000.0)
    scheduler.add_unit(1, name="Main Unit", unit_type=ProductionUnitType.MAIN)
    scheduler.add_unit(2, name="Second Unit", unit_type=ProductionUnitType.SECOND)

    scheduler.add_location(1, name="Stage Main", permitted_days=[1, 2, 3])
    scheduler.add_location(2, name="Ext Desert", permitted_days=[1, 2, 3])

    for d in range(1, 4):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    # Scene 1 is Main Unit with Star
    scheduler.add_scene(
        id=1,
        scene_number="10",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
        unit_type=ProductionUnitType.MAIN,
    )
    # Scene 2 is Second Unit with Star (cannot shoot on same day as Scene 1)
    scheduler.add_scene(
        id=2,
        scene_number="11_STUNT",
        duration_hours=4.0,
        required_cast=[1],
        location_id=2,
        unit_type=ProductionUnitType.SECOND,
    )

    res = scheduler.optimize()
    assert res.is_feasible
    d1 = res.scene_day_assignments["1"]
    d2 = res.scene_day_assignments["2"]
    assert d1 != d2


def test_vfx_early_turnover_deadline() -> None:
    """Ensure scenes with VFX vendor turnover deadlines are scheduled on or before deadline."""
    scheduler = FilmProductionScheduler(
        project_title="VFX Tentpole",
        shoot_day_hours=10,
        max_shooting_days=5,
    )
    scheduler.add_cast_member(1, name="Actor", daily_rate=1000.0)
    scheduler.add_location(1, name="Stage Green", permitted_days=list(range(1, 6)))

    for d in range(1, 6):
        scheduler.add_calendar_day(d, f"2026-11-{d:02d}", expected_weather="CLEAR")

    # Scene 1 is VFX heavy and must turnover by Day 2
    scheduler.add_scene(
        id=1,
        scene_number="VFX_01",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
        vfx_turnover_deadline_day=2,
        is_vfx_heavy=True,
    )
    scheduler.add_scene(
        id=2,
        scene_number="NORM_01",
        duration_hours=4.0,
        required_cast=[1],
        location_id=1,
    )

    res = scheduler.optimize()
    assert res.is_feasible
    assert res.scene_day_assignments["1"] <= 2


def test_intraday_micro_optimization_and_golden_hour() -> None:
    """Ensure micro intra-day scheduling places magic hour scenes within solar dawn/dusk windows."""
    cal = CalendarDay(
        day_number=1,
        calendar_date="2026-11-01",
        sunrise_time="06:30",
        sunset_time="18:00",
    )
    loc = Location(id=1, name="Hilltop Practical")
    t = Talent(id=1, name="Hero")

    scenes = [
        Scene(
            id=1,
            scene_number="101",
            duration_minutes=45,
            time_of_day=TimeOfDay.MAGIC_HOUR,
            location_id=1,
        ),
        Scene(
            id=2, scene_number="102", duration_minutes=120, time_of_day=TimeOfDay.DAY, location_id=1
        ),
    ]

    from ojas_ops.adapters.film_production import optimize_intraday_schedule

    # 08:00 AM shooting call = 480 mins
    # Sunset is 18:00 = 1080 mins; dusk is 1110 mins; dusk magic hour window is [1035, 1110]
    schedule = optimize_intraday_schedule(scenes, cal, {1: loc}, {1: t}, shooting_call_minute=480)

    assert len(schedule) == 2
    magic_item = next(item for item in schedule if item[0].id == 1)
    _day_item = next(item for item in schedule if item[0].id == 2)

    # Magic hour scene must either be in dawn (<= 420) or dusk (>= 1035)
    st_magic = magic_item[1]
    is_dawn = st_magic <= cal.sunrise_minute + 30
    is_dusk = st_magic >= cal.sunset_minute - 45
    assert is_dawn or is_dusk


def test_pure_integer_model_attributes() -> None:
    """Ensure pure-integer model contracts maintain integer minutes and cents."""
    t = Talent(id=1, name="Actor", daily_rate=2500.50, max_daily_hours=8.5)
    assert t.daily_rate_cents == 250050
    assert t.max_daily_minutes == 510

    loc = Location(id=1, name="Stage", daily_rental_cost=4000.0, noise_curfew_hour=21)
    assert loc.daily_rental_cost_cents == 400000
    assert loc.noise_curfew_minute == 1260

    s = Scene(id=1, scene_number="1", duration_hours=2.5)
    assert s.duration_minutes == 150
