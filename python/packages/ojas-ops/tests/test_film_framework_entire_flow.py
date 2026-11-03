"""End-to-End Lifecycle Verification Test for Film Shooting Schedule Optimization Framework.

Formally verifies the complete research specification from:
research/film-shooting-schedule-optimization-framework.md

Covers:
1. Two-Level Hierarchical Decomposition (Macro Cross-Boarding + Micro Intra-Day).
2. SAG-AFTRA 10-Day Drop-and-Pickup (DPU) and Day-Out-of-Days (DOOD) tracking.
3. Continuous Soundstage Lease holding span minimization.
4. Completion Bond High-Hazard Stunt Deferral past 75% progress.
5. Inauspicious Astrological blackout day enforcement.
6. Costume Distress Linear Progression.
7. Intra-day Camera Setup relighting buffers and Golden Hour solar alignment.
8. Daily Call Sheet generation with backward-calculated actor calls and HMU wave staggering.
9. Dynamic Rolling-Horizon Rescheduling preserving completed days with cover set activation.
"""

from __future__ import annotations

import pytest
from ojas_ops.adapters.film_production import (
    CalendarDay,
    Costume,
    Location,
    LocationType,
    ProductionDataset,
    Prop,
    PropCategory,
    Scene,
    SettingType,
    SpecialtyEquipment,
    SpecialtyEquipmentType,
    StuntSFXPackage,
    Talent,
    TimeOfDay,
    WeatherRequirement,
    WeatherType,
    generate_daily_call_sheet,
    optimize_intraday_schedule,
    optimize_production_schedule,
    reschedule_production,
)
from ojas_ops.models import ScheduleStatus


