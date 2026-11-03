"""Two-Level Hierarchical Film Shooting Schedule Optimization Flow.

Demonstrates the end-to-end framework described in:
`research/film-shooting-schedule-optimization-framework.md`

1. Level 1: Macro Cross-Boarding Optimization via Google OR-Tools CP-SAT.
2. Master Stripboard generation with industry color coding.
3. Day-Out-of-Days (DOOD) cast status matrix with SAG-AFTRA drop-and-pickup tracking.
4. Level 2: Micro Intra-day Stripboard Sequencing with mandatory union meal breaks and setup buffers.
5. Daily Call Sheet generation with backward-calculated actor wave call times.
6. Rolling-horizon rescheduling with completed days preservation and dynamic cover set substitution.
"""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

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

# ANSI terminal color helpers
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_WHITE_BG = "\033[47m\033[30m"
C_YELLOW_BG = "\033[43m\033[30m"
C_GREEN_BG = "\033[42m\033[30m"
C_BLUE_BG = "\033[44m\033[37m"
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_MAGENTA = "\033[35m"


def build_franchise_production_dataset() -> ProductionDataset:
    """Builds a representative 2-part cross-boarded tentpole film production dataset."""
    return ProductionDataset(
        project_title="Chronicles of Ojas: The Continuum Saga (Parts 1 & 2)",
        max_shooting_days=10,
        max_hours_per_day=10.0,
        hmu_stations_capacity=2,  # 2-chair salon capacity for wave staggering
        medic_capacity=2,
        talents=[
            Talent(
                id=1,
                name="Vikram Rathore",
                character_name="Captain Vikram (Lead)",
                daily_rate=10000.0,
                daily_rate_cents=1000000,
                is_minor=False,
                max_daily_hours=12.0,
                hmu_duration_minutes=60,
                wardrobe_duration_minutes=30,
                travel_duration_minutes=30,
            ),
            Talent(
                id=2,
                name="Dr. Maya Sen",
                character_name="Dr. Sen (Antagonist)",
                daily_rate=7500.0,
                daily_rate_cents=750000,
                is_minor=False,
                max_daily_hours=12.0,
                hmu_duration_minutes=45,
                wardrobe_duration_minutes=20,
                travel_duration_minutes=30,
            ),
            Talent(
                id=3,
                name="Ananya Sharma",
                character_name="Young Tara (Minor)",
                daily_rate=2500.0,
                daily_rate_cents=250000,
                is_minor=True,
                max_daily_hours=5.0,  # Strict child labor cap
                hmu_duration_minutes=30,
                wardrobe_duration_minutes=15,
                travel_duration_minutes=20,
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
            ),
            Location(
                id=3,
                name="Heritage Vault Interior (Cover Set)",
                location_type=LocationType.PRACTICAL_INT,
                permitted_days=[1, 2, 4, 5, 8, 9, 10],
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
                stunt_hazard_level=4,
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
            ),  # Astrological rest day
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


def strip_color_badge(setting: str, time_of_day: str) -> str:
    """Returns ANSI colored tag for stripboard."""
    s = str(setting).upper()
    t = str(time_of_day).upper()
    if "INT" in s and ("DAY" in t or "MAGIC" in t):
        return f"{C_WHITE_BG} INT. DAY {C_RESET}"
    elif "EXT" in s and ("DAY" in t or "MAGIC" in t):
        return f"{C_YELLOW_BG} EXT. DAY {C_RESET}"
    elif "INT" in s and "NIGHT" in t:
        return f"{C_GREEN_BG} INT. NIGHT {C_RESET}"
    elif "EXT" in s and "NIGHT" in t:
        return f"{C_BLUE_BG} EXT. NIGHT {C_RESET}"
    return f"[{s}. {t}]"


def main() -> None:
    print(
        f"\n{C_BOLD}{C_CYAN}========================================================================{C_RESET}"
    )
    print(
        f"{C_BOLD}{C_CYAN}    OJAS-OPS: FILM SHOOTING SCHEDULE OPTIMIZATION FRAMEWORK FLOW    {C_RESET}"
    )
    print(
        f"{C_BOLD}{C_CYAN}========================================================================{C_RESET}\n"
    )

    dataset = build_franchise_production_dataset()
    print(f"{C_BOLD}Loaded Project:{C_RESET} {dataset.project_title}")
    print(
        f"{C_BOLD}Scope:{C_RESET} {len(dataset.scenes)} Scenes, {len(dataset.talents)} Cast, "
        f"{len(dataset.locations)} Locations, {len(dataset.calendar)} Calendar Days.\n"
    )

    # -------------------------------------------------------------------------
    # LEVEL 1: MACRO CROSS-BOARDING OPTIMIZATION
    # -------------------------------------------------------------------------
    print(f"{C_BOLD}{C_YELLOW}>>> PHASE 1: Level 1 Macro Cross-Boarding (OR-Tools CP-SAT){C_RESET}")
    result = optimize_production_schedule(
        dataset,
        enable_drop_pickup=True,
        enable_soundstage_lease_tracking=True,
        enable_hazard_deferral=True,
        enable_intraday_micro_optimization=True,
    )

    print(
        f"\n{C_BOLD}Optimization Result:{C_RESET} Status = {C_GREEN}{result.status}{C_RESET}, "
        f"Objective Cost = {C_GREEN}₹{result.objective_cost:,.2f}{C_RESET}, "
        f"Solve Time = {result.solve_time_seconds:.3f}s\n"
    )

    print(f"{C_BOLD}--- MASTER STRIPBOARD ---{C_RESET}")
    for day in result.stripboard.days:
        if day.is_rest_day:
            print(
                f"\n{C_BOLD}DAY {day.day_number}{C_RESET} ({day.calendar_date}) | "
                f"{C_MAGENTA}*** REST DAY / INAUSPICIOUS / ASTROLOGICAL BLACKOUT ***{C_RESET}"
            )
            continue

        print(
            f"\n{C_BOLD}DAY {day.day_number}{C_RESET} ({day.calendar_date}) | "
            f"Est. Hours: {day.total_hours:.1f}h | Scenes: {len(day.strips)} | Weather: {day.expected_weather}"
        )
        print("  " + "-" * 75)
        for idx, strip in enumerate(day.strips, 1):
            color_badge = strip_color_badge(strip.setting, strip.time_of_day)
            cast_str = ", ".join(strip.cast_names) if strip.cast_names else "None"
            print(
                f"  Strip {idx}: {color_badge} Sc {strip.scene_number:<8} Part {strip.part} "
                f"| {strip.location_name:<26} | {strip.duration_hours:>4.1f}h | Cast: {cast_str}"
            )
        print("  " + "-" * 75)

    # -------------------------------------------------------------------------
    # DAY-OUT-OF-DAYS (DOOD) CAST STATUS MATRIX
    # -------------------------------------------------------------------------
    print(f"\n{C_BOLD}{C_YELLOW}>>> PHASE 2: Day-Out-of-Days (DOOD) Cast Status Matrix{C_RESET}\n")
    all_days = [d.day_number for d in dataset.calendar]
    header = (
        f"{'Performer':<22} | "
        + " | ".join(f"D{d:>2}" for d in all_days)
        + " | Work | Hold | Paid | Total Cost"
    )
    print(C_BOLD + header + C_RESET)
    print("-" * len(header))
    for dood in result.dood_reports:
        daily_cells = [dood.daily_codes.get(d, ".") for d in all_days]
        stat_str = " | ".join(f"{s:>3}" for s in daily_cells)
        print(
            f"{dood.talent_name[:22]:<22} | {stat_str} | {dood.total_work_days:>4} | "
            f"{dood.total_hold_days:>4} | {dood.total_paid_days:>4} | ₹{dood.total_cost:>10,.2f}"
        )

    # -------------------------------------------------------------------------
    # LEVEL 2: MICRO INTRADAY SEQUENCING
    # -------------------------------------------------------------------------
    print(
        f"\n{C_BOLD}{C_YELLOW}>>> PHASE 3: Level 2 Micro Intra-day Stripboard Sequencing (Day 1){C_RESET}\n"
    )
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

    print(f"Scheduled {len(intraday_shots)} shots for Day 1:")
    for s, st_min, et_min in intraday_shots:
        st_h, st_m = divmod(st_min, 60)
        et_h, et_m = divmod(et_min, 60)
        dur = et_min - st_min
        print(
            f"  [{st_h:02d}:{st_m:02d} - {et_h:02d}:{et_m:02d}] ({dur:>3}m) : Scene {s.scene_number} "
            f"(Part {s.part}) - {s.setting}. {s.time_of_day} | Setup {s.setup_id}"
        )

    # -------------------------------------------------------------------------
    # DAILY CALL SHEET GENERATION
    # -------------------------------------------------------------------------
    print(
        f"\n{C_BOLD}{C_YELLOW}>>> PHASE 4: Daily Call Sheet Generation with Staggered HMU Waves (Day 1){C_RESET}\n"
    )
    call_sheet = generate_daily_call_sheet(
        dataset,
        1,
        day_1_scenes,
        cal_day_1,
        loc_dict,
        tal_dict,
    )

    print(
        f"CALL SHEET: Date: {call_sheet.calendar_date} | Crew Call: {call_sheet.general_crew_call} | "
        f"Shooting Call: {call_sheet.shooting_call}"
    )
    print(f"Meal 1 Due: {call_sheet.first_meal_due} | Hospital: {call_sheet.hospital_info}")
    print("\nTalent Call Schedule (Backward calculated with staggered HMU salon chairs):")
    print(
        f"  {'Character':<24} {'Actor':<18} {'Pickup':<10} {'HMU':<10} {'Wardrobe':<10} {'On Set':<8}"
    )
    print("  " + "-" * 84)
    for c in call_sheet.character_calls:
        print(
            f"  {c.character_name[:24]:<24} {c.actor_name[:18]:<18} {c.pickup_call:<10} "
            f"{c.hmu_call:<10} {c.wardrobe_call:<10} {c.set_call:<8}"
        )

    # -------------------------------------------------------------------------
    # PHASE 5: ROLLING-HORIZON RESCHEDULING & DYNAMIC DISRUPTION
    # -------------------------------------------------------------------------
    print(
        f"\n{C_BOLD}{C_YELLOW}>>> PHASE 5: Rolling-Horizon Reschedule with Weather Disruption{C_RESET}\n"
    )
    print(
        "Simulating event: Day 1 completed. Torrential rain hits Day 2 affecting Desert Exterior."
    )
    print(
        "Action: Trigger rolling reschedule with completed_days=[1] and activate_cover_sets=True.\n"
    )

    rescheduled = reschedule_production(
        dataset,
        completed_days=[1],
        weather_disruptions={2: WeatherType.RAIN},
        activate_cover_sets=True,
    )

    print(
        f"Reschedule Solver Status: {C_GREEN}{rescheduled.status}{C_RESET}, "
        f"Revised Cost: ₹{rescheduled.objective_cost:,.2f}\n"
    )

    print(f"{C_BOLD}--- REVISED MASTER STRIPBOARD ---{C_RESET}")
    for day in rescheduled.stripboard.days:
        status_flag = (
            "[COMPLETED]"
            if day.day_number == 1
            else ("[WEATHER DISRUPTED]" if day.day_number == 2 else "[ACTIVE]")
        )
        if day.is_rest_day:
            print(
                f"\n{C_BOLD}DAY {day.day_number}{C_RESET} ({day.calendar_date}) {status_flag} | "
                f"{C_MAGENTA}*** REST DAY ***{C_RESET}"
            )
            continue

        print(
            f"\n{C_BOLD}DAY {day.day_number}{C_RESET} ({day.calendar_date}) {status_flag} | "
            f"Est. Hours: {day.total_hours:.1f}h | Weather: {day.expected_weather}"
        )
        print("  " + "-" * 75)
        for idx, strip in enumerate(day.strips, 1):
            color_badge = strip_color_badge(strip.setting, strip.time_of_day)
            print(
                f"  Strip {idx}: {color_badge} Sc {strip.scene_number:<12} Part {strip.part} "
                f"| {strip.location_name:<26} | {strip.duration_hours:>4.1f}h"
            )
        print("  " + "-" * 75)

    print(f"\n{C_BOLD}{C_GREEN}✓ Flow verification completed successfully!{C_RESET}\n")


if __name__ == "__main__":
    main()
