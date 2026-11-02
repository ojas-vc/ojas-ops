# Domain Adapters & Industry Use Cases

Ojas Ops ships with 6 production-grade domain adapters (`ojas_ops.adapters`) that translate industry-specific scheduling entities into mathematical constraints and objectives.

```python
from ojas_ops.adapters import (
    FilmProductionScheduler,
    ManufacturingScheduler,
    WorkforceScheduler,
    AcademicTimetableScheduler,
    EventRunSheetScheduler,
    MarketingFlightingScheduler,
)
```

---

## 1. Film & Media Production: `FilmProductionScheduler`

`FilmProductionScheduler` provides a full-lifecycle computational framework for film and episodic television scheduling. It features a dual-engine architecture:
1. **Extended Combinatorial CP-SAT Engine (`optimize()` / `optimize_production_schedule()`):** Directly generates professional industry artifacts—including **Master Stripboards**, **Day Out of Days (DOOD)** cast reports, and backward-calculated **Daily Call Sheets**—while enforcing SAG-AFTRA drop-and-pickup, child labor laws, costume distress progressions, breakaway prop limits, and turnaround defense.
2. **Generic Task-Graph Engine (`build_scheduler()`):** Converts film entities into general `Task`, `Resource`, and `Constraint` models for backward-compatible solving inside the unified `Scheduler` pipeline.

### Data Contracts & Taxonomy

All domain contracts are defined as zero-overhead, strictly typed `msgspec.Struct` instances (`kw_only=True`, `gc=False`):

- **`Scene`:** Granular scene breakdowns specifying duration, script page eighths, required cast, hero props, costumes, specialty equipment, stunt packages, weather prerequisites (`RAIN_MANDATORY`, `NO_RAIN`, etc.), acoustic recording requirements (`SYNC_SOUND` vs. `MOS`), precedence, and grooming lags (`min_lag_days`).
- **`Talent`:** Cast members with contractual daily rates, minor status (`is_minor`), daily hour ceilings, blackout intervals, and prep durations (Hair/Makeup, Wardrobe, Residence Transit).
- **`Location`:** Practical and soundstage locations with permitted shooting days, noise curfews, acoustic suitability (`allows_sync_sound`), daily rental costs, and prep/strike day requirements.
- **`Prop`:** Props categorized as `HERO`, `DRESSING`, `WEAPON`, or `BREAKAWAY` (destructible items tracking daily exhaustion limits and reset times).
- **`Costume`:** Wardrobe assets tracking unidirectional distress stages (Stage 1 Clean $\rightarrow$ Stage 2 Weathered $\rightarrow$ Stage 3 Damaged $\rightarrow$ Stage 4 Destroyed) and available duplicate builds.
- **`SpecialtyEquipment`:** High-cost rented gear (Technocranes, Russian Arms, Motion Control) bounded by contractual rental windows (`rental_start_day` to `rental_end_day`).
- **`StuntSFXPackage`:** Action sequences requiring wirework, pyrotechnics, safety lockdowns, and pre-rigging intervals.
- **`CalendarDay`:** Calendar days tracking weather forecasts, statutory holidays, and cultural/astrological parameters (`is_inauspicious` for Rahu Kaal / Pitru Paksha, `is_muhurat_day` for auspicious start dates).
- **`ProductionDataset`:** Top-level immutable production container serializable to and from JSON.

### Comprehensive Optimization Constraints

The CP-SAT discrete solver enforces:

- **Upfront Domain Pruning:** Sparse variable instantiation ($x_{sd}$) filtering out infeasible days prior to model compilation based on location permits, actor blackout days, equipment lease windows, statutory holidays, weather incompatibilities, and astrological taboos.
- **Daily Workload Ceilings:** Enforces $\sum_s \text{duration}(s) \cdot x_{sd} \le \text{max\_hours}$ using scaled pure-integer knapsack constraints.
- **Child Labor Regulatory Compliance:** Strictly limits minor performers to statutory daily work limits (e.g. 5.0 hours max set time) under California DLSE, UK Children Act, and Indian NCPCR rules.
- **Costume Distress Progression:** Enforces unidirectional forward stage chaining ($d(\text{stage } k) \le d(\text{stage } k+1)$) when duplicate wardrobe builds are not funded.
- **Breakaway Prop Ceilings:** Limits daily scene destructions of breakaway items to total manufactured duplicates.
- **Grooming & Narrative Precedence:** Enforces $d(s_1) + \text{min\_lag\_days} \le d(s_2)$ for narrative dependencies and physical performer transformations (e.g. shaving beard, healing bruises).
- **Location Move Bounds:** Caps daily company moves between distinct physical locations to prevent crew exhaustion and transit waste.
- **Contractual Talent Hold Minimization & SAG-AFTRA Drop-and-Pickup:**
  - Continuous consecutive employment hold span minimization: $\min \sum_t (latest_t - earliest_t + 1) \cdot \text{daily\_rate}_t$.
  - SAG-AFTRA 10-day Drop-and-Pickup: Automatically splits talent bookings into two intervals ($[e_1, l_1]$ and $[e_2, l_2]$) when the intervening hiatus is $\ge 10$ calendar days ($e_2 - l_1 \ge 11$), waiving hold costs during the drop window and outputting `DROP` status codes.