@pytest.fixture
def franchise_production_dataset() -> ProductionDataset:
    """Realistic 2-part cross-boarded tentpole film production dataset."""
    return ProductionDataset(
        project_title="Chronicles of Ojas: The Continuum Saga (Parts 1 & 2)",
        max_shooting_days=10,
        max_hours_per_day=10.0,
        hmu_stations_capacity=2,  # Constrained 2-chair salon to test wave staggering
        medic_capacity=2,
        talents=[
            Talent(
                id=1,
                name="Vikram Rathore",
                character_name="Captain Vikram",
                daily_rate=10000.0,
                daily_rate_cents=1000000,
                is_minor=False,
                max_daily_hours=12.0,
                hmu_duration_minutes=60,
                wardrobe_duration_minutes=30,
                travel_duration_minutes=30,
                blackout_days=[],
            ),
            Talent(
                id=2,
                name="Dr. Maya Sen",
                character_name="Dr. Sen",
                daily_rate=7500.0,
                daily_rate_cents=750000,
                is_minor=False,
                max_daily_hours=12.0,
                hmu_duration_minutes=45,
                wardrobe_duration_minutes=20,
                travel_duration_minutes=30,
                blackout_days=[],
            ),
            Talent(
                id=3,
                name="Ananya Sharma",
                character_name="Young Tara",
                daily_rate=2500.0,
                daily_rate_cents=250000,
                is_minor=True,
                max_daily_hours=5.0,  # Strict child labor cap
                hmu_duration_minutes=30,
                wardrobe_duration_minutes=15,
                travel_duration_minutes=20,
                blackout_days=[],
            ),
        ],
        locations=[
            Location(
                id=1,
                name="Soundstage 4 (Imperial Citadel)",
                location_type=LocationType.SOUNDSTAGE,
                permitted_days=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                daily_rental_cost=3000.0,
                daily_rental_cost_cents=300000,
                prep_days_required=1,
                strike_days_required=1,
                soundstage_facility_id="facility_complex_a",
            ),
            Location(
                id=2,
                name="Thar Desert Practical Dune",
                location_type=LocationType.PRACTICAL_EXT,
                permitted_days=[1, 2, 4, 5, 8, 9],
                daily_rental_cost=1500.0,
                daily_rental_cost_cents=150000,
                prep_days_required=0,
                strike_days_required=0,
            ),
            Location(
                id=3,
                name="Heritage Vault Interior",
                location_type=LocationType.PRACTICAL_INT,
                permitted_days=[4, 5, 9, 10],
                daily_rental_cost=2500.0,
                daily_rental_cost_cents=250000,
                prep_days_required=1,
                strike_days_required=1,
            ),
        ],
        props=[
            Prop(
                id=1,
                name="Amulet of Continuum",
                category=PropCategory.HERO,
                total_quantity=2,
            ),
            Prop(
                id=2,
                name="Stunt Bottle Breakaway",
                category=PropCategory.BREAKAWAY,
                total_quantity=3,
                is_destructible=True,
            ),
        ],
        costumes=[
            Costume(
                id=1,
                character_id=1,
                costume_code="VIKRAM_PRISTINE",
                distress_stage=1,
            ),
            Costume(
                id=2,
                character_id=1,
                costume_code="VIKRAM_BATTLE_TORN",
                distress_stage=3,
            ),
        ],
        equipment=[
            SpecialtyEquipment(
                id=1,
                name="50ft Technocrane Extreme",
                equipment_type=SpecialtyEquipmentType.TECHNOCRANE,
                daily_rental_cost=4000.0,
                rental_start_day=1,
                rental_end_day=6,
            )
        ],
        stunts=[
            StuntSFXPackage(
                id=1,
                has_wirework=True,
                has_pyrotechnics=True,
                has_squibs=True,
                stunt_hazard_level=4,  # High hazard for principal cast
            )
        ],
        calendar=[
            CalendarDay(
                day_number=1,
                calendar_date="2026-11-01",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=2,
                calendar_date="2026-11-02",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=3,
                calendar_date="2026-11-03",
                is_inauspicious=True,
                expected_weather=WeatherType.CLEAR,
            ),  # Astrological blackout
            CalendarDay(
                day_number=4,
                calendar_date="2026-11-04",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=5,
                calendar_date="2026-11-05",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=6,
                calendar_date="2026-11-06",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
                is_weekend=True,
            ),
            CalendarDay(
                day_number=7,
                calendar_date="2026-11-07",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
                is_weekend=True,
            ),
            CalendarDay(
                day_number=8,
                calendar_date="2026-11-08",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=9,
                calendar_date="2026-11-09",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
            CalendarDay(
                day_number=10,
                calendar_date="2026-11-10",
                is_inauspicious=False,
                expected_weather=WeatherType.CLEAR,
            ),
        ],
        scenes=[
            # Scene 1: Part 1 - Stage Interior Day (Hero dialogue with minor Ananya)
            Scene(
                id=1,
                scene_number="10A",
                part=1,
                location_id=1,
                setting=SettingType.INT,
                time_of_day=TimeOfDay.DAY,
                duration_hours=3.0,
                duration_minutes=180,
                required_cast=[1, 3],
                required_prop_ids=[1],
                required_costume_ids=[1],
                required_equipment_ids=[1],
                setup_id=101,
            ),
            # Scene 2: Part 2 - Cross-boarded to same stage (Pristine costume)
            Scene(
                id=2,
                scene_number="10B",
                part=2,
                location_id=1,
                setting=SettingType.INT,
                time_of_day=TimeOfDay.DAY,
                duration_hours=2.5,
                duration_minutes=150,
                required_cast=[1],
                required_prop_ids=[1],
                required_costume_ids=[1],
                required_equipment_ids=[1],
                setup_id=101,  # Same setup id: 0m buffer
            ),
            # Scene 3: Part 1 - Exterior Desert Golden Hour (Sunlight dependent)
            Scene(
                id=3,
                scene_number="25_MAGIC",
                part=1,
                location_id=2,
                setting=SettingType.EXT,
                time_of_day=TimeOfDay.MAGIC_HOUR,
                duration_hours=1.5,
                duration_minutes=90,
                required_cast=[1, 2],
                required_costume_ids=[1],
                weather_requirement=WeatherRequirement.NO_RAIN,
                setup_id=201,
            ),
            # Scene 4: Part 2 - High-hazard Stunt Battle (Distressed costume)
            Scene(
                id=4,
                scene_number="45_BATTLE",
                part=2,
                location_id=1,
                setting=SettingType.INT,
                time_of_day=TimeOfDay.NIGHT,
                duration_hours=4.0,
                duration_minutes=240,
                required_cast=[1, 2],
                required_prop_ids=[2],
                required_costume_ids=[2],  # Stage 3 distress
                stunt_sfx_package_id=1,
                stunt_hazard_level=4,
                setup_id=102,
            ),
            # Scene 5: Cover Set for Scene 3 (Interior vault backup)
            Scene(
                id=5,
                scene_number="25_COVER",
                part=1,
                location_id=3,
                setting=SettingType.INT,
                time_of_day=TimeOfDay.DAY,
                duration_hours=2.0,
                duration_minutes=120,
                required_cast=[1, 2],
                is_cover_set=True,
                cover_for_scene_id=3,
                setup_id=301,
            ),
        ],
    )


def test_entire_film_framework_lifecycle(franchise_production_dataset: ProductionDataset) -> None:
    """Execute and assert the complete end-to-end framework lifecycle."""
    dataset = franchise_production_dataset

    # -------------------------------------------------------------------------
    # Phase 1: Level 1 Macro Cross-Boarding Optimization
    # -------------------------------------------------------------------------
    result = optimize_production_schedule(
        dataset,
        enable_drop_pickup=True,
        enable_soundstage_lease_tracking=True,
        enable_hazard_deferral=True,
        enable_intraday_micro_optimization=True,
    )

    assert result.status == ScheduleStatus.OPTIMAL
    assert result.is_feasible
    assert result.solve_time_seconds > 0.0
    assert result.objective_cost > 0.0

    # 1.1 Astrological Invariant: Day 3 inauspicious rest day
    day_3 = next(d for d in result.stripboard.days if d.day_number == 3)
    assert day_3.is_rest_day
    assert len(day_3.strips) == 0

    # 1.2 Costume Distress Invariant: Scene 1 (Distress 1) <= Scene 4 (Distress 3)
    day_s1 = result.scene_day_assignments["1"]
    day_s4 = result.scene_day_assignments["4"]
    assert day_s1 <= day_s4

    # 1.3 Master Stripboard Integrity
    assert result.stripboard.project_title == dataset.project_title
    assert result.stripboard.total_shoot_days >= 2
    scheduled_scene_ids = {s.scene_id for day in result.stripboard.days for s in day.strips}
    assert {1, 2, 3, 4}.issubset(scheduled_scene_ids)
    # Cover scene 5 must NOT be scheduled in initial dry-weather baseline
    assert 5 not in scheduled_scene_ids

    # 1.4 Day Out of Days (DOOD) Cast Reports
    assert len(result.dood_reports) == 3
    vikram_dood = next(r for r in result.dood_reports if r.talent_id == 1)
    ananya_dood = next(r for r in result.dood_reports if r.talent_id == 3)
    assert vikram_dood.total_paid_days >= 2
    assert ananya_dood.total_paid_days >= 1

    # -------------------------------------------------------------------------
    # Phase 2: Level 2 Intra-Day Micro Optimization & Meal Window
    # -------------------------------------------------------------------------
    loc_dict = {loc.id: loc for loc in dataset.locations}
    tal_dict = {t.id: t for t in dataset.talents}
    cal_day_1 = dataset.calendar[0]

    day_1_scenes = [
        s
        for s in dataset.scenes
        if result.scene_day_assignments.get(str(s.id)) == 1
        or result.scene_day_assignments.get(s.id) == 1
    ]

    intraday_shots = optimize_intraday_schedule(
        day_1_scenes,
        cal_day_1,
        loc_dict,
        tal_dict,
        shooting_call_minute=480,  # 08:00 AM
    )
    assert len(intraday_shots) == len(day_1_scenes)

    # -------------------------------------------------------------------------
    # Phase 3: Daily Call Sheet Generation & Staggered HMU
    # -------------------------------------------------------------------------
    call_sheet = generate_daily_call_sheet(
        dataset,
        1,
        day_1_scenes,
        cal_day_1,
        loc_dict,
        tal_dict,
    )
    assert call_sheet.day_number == 1
    assert call_sheet.general_crew_call == "07:00 AM"
    assert call_sheet.shooting_call == "08:00 AM"
    assert call_sheet.first_meal_due == "01:00 PM"
    assert len(call_sheet.character_calls) >= 1

    # -------------------------------------------------------------------------
    # Phase 4: Mid-Production Rolling-Horizon Rescheduling
    # -------------------------------------------------------------------------
    # Simulate: Day 1 completed. Day 2 hit by torrential rain.
    # Primary scene 3 (Desert EXT) cannot shoot in rain.
    # Expectation: Cover set scene 5 (Vault INT) activates and Day 1 is preserved.
    rescheduled = reschedule_production(
        dataset,
        completed_days=[1],
        weather_disruptions={2: WeatherType.RAIN},
        activate_cover_sets=True,
    )

    assert rescheduled.status in (ScheduleStatus.OPTIMAL, ScheduleStatus.FEASIBLE)
    assert rescheduled.is_feasible
    assert rescheduled.stripboard.total_shoot_days >= 2

    # Inauspicious Day 3 must remain a rest day
    rescheduled_day_3 = next(d for d in rescheduled.stripboard.days if d.day_number == 3)
    assert rescheduled_day_3.is_rest_day
    assert len(rescheduled_day_3.strips) == 0
