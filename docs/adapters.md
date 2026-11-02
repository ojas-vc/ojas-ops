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

Coordinates scenes, cast availability, shooting locations, interior/exterior lighting, and equipment moves.

### Key Capabilities

- Groups scenes by shooting location to minimize location transit time.
- Enforces cast daily availability and blackout intervals.
- Coordinates location turnaround buffers (cleaning, set re-dressing).
- Minimizes total shooting days and cast idle time.

### Example

```python
film = FilmProductionScheduler()

# Add cast
film.add_cast_member("lead_star", name="Lead Actor", day_rate=8000.0)
film.add_cast_member("villain", name="Villain Actor", day_rate=5000.0)

# Add locations with turnaround buffers
film.add_location("palace", name="Royal Palace", turnaround_minutes=30)
film.add_location("forest", name="Deep Woods", turnaround_minutes=45)

# Add scenes
film.add_scene(
    id="scene_01",
    scene_number="1A",
    duration_minutes=90,
    character_ids=["lead_star"],
    location_id="palace",
)
film.add_scene(
    id="scene_02",
    scene_number="2B",
    duration_minutes=120,
    character_ids=["lead_star", "villain"],
    location_id="palace",
    dependencies=["scene_01"],
)

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