- **Turnaround & Fraturday Mitigation:** Penalizes night-to-day transitions between consecutive production days to defend the mandatory 54-hour weekend crew turnaround.

### Production Artifacts & Reporting

- **`MasterStripboard`:** Standardized stripboard featuring 4-strip color coding:
  - **White:** Interior Day (`INT. DAY`)
  - **Yellow:** Exterior Day (`EXT. DAY`)
  - **Green:** Interior Night (`INT. NIGHT`)
  - **Blue:** Exterior Night (`EXT. NIGHT`)
  Tracks scene numbers, page eighths, cast IDs, hero props, and sound regimes.
- **`DayOutOfDaysReport` (DOOD):** Full talent matrix using standardized industry codes:
  - `SW`: Start Work (first shoot day)
  - `W`: Work (active filming day)
  - `H`: Hold (paid non-working day)
  - `WF`: Work Finish (final wrap day)
  - `SWF`: Start Work Finish (single-day booking)
  - `DROP`: Dropped talent during valid $\ge 10$-day hiatus (unpaid)
  - `.`: Off contract
  Calculates `total_work_days`, `total_hold_days`, `total_paid_days`, and financial liability.
- **`DailyCallSheet`:** Backward-calculated operational call sheet:
  $$\text{Performer Set Call} = \text{Scene Start Time} - \text{Blocking Buffer}$$
  $$\text{Performer HMU Call} = \text{Performer Set Call} - \text{HMU Duration} - \text{Wardrobe Duration}$$
  $$\text{Performer Pickup Call} = \text{Performer HMU Call} - \text{Transit Time}$$
  Includes shooting call, general crew call, first meal due time ($\le 6$ hours), second meal due time ($\le 6$ hours after first meal), and nearest emergency hospital.

### Dynamic Operational Rescheduling

When unpredictable set disruptions strike (e.g. torrential rain on exterior practical locations, sudden cast illness, or permit cancellations), `reschedule()` / `reschedule_production()` re-optimizes remaining scenes while preserving completed shoot days and automatically activating interior cover sets.

### Example: Full Combinatorial Schedule Optimization

```python
from ojas_ops.adapters.film_production import (
    CalendarDay,
    Costume,
    FilmProductionScheduler,
    Location,
    LocationType,
    ProductionDataset,
    Prop,
    PropCategory,
    Scene,
    SettingType,
    SpecialtyEquipment,
    Talent,
    TimeOfDay,
    WeatherRequirement,
    WeatherType,
    optimize_production_schedule,
)

# 1. Instantiate scheduler with fluent API
film = FilmProductionScheduler(
    project_title="Apex Predator",
    shoot_day_hours=10,
    max_shooting_days=14,
)

# 2. Add cast (including minor performer and A-list star)
film.add_cast_member(
    1,
    name="Marcus Stone",
    character_name="Captain Vance",
    daily_rate=10000.0,
    hmu_duration_minutes=45,
    wardrobe_duration_minutes=15,
    travel_duration_minutes=30,
)
film.add_cast_member(
    2,
    name="Timmy Miller",
    character_name="Billy",
    daily_rate=1500.0,
    is_minor=True,
    max_daily_hours=5.0,  # California DLSE child labor ceiling
)

# 3. Add locations with permits
film.add_location(1, name="Soundstage 2", location_type=LocationType.SOUNDSTAGE)
film.add_location(2, name="Ridge Ridge (EXT)", location_type=LocationType.PRACTICAL_EXT, permitted_days=[1, 2, 3, 4, 5])

# 4. Add physical assets
film.add_prop(1, name="Hero Blaster", category=PropCategory.HERO)
film.add_prop(2, name="Stunt Breakaway Bottle", category=PropCategory.BREAKAWAY, total_quantity=3)
film.add_costume(1, character_id=1, costume_code="VANCE_UNIFORM", distress_stage=1)
film.add_costume(2, character_id=1, costume_code="VANCE_UNIFORM", distress_stage=2)

# 5. Add scenes with dependencies and weather rules
film.add_scene(
    id=1,
    scene_number="1A",
    duration_hours=4.0,
    page_eighths=24,
    required_cast=[1, 2],
    required_costume_ids=[1],
    location_id=1,
)
film.add_scene(
    id=2,
    scene_number="5B",
    duration_hours=5.0,
    page_eighths=32,
    required_cast=[1],
    required_costume_ids=[2],  # Stage 2 costume must shoot AFTER Stage 1
    required_prop_ids=[2],
    location_id=2,
    weather_requirement=WeatherRequirement.CLEAR_ONLY,
    dependencies=["1"],
)

# 6. Solve with multithreaded CP-SAT engine and SAG-AFTRA drop-and-pickup enabled
result = film.optimize(
    enable_drop_pickup=True,
    max_time_in_seconds=15.0,
)

assert result.is_feasible
print(f"Status: {result.status.value}")
print(f"Total Shoot Days: {result.stripboard.total_shoot_days}")

# Inspect Day Out of Days (DOOD)
for dood in result.dood_reports:
    print(f"Talent {dood.talent_name}: Work={dood.total_work_days}d, Hold={dood.total_hold_days}d, Cost=${dood.total_cost:,.2f}")

# Inspect Day 1 Call Sheet
day1_call_sheet = result.call_sheets[1]
print(f"Shooting Call: {day1_call_sheet.shooting_call}")
print(f"First Meal Due: {day1_call_sheet.first_meal_due}")
for call in day1_call_sheet.character_calls:
    print(f"  {call.character_name}: Pickup={call.pickup_call}, HMU={call.hmu_call}, Set={call.set_call}")
```

### Classic Task-Graph Solving Example

For integration with general-purpose project management pipelines, `FilmProductionScheduler` can compile down to a generic `Scheduler`:

```python
film = FilmProductionScheduler()
film.add_cast_member("lead", name="Lead Actor")
film.add_location("stage", name="Soundstage")
film.add_scene(id="sc1", scene_number="1", duration_minutes=120, character_ids=["lead"], location_id="stage")
film.add_scene(id="sc2", scene_number="2", duration_minutes=180, character_ids=["lead"], location_id="stage", dependencies=["sc1"])

scheduler = film.build_scheduler()
result = scheduler.solve()
```

---

## 2. Industrial Manufacturing: `ManufacturingScheduler`

Optimizes job shop and flow shop manufacturing with sequence-dependent machine setups.

### Key Capabilities

- Multi-operation sequential jobs (e.g. Cutting $\rightarrow$ Milling $\rightarrow$ Quality Inspection).
- Sequence-dependent changeover matrix between product families on machines.
- Minimizes makespan and delivery tardiness against job due dates.

### Example

```python
mfg = ManufacturingScheduler()

mfg.add_machine("laser_cutter", name="Laser Cutting Machine")
mfg.add_machine("cnc_mill", name="5-Axis CNC Mill")

# Setup times when changing materials on the mill
mfg.set_family_setup_time("cnc_mill", "steel", "aluminum", setup_minutes=25)
mfg.set_family_setup_time("cnc_mill", "aluminum", "steel", setup_minutes=30)

# Job 1: Precision Gears
job1 = mfg.add_job("order_gears", name="Gears Batch", due_date=240)
mfg.add_operation("order_gears", "cut_gears", "laser_cutter", duration_minutes=40)
mfg.add_operation(
    "order_gears", "mill_gears", "cnc_mill", duration_minutes=60, product_family="steel"
)

scheduler = mfg.build_scheduler()
result = scheduler.solve()
```

---

## 3. Healthcare & Workforce Rostering: `WorkforceScheduler`

Schedules healthcare workers, nurses, and staff across shift slots matching skills, rest rules, and hours.

### Key Capabilities

- Shift requirements matching qualification requirements (e.g. ICU, Triage, Surgical).
- Enforces mandatory recovery rest periods between consecutive shifts (e.g. min 12 hours).
- Enforces maximum cumulative work limits (e.g. 40 hours per week).
- Selects staff dynamically from candidate pools.

### Example

```python
wf = WorkforceScheduler(horizon_minutes=24 * 60)

# Staff
wf.add_staff("nurse_sarah", name="Sarah", skills=["icu", "triage"], min_rest_minutes=120)
wf.add_staff("nurse_david", name="David", skills=["general", "icu"], min_rest_minutes=120)

# Shift slots requiring specific skills
wf.add_shift("morn_icu", start_minute=0, duration_minutes=8 * 60, required_skills=["icu"])
wf.add_shift("eve_icu", start_minute=8 * 60, duration_minutes=8 * 60, required_skills=["icu"])

scheduler = wf.build_scheduler()
result = scheduler.solve()
```

---

## 4. Academic Timetabling: `AcademicTimetableScheduler`

Produces conflict-free lecture and lab timetables for instructors, student cohorts, and classrooms.

### Key Capabilities

- Prevents instructor double-booking.
- Eliminates student cohort class conflicts.
- Distinguishes between standard lecture halls and specialized laboratories.
- Minimizes timetable gaps for students.

### Example

```python
acad = AcademicTimetableScheduler(horizon_minutes=8 * 60)

acad.add_instructor("prof_shannon", name="Prof. Shannon")
acad.add_classroom("hall_101", name="Hall 101", capacity=100, is_lab=False)
acad.add_classroom("lab_01", name="Computing Lab 1", capacity=30, is_lab=True)
acad.add_cohort("cs_seniors", name="CS Senior Cohort")

acad.add_class(
    id="info_theory",
    code="CS401",
    duration_minutes=90,
    instructor_id="prof_shannon",
    cohort_ids=["cs_seniors"],
    is_lab=False,
)

scheduler = acad.build_scheduler()
result = scheduler.solve()
```

---

## 5. Event & Conference Run-Sheets: `EventRunSheetScheduler`

Generates synchronized agendas, speaker run-sheets, and hall allocations.

### Key Capabilities

- Multi-track conference sessions and keynotes.
- Speaker prep buffer intervals and travel windows.
- Venue hall turnaround buffers (AV reset, dining layout re-dressing).
- Eliminates room capacity violations.

### Example

```python
event = EventRunSheetScheduler(event_duration_minutes=8 * 60)

event.add_hall("main_auditorium", name="Grand Ballroom", turnaround_minutes=20)
event.add_speaker("keynote_spk", name="VIP Keynote Speaker", min_prep_buffer_minutes=30)

event.add_session(
    id="opening_keynote",
    title="Keynote Address",
    duration_minutes=60,
    speaker_ids=["keynote_spk"],
    hall_id="main_auditorium",
    fixed_start=0,
)

scheduler = event.build_scheduler()
result = scheduler.solve()
```

---

## 6. Marketing & Campaign Cadence: `MarketingFlightingScheduler`

Schedules synchronized multi-channel media flights and budget pacing.

### Key Capabilities

- Stage progression (Teaser $\rightarrow$ Launch Blitz $\rightarrow$ Sustained Engagement).
- Media channels with daily budget caps and concurrency bounds.
- Paces campaign intensity to prevent overwhelming downstream sales absorption capacity.

### Example

```python
mkt = MarketingFlightingScheduler(total_campaign_days=45)

mkt.add_channel("meta_video", name="Meta Video", max_concurrent_flights=1)
mkt.add_channel("google_search", name="Google Search", max_concurrent_flights=2)

mkt.add_flight("teaser", channel_id="meta_video", duration_days=5, stage="teaser")
mkt.add_flight(
    "blitz", channel_id="meta_video", duration_days=10, stage="launch", dependencies=["teaser"]
)

scheduler = mkt.build_scheduler()
result = scheduler.solve()
```

---

## 7. Data-Driven Scenario Datasets for Adapters

Every industry domain adapter is accompanied by runnable, golden-assertion-verified JSON benchmark datasets located in `examples/**/data/`:

| Adapter                       | Example Directory                                                     | Datasets                                                  |
| :---------------------------- | :-------------------------------------------------------------------- | :-------------------------------------------------------- |
| `FilmProductionScheduler`     | [`examples/film_production/`](../examples/film_production/)           | `feature_film_production.json`, `small_shoot.json`        |
| `ManufacturingScheduler`      | [`examples/manufacturing/`](../examples/manufacturing/)               | `industrial_jobshop.json`, `large_aerospace_jobshop.json` |
| `WorkforceScheduler`          | [`examples/nurse_rostering/`](../examples/nurse_rostering/)           | `hospital_shifts.json`, `monthly_ward_roster.json`        |
| `AcademicTimetableScheduler`  | [`examples/academic_timetabling/`](../examples/academic_timetabling/) | `university_timetable.json`                               |
| `EventRunSheetScheduler`      | [`examples/event_run_sheets/`](../examples/event_run_sheets/)         | `tech_conference.json`                                    |
| `MarketingFlightingScheduler` | [`examples/marketing_flighting/`](../examples/marketing_flighting/)   | `q4_omnichannel_campaign.json`                            |
| Cultural & Panchang           | [`examples/festival_calendar/`](../examples/festival_calendar/)       | `temple_festival.json`                                    |
| General & CSV Ingestion       | [`examples/basic_scheduling/`](../examples/basic_scheduling/)         | `basic_factory.json`, `tasks.csv`, `resources.csv`        |

All examples can be executed directly:

```bash
uv run python examples/film_production/main.py
uv run python examples/manufacturing/main.py
uv run python examples/nurse_rostering/main.py
```
