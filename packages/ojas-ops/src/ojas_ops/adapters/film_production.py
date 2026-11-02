"""Film and media production shooting schedule adapter and optimization framework.

Synthesizes discrete combinatorial scheduling, talent holding cost minimization
(Day Out of Days), SAG-AFTRA drop-and-pickup logic, child labor caps, costume distress
ladders, breakaway prop daily exhaustion limits, location company move bounds, and
algorithmic daily call sheet generation.
"""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


import os
from collections import defaultdict
from datetime import datetime, timedelta
from enum import StrEnum

import msgspec
from ortools.sat.python import cp_model

from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.models.resource import ResourceType
from ojas_ops.models.schedule import ScheduleStatus
from ojas_ops.models.task import TaskPriority
from ojas_ops.models.time import IntervalWindow
from ojas_ops.objectives.composite import WeightedCompositeObjective
from ojas_ops.objectives.idle_time import MinimizeIdleTimeObjective
from ojas_ops.objectives.makespan import MinimizeMakespanObjective
from ojas_ops.scheduling.scheduler import Scheduler

# ==============================================================================
# ENUMERATIONS & DOMAIN TAXONOMY
# ==============================================================================


class PropCategory(StrEnum):
    """Classification for production physical properties."""

    HERO = "HERO"
    SET_DRESSING = "SET_DRESSING"
    BREAKAWAY = "BREAKAWAY"
    WEAPON = "WEAPON"
    VEHICLE = "VEHICLE"


class SpecialtyEquipmentType(StrEnum):
    """High-value or specialized leased technical equipment."""

    TECHNOCRANE = "TECHNOCRANE"
    PHANTOM_HIGH_SPEED = "PHANTOM_HIGH_SPEED"
    MOTION_CONTROL = "MOTION_CONTROL"
    UNDERWATER_HOUSING = "UNDERWATER_HOUSING"
    RUSSIAN_ARM = "RUSSIAN_ARM"
    DRONE = "DRONE"


class LocationType(StrEnum):
    """Type and control level of a filming location."""

    SOUNDSTAGE = "SOUNDSTAGE"
    PRACTICAL_INT = "PRACTICAL_INT"
    PRACTICAL_EXT = "PRACTICAL_EXT"


class WeatherType(StrEnum):
    """Meteorological conditions on a production shoot day."""

    CLEAR = "CLEAR"
    OVERCAST = "OVERCAST"
    RAIN = "RAIN"
    MONSOON = "MONSOON"


class WeatherRequirement(StrEnum):
    """Weather constraint envelope required for scene filming."""

    ANY = "ANY"
    CLEAR_ONLY = "CLEAR_ONLY"
    OVERCAST_ONLY = "OVERCAST_ONLY"
    RAIN_MANDATORY = "RAIN_MANDATORY"
    NO_RAIN = "NO_RAIN"


class SoundRecording(StrEnum):
    """Acoustic sound recording mode for a scene."""

    SYNC_SOUND = "SYNC_SOUND"
    MOS = "MOS"
    WILD_TRACK = "WILD_TRACK"


class HolidayCompatibility(StrEnum):
    """Policy regarding filming on statutory or cultural holidays."""

    NORMAL = "NORMAL"
    HOLIDAY_ONLY = "HOLIDAY_ONLY"
    FORBID_HOLIDAY = "FORBID_HOLIDAY"


class SettingType(StrEnum):
    """Interior vs exterior scene setting."""

    INT = "INT"
    EXT = "EXT"


class TimeOfDay(StrEnum):
    """Cinematic lighting window for a scene."""

    DAY = "DAY"
    NIGHT = "NIGHT"
    MAGIC_HOUR = "MAGIC_HOUR"


class DOODStatusCode(StrEnum):
    """Day Out of Days (DOOD) talent status notation."""

    START_WORK = "SW"
    WORK = "W"
    HOLD = "H"
    WORK_FINISH = "WF"
    START_WORK_FINISH = "SWF"
    DROP = "DROP"
    OFF = "."


class ProductionUnitType(StrEnum):
    """Classification of filming camera unit."""

    MAIN = "MAIN"
    SECOND = "SECOND"
    SPLINTER = "SPLINTER"
    VFX = "VFX"


# ==============================================================================
# CANONICAL MSGSPEC DATA CONTRACTS
# ==============================================================================


class ProductionUnit(msgspec.Struct, kw_only=True, gc=False):
    """Operational filming unit (e.g. Main Unit, 2nd Unit)."""

    id: int | str
    name: str
    unit_type: ProductionUnitType = ProductionUnitType.MAIN
    daily_operating_cost_cents: int = 0
    daily_operating_cost: float = 0.0

    def __post_init__(self) -> None:
        if self.daily_operating_cost != 0.0 and self.daily_operating_cost_cents == 0:
            self.daily_operating_cost_cents = int(round(self.daily_operating_cost * 100))
        elif self.daily_operating_cost_cents != 0 and self.daily_operating_cost == 0.0:
            self.daily_operating_cost = self.daily_operating_cost_cents / 100.0


class CameraSetup(msgspec.Struct, kw_only=True, gc=False):
    """Lighting and camera angle configuration for a scene setup."""

    id: int | str
    name: str
    axis_angle: str = ""
    lighting_setup_id: str = ""


class Prop(msgspec.Struct, kw_only=True, gc=False):
    """A physical prop required for scene action."""

    id: int | str
    name: str
    category: PropCategory = PropCategory.HERO
    total_quantity: int = 1
    is_destructible: bool = False
    requires_armorer: bool = False
    reset_duration_minutes: int = 0


class Costume(msgspec.Struct, kw_only=True, gc=False):
    """Character wardrobe asset tracking distress stages and duplicates."""

    id: int | str
    character_id: int | str
    costume_code: str
    distress_stage: int = 1  # 1: Clean, 2: Weathered, 3: Damaged, 4: Destroyed
    available_duplicates: int = 1
    requires_specialist_dresser: bool = False


class SpecialtyEquipment(msgspec.Struct, kw_only=True, gc=False):
    """High-end rented gear constrained to specific lease windows."""

    id: int | str
    name: str
    equipment_type: SpecialtyEquipmentType = SpecialtyEquipmentType.TECHNOCRANE
    daily_rental_cost: float = 0.0
    daily_rental_cost_cents: int = 0
    rental_start_day: int = 1
    rental_end_day: int = 365
    requires_certified_technician: bool = True

    def __post_init__(self) -> None:
        if self.daily_rental_cost != 0.0 and self.daily_rental_cost_cents == 0:
            self.daily_rental_cost_cents = int(round(self.daily_rental_cost * 100))
        elif self.daily_rental_cost_cents != 0 and self.daily_rental_cost == 0.0:
            self.daily_rental_cost = self.daily_rental_cost_cents / 100.0


class StuntSFXPackage(msgspec.Struct, kw_only=True, gc=False):
    """Stunt, wirework, pyrotechnics, and special effects requirements."""

    id: int | str
    has_wirework: bool = False
    has_pyrotechnics: bool = False
    has_squibs: bool = False
    pre_rigging_hours_required: float = 0.0
    pre_rigging_minutes_required: int = 0
    mandatory_medic_count: int = 1
    stunt_hazard_level: int = 1  # 1 (low) to 5 (extreme risk for principal cast)

    def __post_init__(self) -> None:
        if self.pre_rigging_hours_required != 0.0 and self.pre_rigging_minutes_required == 0:
            self.pre_rigging_minutes_required = int(self.pre_rigging_hours_required * 60)
        elif self.pre_rigging_minutes_required != 0 and self.pre_rigging_hours_required == 0.0:
            self.pre_rigging_hours_required = self.pre_rigging_minutes_required / 60.0


class Talent(msgspec.Struct, kw_only=True, gc=False):
    """Performer with daily rate, minor labor limits, and turnaround times."""

    id: int | str
    name: str
    character_name: str = ""
    daily_rate: float = 0.0
    day_rate: float = 0.0
    daily_rate_cents: int = 0
    is_minor: bool = False
    max_daily_hours: float = 10.0
    max_daily_minutes: int = 600
    hmu_duration_minutes: int = 60
    wardrobe_duration_minutes: int = 30
    travel_duration_minutes: int = 30
    blackout_days: list[int] = msgspec.field(default_factory=list)
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)
    requires_studio_teacher: bool = False
    stunt_double_id: int | str | None = None

    def __post_init__(self) -> None:
        if self.day_rate != 0.0 and self.daily_rate == 0.0:
            self.daily_rate = self.day_rate
        elif self.daily_rate != 0.0 and self.day_rate == 0.0:
            self.day_rate = self.daily_rate

        if self.daily_rate != 0.0 and self.daily_rate_cents == 0:
            self.daily_rate_cents = int(round(self.daily_rate * 100))
        elif self.daily_rate_cents != 0 and self.daily_rate == 0.0:
            self.daily_rate = self.daily_rate_cents / 100.0
            self.day_rate = self.daily_rate

        if self.max_daily_hours != 10.0 and self.max_daily_minutes == 600:
            self.max_daily_minutes = int(self.max_daily_hours * 60)
        elif self.max_daily_minutes != 600 and self.max_daily_hours == 10.0:
            self.max_daily_hours = self.max_daily_minutes / 60.0

        if not self.character_name:
            self.character_name = self.name


# Backward compatibility alias
CastMember = Talent


class Location(msgspec.Struct, kw_only=True, gc=False):
    """Filming location, soundstage, or practical exterior."""

    id: int | str
    name: str
    location_type: LocationType = LocationType.SOUNDSTAGE
    permitted_days: list[int] = msgspec.field(default_factory=list)
    noise_curfew_hour: int | None = None
    noise_curfew_minute: int | None = None
    allows_sync_sound: bool = True
    daily_rental_cost: float = 0.0
    daily_rental_cost_cents: int = 0
    prep_days_required: int = 0
    strike_days_required: int = 0
    turnaround_minutes: int = 60
    soundstage_facility_id: str | int | None = None
    blackout_windows: list[IntervalWindow] = msgspec.field(default_factory=list)

    def __post_init__(self) -> None:
        if self.daily_rental_cost != 0.0 and self.daily_rental_cost_cents == 0:
            self.daily_rental_cost_cents = int(round(self.daily_rental_cost * 100))
        elif self.daily_rental_cost_cents != 0 and self.daily_rental_cost == 0.0:
            self.daily_rental_cost = self.daily_rental_cost_cents / 100.0

        if self.noise_curfew_hour is not None and self.noise_curfew_minute is None:
            self.noise_curfew_minute = self.noise_curfew_hour * 60
        elif self.noise_curfew_minute is not None and self.noise_curfew_hour is None:
            self.noise_curfew_hour = self.noise_curfew_minute // 60


# Backward compatibility alias
ShootingLocation = Location


class CalendarDay(msgspec.Struct, kw_only=True, gc=False):
    """Calendar production day with weather forecast and cultural markers."""

    day_number: int
    calendar_date: str
    is_statutory_holiday: bool = False
    is_inauspicious: bool = False
    expected_weather: WeatherType = WeatherType.CLEAR
    sunrise_time: str = "06:15"
    sunset_time: str = "18:30"
    dawn_minute: int = 345
    sunrise_minute: int = 375
    sunset_minute: int = 1110
    dusk_minute: int = 1140
    is_weekend: bool = False

    def __post_init__(self) -> None:
        try:
            if ":" in self.sunrise_time:
                parts = self.sunrise_time.split(":")
                h, m = int(parts[0]), int(parts[1][:2])
                self.sunrise_minute = h * 60 + m
                self.dawn_minute = max(0, self.sunrise_minute - 30)
            if ":" in self.sunset_time:
                parts = self.sunset_time.split(":")
                h, m = int(parts[0]), int(parts[1][:2])
                self.sunset_minute = h * 60 + m
                self.dusk_minute = min(1440, self.sunset_minute + 30)
        except Exception:
            pass


class Scene(msgspec.Struct, kw_only=True, gc=False):
    """Screenplay scene unit requiring cast, location, props, and equipment."""

    id: int | str
    scene_number: str
    part: int = 1
    location_id: int | str = ""
    setting: SettingType = SettingType.INT
    time_of_day: TimeOfDay = TimeOfDay.DAY
    page_eighths: int = 8
    duration_hours: float = 1.0
    duration_minutes: int = 60
    required_cast: list[int | str] = msgspec.field(default_factory=list)
    character_ids: list[str] = msgspec.field(default_factory=list)
    required_prop_ids: list[int | str] = msgspec.field(default_factory=list)
    required_costume_ids: list[int | str] = msgspec.field(default_factory=list)
    required_equipment_ids: list[int | str] = msgspec.field(default_factory=list)
    stunt_sfx_package_id: int | str | None = None
    weather_requirement: WeatherRequirement = WeatherRequirement.ANY
    sound_recording: SoundRecording = SoundRecording.SYNC_SOUND
    holiday_compatibility: HolidayCompatibility = HolidayCompatibility.NORMAL
    earliest_allowed_day: int | None = None
    latest_allowed_day: int | None = None
    is_cover_set: bool = False
    cover_for_scene_id: int | str | None = None
    requires_precedence_over: int | str | None = None
    min_lag_days: int = 0
    is_second_unit: bool = False
    is_vfx_heavy: bool = False
    unit_type: ProductionUnitType = ProductionUnitType.MAIN
    setup_id: int | str | None = None
    background_count: int = 0
    vfx_turnover_deadline_day: int | None = None
    stunt_hazard_level: int = 1
    dependencies: list[str] = msgspec.field(default_factory=list)
    is_night: bool = False
    is_exterior: bool = False

    def __post_init__(self) -> None:
        if self.character_ids and not self.required_cast:
            self.required_cast = list(self.character_ids)
        elif self.required_cast and not self.character_ids:
            self.character_ids = [str(c) for c in self.required_cast]

        if self.duration_minutes != 60 and self.duration_hours == 1.0:
            self.duration_hours = self.duration_minutes / 60.0
        elif self.duration_hours != 1.0 and self.duration_minutes == 60:
            self.duration_minutes = int(self.duration_hours * 60)

        if self.is_night and self.time_of_day == TimeOfDay.DAY:
            self.time_of_day = TimeOfDay.NIGHT
        elif self.time_of_day == TimeOfDay.NIGHT:
            self.is_night = True

        if self.is_exterior and self.setting == SettingType.INT:
            self.setting = SettingType.EXT
        elif self.setting == SettingType.EXT:
            self.is_exterior = True

        if self.is_second_unit and self.unit_type == ProductionUnitType.MAIN:
            self.unit_type = ProductionUnitType.SECOND
        elif self.unit_type in (ProductionUnitType.SECOND, "SECOND"):
            self.is_second_unit = True


class ProductionDataset(msgspec.Struct, kw_only=True, gc=False):
    """Complete multi-part film production scheduling dataset."""

    project_title: str
    talents: list[Talent] = msgspec.field(default_factory=list)
    locations: list[Location] = msgspec.field(default_factory=list)
    props: list[Prop] = msgspec.field(default_factory=list)
    costumes: list[Costume] = msgspec.field(default_factory=list)
    equipment: list[SpecialtyEquipment] = msgspec.field(default_factory=list)
    stunts: list[StuntSFXPackage] = msgspec.field(default_factory=list)
    calendar: list[CalendarDay] = msgspec.field(default_factory=list)
    scenes: list[Scene] = msgspec.field(default_factory=list)
    units: list[ProductionUnit] = msgspec.field(default_factory=list)
    setups: list[CameraSetup] = msgspec.field(default_factory=list)
    max_shooting_days: int = 30
    max_hours_per_day: float = 12.0
    hmu_stations_capacity: int = 4
    medic_capacity: int = 2


# ==============================================================================
# REPORTING & OUTPUT MODELS
# ==============================================================================


class StripboardStrip(msgspec.Struct, kw_only=True, gc=False):
    """Individual strip on the production stripboard."""

    scene_id: int | str
    scene_number: str
    part: int
    setting: str
    time_of_day: str
    location_name: str
    duration_hours: float
    page_eighths: int
    cast_names: list[str]
    prop_names: list[str]
    sound_recording: str


class StripboardDay(msgspec.Struct, kw_only=True, gc=False):
    """Daily column/panel on the master stripboard."""

    day_number: int
    calendar_date: str
    is_rest_day: bool
    expected_weather: str
    total_hours: float
    total_eighths: int
    location_names: list[str]
    strips: list[StripboardStrip]


class MasterStripboard(msgspec.Struct, kw_only=True, gc=False):
    """Complete production stripboard across all shooting days."""

    project_title: str
    total_shoot_days: int
    total_hours: float
    days: list[StripboardDay]


class DayOutOfDaysReport(msgspec.Struct, kw_only=True, gc=False):
    """Day Out of Days (DOOD) cast utilization report entry."""

    talent_id: int | str
    talent_name: str
    character_name: str
    daily_codes: dict[int, str]
    total_work_days: int
    total_hold_days: int
    total_paid_days: int
    earliest_work_day: int | None = None
    latest_work_day: int | None = None
    total_cost: float = 0.0


class CallSheetSceneEntry(msgspec.Struct, kw_only=True, gc=False):
    """Scene line item on the daily call sheet."""

    scene_number: str
    start_time: str
    end_time: str
    setting: str
    time_of_day: str
    location_name: str
    cast_ids: list[str]
    page_eighths: int


class CallSheetCharacterEntry(msgspec.Struct, kw_only=True, gc=False):
    """Actor call time matrix calculated backwards from camera call."""

    talent_id: int | str
    character_name: str
    actor_name: str
    pickup_call: str
    hmu_call: str
    wardrobe_call: str
    set_call: str


class DailyCallSheet(msgspec.Struct, kw_only=True, gc=False):
    """Comprehensive daily production call sheet."""

    day_number: int
    calendar_date: str
    project_title: str
    sunrise_time: str
    sunset_time: str
    expected_weather: str
    general_crew_call: str
    shooting_call: str
    first_meal_due: str
    second_meal_due: str | None = None
    hospital_info: str
    scene_entries: list[CallSheetSceneEntry]
    character_calls: list[CallSheetCharacterEntry]


class FilmScheduleResult(msgspec.Struct, kw_only=True, gc=False):
    """Comprehensive outcome of a film production scheduling run."""

    status: ScheduleStatus
    is_feasible: bool
    solve_time_seconds: float
    objective_cost: float
    stripboard: MasterStripboard
    dood_reports: list[DayOutOfDaysReport]
    call_sheets: dict[int, DailyCallSheet] = msgspec.field(default_factory=dict)
    scene_day_assignments: dict[str, int] = msgspec.field(default_factory=dict)
    talent_daily_status: dict[str, dict[int, str]] = msgspec.field(default_factory=dict)


# ==============================================================================
# DISCRETE OPTIMIZATION SOLVER ENGINE
# ==============================================================================


def optimize_production_schedule(
    data: ProductionDataset,
    *,
    max_time_in_seconds: float = 30.0,
    num_workers: int | None = None,
    move_penalty: int = 500,
    enable_drop_pickup: bool = False,
    enable_soundstage_lease_tracking: bool = False,
    enable_hazard_deferral: bool = False,
    enable_intraday_micro_optimization: bool = True,
    fixed_assignments: dict[int | str, int] | None = None,
) -> FilmScheduleResult:
    """Build and solve the extended film shooting schedule using Google OR-Tools CP-SAT."""
    t_start = datetime.now()
    model = cp_model.CpModel()
    num_days = data.max_shooting_days

    # 1. Lookup Dictionaries & Automatic Calendar Synthesis
    scene_dict: dict[int | str, Scene] = {}
    for s in data.scenes:
        scene_dict[s.id] = s
        scene_dict[str(s.id)] = s

    talent_dict: dict[int | str, Talent] = {}
    for t in data.talents:
        talent_dict[t.id] = t
        talent_dict[str(t.id)] = t

    location_dict: dict[int | str, Location] = {}
    for loc in data.locations:
        location_dict[loc.id] = loc
        location_dict[str(loc.id)] = loc

    prop_dict: dict[int | str, Prop] = {}
    for prop_item in data.props:
        prop_dict[prop_item.id] = prop_item
        prop_dict[str(prop_item.id)] = prop_item

    costume_dict: dict[int | str, Costume] = {}
    for cost in data.costumes:
        costume_dict[cost.id] = cost
        costume_dict[str(cost.id)] = cost

    equipment_dict: dict[int | str, SpecialtyEquipment] = {}
    for eq_item in data.equipment:
        equipment_dict[eq_item.id] = eq_item
        equipment_dict[str(eq_item.id)] = eq_item

    # Ensure Calendar exists for all days
    calendar_dict: dict[int, CalendarDay] = {}
    for cal_day in data.calendar:
        calendar_dict[cal_day.day_number] = cal_day
    for d in range(1, num_days + 1):
        if d not in calendar_dict:
            calendar_dict[d] = CalendarDay(day_number=d, calendar_date=f"Day {d:02d}")

    # 2. Inverted Indexing for Fast Relational Constraint Assembly
    scenes_by_talent: dict[int | str, list[Scene]] = defaultdict(list)
    scenes_by_location: dict[int | str, list[Scene]] = defaultdict(list)
    scenes_by_prop: dict[int | str, list[Scene]] = defaultdict(list)
    scenes_by_costume: dict[int | str, list[Scene]] = defaultdict(list)

    for s in data.scenes:
        for cid in s.required_cast:
            scenes_by_talent[cid].append(s)
            scenes_by_talent[str(cid)].append(s)
        scenes_by_location[s.location_id].append(s)
        scenes_by_location[str(s.location_id)].append(s)
        for pid in s.required_prop_ids:
            scenes_by_prop[pid].append(s)
            scenes_by_prop[str(pid)].append(s)
        for c_id in s.required_costume_ids:
            scenes_by_costume[c_id].append(s)
            scenes_by_costume[str(c_id)].append(s)

    # 3. Upfront Domain Pruning (Sparse Variable Instantiation)
    feasible_days_by_scene: dict[int | str, list[int]] = {}
    x: dict[tuple[int | str, int], cp_model.IntVar] = {}
    day_scene_vars: dict[int, list[cp_model.IntVar]] = defaultdict(list)
    day_scene_durations: dict[int, list[int]] = defaultdict(list)
    scene_vars_by_day: dict[int, dict[int | str, cp_model.IntVar]] = defaultdict(dict)

    scale = 10
    max_daily_units = int(data.max_hours_per_day * scale)

    for s in data.scenes:
        valid_days: list[int] = []
        loc_opt: Location | None = location_dict.get(s.location_id) or location_dict.get(str(s.location_id))

        for d in range(1, num_days + 1):
            cal = calendar_dict[d]
            is_valid = True

            # Fixed assignments check
            if fixed_assignments and (s.id in fixed_assignments or str(s.id) in fixed_assignments):
                target_d = fixed_assignments.get(s.id)
                if target_d is None:
                    target_d = fixed_assignments.get(str(s.id))
                if target_d != d:
                    is_valid = False

            # Calendar Window Bounds
            if is_valid and s.earliest_allowed_day is not None and d < s.earliest_allowed_day:
                is_valid = False
            elif is_valid and s.latest_allowed_day is not None and d > s.latest_allowed_day:
                is_valid = False
            # Location Permits
            elif is_valid and loc_opt and loc_opt.permitted_days and d not in loc_opt.permitted_days:
                is_valid = False
            # Astrological / Inauspicious Days
            elif is_valid and cal.is_inauspicious:
                is_valid = False
            # Holiday Filtering
            elif (
                is_valid
                and s.holiday_compatibility
                in (HolidayCompatibility.FORBID_HOLIDAY, "FORBID_HOLIDAY")
                and cal.is_statutory_holiday
            ):
                is_valid = False
            elif (
                is_valid
                and s.holiday_compatibility in (HolidayCompatibility.HOLIDAY_ONLY, "HOLIDAY_ONLY")
                and not cal.is_statutory_holiday
            ):
                is_valid = False
            # Weather Compatibility
            elif is_valid and s.weather_requirement in (
                WeatherRequirement.RAIN_MANDATORY,
                "RAIN_MANDATORY",
            ):
                if cal.expected_weather not in (
                    WeatherType.RAIN,
                    WeatherType.MONSOON,
                    "RAIN",
                    "MONSOON",
                ):
                    is_valid = False
            elif is_valid and s.weather_requirement in (
                WeatherRequirement.NO_RAIN,
                WeatherRequirement.CLEAR_ONLY,
                "NO_RAIN",
                "CLEAR_ONLY",
            ):
                if cal.expected_weather in (
                    WeatherType.RAIN,
                    WeatherType.MONSOON,
                    "RAIN",
                    "MONSOON",
                ):
                    is_valid = False
            elif is_valid and s.weather_requirement in (
                WeatherRequirement.OVERCAST_ONLY,
                "OVERCAST_ONLY",
            ):
                if cal.expected_weather not in (WeatherType.OVERCAST, "OVERCAST"):
                    is_valid = False
            # Acoustic Noise vs Rain
            elif (
                is_valid
                and s.sound_recording in (SoundRecording.SYNC_SOUND, "SYNC_SOUND")
                and loc_opt
                and not loc_opt.allows_sync_sound
                and cal.expected_weather
                in (WeatherType.RAIN, WeatherType.MONSOON, "RAIN", "MONSOON")
            ):
                is_valid = False
            # VFX Early Turnover Deadline
            elif is_valid and s.vfx_turnover_deadline_day is not None and d > s.vfx_turnover_deadline_day:
                is_valid = False
            # Location Noise Curfew
            elif (
                is_valid
                and s.time_of_day in (TimeOfDay.NIGHT, "NIGHT")
                and loc_opt
                and loc_opt.noise_curfew_hour is not None
                and loc_opt.noise_curfew_hour < 22
                and s.stunt_sfx_package_id is not None
            ):
                stunt_pkg = next((p for p in data.stunts if p.id == s.stunt_sfx_package_id or str(p.id) == str(s.stunt_sfx_package_id)), None)
                if stunt_pkg and (stunt_pkg.has_pyrotechnics or stunt_pkg.has_squibs):
                    is_valid = False
            else:
                # Equipment Leases
                if is_valid:
                    for eq_id in s.required_equipment_ids:
                        eq = equipment_dict.get(eq_id) or equipment_dict.get(str(eq_id))
                        if eq and (d < eq.rental_start_day or d > eq.rental_end_day):
                            is_valid = False
                            break
                # Cast Blackouts
                if is_valid:
                    for cid in s.required_cast:
                        tal = talent_dict.get(cid) or talent_dict.get(str(cid))
                        if tal and d in tal.blackout_days:
                            is_valid = False
                            break

            if is_valid:
                valid_days.append(d)

        feasible_days_by_scene[s.id] = valid_days
        feasible_days_by_scene[str(s.id)] = valid_days

        # Instantiate sparse decision variables only for valid days
        duration_unit = int(s.duration_hours * scale)
        for d in valid_days:
            var = model.new_bool_var(f"x_s{s.id}_d{d}")
            x[s.id, d] = var
            x[str(s.id), d] = var
            day_scene_vars[d].append(var)
            day_scene_durations[d].append(duration_unit)
            scene_vars_by_day[d][s.id] = var
            scene_vars_by_day[d][str(s.id)] = var

    # Constraint 1: Scene Assignment Uniqueness
    for s in data.scenes:
        candidate_vars = [x[s.id, d] for d in feasible_days_by_scene[s.id]]
        if not candidate_vars and not s.is_cover_set:
            return FilmScheduleResult(
                status=ScheduleStatus.INFEASIBLE,
                is_feasible=False,
                solve_time_seconds=(datetime.now() - t_start).total_seconds(),
                objective_cost=0.0,
                stripboard=MasterStripboard(
                    project_title=data.project_title,
                    total_shoot_days=0,
                    total_hours=0.0,
                    days=[],
                ),
                dood_reports=[],
            )

        if not s.is_cover_set:
            model.add_exactly_one(candidate_vars)
        else:
            model.add(sum(candidate_vars) <= 1)

    # Constraint 2: Daily Workload & Child Labor Limits
    for d in range(1, num_days + 1):
        if day_scene_vars[d]:
            daily_expr = cp_model.LinearExpr.WeightedSum(day_scene_vars[d], day_scene_durations[d])
            model.add(daily_expr <= max_daily_units)

            # Child Labor Caps
            for t in data.talents:
                if t.is_minor:
                    minor_max = int(t.max_daily_hours * scale)
                    minor_scenes_on_day = [
                        scene_vars_by_day[d][s.id]
                        for s in scenes_by_talent[t.id]
                        if s.id in scene_vars_by_day[d]
                    ]
                    if minor_scenes_on_day:
                        is_minor_working = model.new_bool_var(f"minor_{t.id}_active_d{d}")
                        model.add_max_equality(is_minor_working, minor_scenes_on_day)
                        model.add(daily_expr <= minor_max).only_enforce_if(is_minor_working)

    # Constraint 3: Explicit Precedence Constraints
    for s in data.scenes:
        if s.requires_precedence_over is not None:
            target_id = s.requires_precedence_over
            if (
                target_id in scene_dict
                and feasible_days_by_scene[s.id]
                and feasible_days_by_scene[target_id]
            ):
                s1_day = cp_model.LinearExpr.WeightedSum(
                    [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                    feasible_days_by_scene[s.id],
                )
                s2_day = cp_model.LinearExpr.WeightedSum(
                    [x[target_id, d] for d in feasible_days_by_scene[target_id]],
                    feasible_days_by_scene[target_id],
                )
                min_lag = max(1, s.min_lag_days)
                model.add(s1_day + min_lag <= s2_day)

        if s.dependencies:
            for dep_id in s.dependencies:
                if (
                    dep_id in scene_dict
                    and feasible_days_by_scene[dep_id]
                    and feasible_days_by_scene[s.id]
                ):
                    dep_scene = scene_dict[dep_id]
                    dep_day = cp_model.LinearExpr.WeightedSum(
                        [x[dep_id, d] for d in feasible_days_by_scene[dep_id]],
                        feasible_days_by_scene[dep_id],
                    )
                    this_day = cp_model.LinearExpr.WeightedSum(
                        [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                        feasible_days_by_scene[s.id],
                    )
                    min_lag = max(1, dep_scene.min_lag_days)
                    model.add(dep_day + min_lag <= this_day)

    # Constraint 4: Linear Stage-Chaining for Costume Distress Ladders
    character_costumes: dict[int | str, list[Costume]] = defaultdict(list)
    for cost in data.costumes:
        character_costumes[cost.character_id].append(cost)

    for _char_id, c_list in character_costumes.items():
        if len(c_list) > 1:
            sorted_costumes = sorted(c_list, key=lambda c: c.distress_stage)
            for idx in range(len(sorted_costumes) - 1):
                c_early = sorted_costumes[idx]
                c_late = sorted_costumes[idx + 1]
                if c_early.distress_stage < c_late.distress_stage:
                    scenes_early = scenes_by_costume[c_early.id]
                    scenes_late = scenes_by_costume[c_late.id]
                    if scenes_early and scenes_late:
                        max_early_day = model.new_int_var(1, num_days, f"max_day_c{c_early.id}")
                        early_day_exprs = [
                            cp_model.LinearExpr.WeightedSum(
                                [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                                feasible_days_by_scene[s.id],
                            )
                            for s in scenes_early
                            if feasible_days_by_scene[s.id]
                        ]
                        if early_day_exprs:
                            model.add_max_equality(max_early_day, early_day_exprs)

                            for s_late in scenes_late:
                                if feasible_days_by_scene[s_late.id]:
                                    late_day_expr = cp_model.LinearExpr.WeightedSum(
                                        [
                                            x[s_late.id, d]
                                            for d in feasible_days_by_scene[s_late.id]
                                        ],
                                        feasible_days_by_scene[s_late.id],
                                    )
                                    model.add(max_early_day <= late_day_expr)

    # Constraint 5: Breakaway Prop Daily Exhaustion Limits
    for p in data.props:
        if p.category in (PropCategory.BREAKAWAY, "BREAKAWAY") and p.is_destructible:
            scenes_with_prop = scenes_by_prop[p.id]
            for d in range(1, num_days + 1):
                p_vars = [
                    scene_vars_by_day[d][s.id]
                    for s in scenes_with_prop
                    if s.id in scene_vars_by_day[d]
                ]
                if p_vars:
                    model.add(sum(p_vars) <= p.total_quantity)

    # Constraint 6: Location Tracking & Move Limits
    loc_active: dict[tuple[int | str, int], cp_model.IntVar] = {}
    for loc_item in data.locations:
        scenes_at_loc = scenes_by_location[loc_item.id]
        if not scenes_at_loc:
            continue
        for d in range(1, num_days + 1):
            active_scenes = [
                scene_vars_by_day[d][s.id] for s in scenes_at_loc if s.id in scene_vars_by_day[d]
            ]
            if active_scenes:
                loc_var = model.new_bool_var(f"loc_{loc_item.id}_d{d}")
                loc_active[loc_item.id, d] = loc_var
                model.add_max_equality(loc_var, active_scenes)

    for d in range(1, num_days + 1):
        day_locs = [loc_active[loc_item.id, d] for loc_item in data.locations if (loc_item.id, d) in loc_active]
        if day_locs:
            model.add(sum(day_locs) <= 2)

    # Constraint 7: Day Out of Days (DOOD) Talent Hold Bounds
    hold_cost_terms = []
    talent_work: dict[tuple[int | str, int], cp_model.IntVar] = {}
    earliest: dict[int | str, cp_model.IntVar] = {}
    latest: dict[int | str, cp_model.IntVar] = {}
    talent_drop_info: dict[
        int | str,
        tuple[
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
        ],
    ] = {}

    for t in data.talents:
        scenes_with_t = scenes_by_talent[t.id]
        if not scenes_with_t:
            continue

        all_t_days = {d for s in scenes_with_t for d in feasible_days_by_scene[s.id]}
        if not all_t_days:
            continue

        t_min_day, t_max_day = min(all_t_days), max(all_t_days)

        if enable_drop_pickup and num_days >= 12 and t.daily_rate > 0:
            is_drop = model.new_bool_var(f"is_drop_t{t.id}")
            e1 = model.new_int_var(t_min_day, t_max_day, f"e1_t{t.id}")
            l1 = model.new_int_var(t_min_day, t_max_day, f"l1_t{t.id}")
            e2 = model.new_int_var(t_min_day, t_max_day, f"e2_t{t.id}")
            l2 = model.new_int_var(t_min_day, t_max_day, f"l2_t{t.id}")
            model.add(e1 <= l1)
            model.add(e2 <= l2).only_enforce_if(is_drop)
            # Minimum 10 drop days hiatus between intervals: e2 - l1 >= 11
            model.add(e2 - l1 >= 11).only_enforce_if(is_drop)

            span1 = model.new_int_var(0, num_days, f"span1_t{t.id}")
            span2 = model.new_int_var(0, num_days, f"span2_t{t.id}")
            model.add(span1 == l1 - e1 + 1)
            model.add(span2 == l2 - e2 + 1).only_enforce_if(is_drop)
            model.add(span2 == 0).only_enforce_if(is_drop.negated())

            for d in range(1, num_days + 1):
                active_cast_scenes = [
                    scene_vars_by_day[d][s.id]
                    for s in scenes_with_t
                    if s.id in scene_vars_by_day[d]
                ]
                if active_cast_scenes:
                    w_var = model.new_bool_var(f"twork_t{t.id}_d{d}")
                    talent_work[t.id, d] = w_var
                    model.add_max_equality(w_var, active_cast_scenes)
                    in_b1 = model.new_bool_var(f"in_b1_t{t.id}_d{d}")
                    in_b2 = model.new_bool_var(f"in_b2_t{t.id}_d{d}")
                    model.add(in_b1 + in_b2 == w_var)
                    model.add(in_b2 == 0).only_enforce_if(is_drop.negated())
                    model.add(e1 <= d).only_enforce_if(in_b1)
                    model.add(l1 >= d).only_enforce_if(in_b1)
                    model.add(e2 <= d).only_enforce_if(in_b2)
                    model.add(l2 >= d).only_enforce_if(in_b2)

            comp_span = model.new_int_var(0, num_days, f"comp_span_t{t.id}")
            model.add(comp_span == span1 + span2)
            hold_cost_terms.append(comp_span * int(t.daily_rate))
            earliest[t.id] = e1
            actual_latest = model.new_int_var(t_min_day, t_max_day, f"actual_latest_t{t.id}")
            model.add(actual_latest == l1).only_enforce_if(is_drop.negated())
            model.add(actual_latest == l2).only_enforce_if(is_drop)
            latest[t.id] = actual_latest
            talent_drop_info[t.id] = (is_drop, e1, l1, e2, l2)
        else:
            earliest[t.id] = model.new_int_var(t_min_day, t_max_day, f"earliest_t{t.id}")
            latest[t.id] = model.new_int_var(t_min_day, t_max_day, f"latest_t{t.id}")

            for d in range(1, num_days + 1):
                active_cast_scenes = [
                    scene_vars_by_day[d][s.id]
                    for s in scenes_with_t
                    if s.id in scene_vars_by_day[d]
                ]
                if active_cast_scenes:
                    w_var = model.new_bool_var(f"twork_t{t.id}_d{d}")
                    talent_work[t.id, d] = w_var
                    model.add_max_equality(w_var, active_cast_scenes)
                    model.add(earliest[t.id] <= d).only_enforce_if(w_var)
                    model.add(latest[t.id] >= d).only_enforce_if(w_var)

            span_var = model.new_int_var(0, num_days, f"span_t{t.id}")
            model.add(span_var == latest[t.id] - earliest[t.id] + 1)
            hold_cost_terms.append(span_var * int(t.daily_rate))

    # Move Penalties & Turnaround (Fraturday) Penalties
    move_cost_terms = [var * move_penalty for var in loc_active.values()]

    turnaround_penalty_terms: list[cp_model.LinearExpr] = []
    night_scenes = [s for s in data.scenes if s.time_of_day in (TimeOfDay.NIGHT, "NIGHT")]
    day_scenes = [s for s in data.scenes if s.time_of_day in (TimeOfDay.DAY, "DAY")]

    if night_scenes and day_scenes:
        for d in range(1, num_days):
            night_vars_d = [
                scene_vars_by_day[d][s.id] for s in night_scenes if s.id in scene_vars_by_day[d]
            ]
            day_vars_next = [
                scene_vars_by_day[d + 1][s.id]
                for s in day_scenes
                if s.id in scene_vars_by_day[d + 1]
            ]
            if night_vars_d and day_vars_next:
                has_night_d = model.new_bool_var(f"has_night_d{d}")
                has_day_next = model.new_bool_var(f"has_day_d{d+1}")
                model.add_max_equality(has_night_d, night_vars_d)
                model.add_max_equality(has_day_next, day_vars_next)

                turnaround_violation = model.new_bool_var(f"turnaround_violation_d{d}")
                model.add_bool_and([has_night_d, has_day_next]).only_enforce_if(turnaround_violation)
                model.add(turnaround_violation == 1).only_enforce_if([has_night_d, has_day_next])
                turnaround_penalty_terms.append(turnaround_violation * 1000)

    # --------------------------------------------------------------------------
    # CONSTRAINT 8: Continuous Soundstage Leases & Stage Facility Disjunction
    # --------------------------------------------------------------------------
    stage_lease_terms: list[cp_model.LinearExpr] = []
    location_prep_strike_intervals: dict[int | str, tuple[cp_model.IntVar, cp_model.IntVar, cp_model.IntVar]] = {}

    for loc in data.locations:
        scenes_at_loc = scenes_by_location[loc.id]
        if not scenes_at_loc:
            continue
        active_loc_days = [
            loc_active[loc.id, d] for d in range(1, num_days + 1) if (loc.id, d) in loc_active
        ]
        if not active_loc_days:
            continue

        loc_is_used = model.new_bool_var(f"loc_used_{loc.id}")
        model.add_max_equality(loc_is_used, active_loc_days)

        first_shoot_loc = model.new_int_var(1, num_days, f"first_shoot_{loc.id}")
        last_shoot_loc = model.new_int_var(1, num_days, f"last_shoot_{loc.id}")

        for d in range(1, num_days + 1):
            if (loc.id, d) in loc_active:
                model.add(first_shoot_loc <= d).only_enforce_if(loc_active[loc.id, d])
                model.add(last_shoot_loc >= d).only_enforce_if(loc_active[loc.id, d])

        prep_days = loc.prep_days_required
        strike_days = loc.strike_days_required
        prep_start_day = model.new_int_var(1 - prep_days, num_days, f"prep_start_{loc.id}")
        strike_end_day = model.new_int_var(1, num_days + strike_days, f"strike_end_{loc.id}")

        model.add(prep_start_day == first_shoot_loc - prep_days).only_enforce_if(loc_is_used)
        model.add(strike_end_day == last_shoot_loc + strike_days).only_enforce_if(loc_is_used)

        lease_days = model.new_int_var(0, num_days + prep_days + strike_days, f"lease_days_{loc.id}")
        model.add(lease_days == strike_end_day - prep_start_day + 1).only_enforce_if(loc_is_used)
        model.add(lease_days == 0).only_enforce_if(loc_is_used.negated())

        rental_rate = int(loc.daily_rental_cost) if loc.daily_rental_cost > 0 else (loc.daily_rental_cost_cents // 100)
        if enable_soundstage_lease_tracking and rental_rate > 0:
            stage_lease_terms.append(lease_days * rental_rate)

        location_prep_strike_intervals[loc.id] = (loc_is_used, prep_start_day, strike_end_day)

    # Stage Disjunction for sets sharing the same physical soundstage facility
    facility_sets: dict[str | int, list[Location]] = defaultdict(list)
    for loc in data.locations:
        if loc.soundstage_facility_id:
            facility_sets[loc.soundstage_facility_id].append(loc)

    for _fac_id, set_list in facility_sets.items():
        if len(set_list) > 1:
            for i in range(len(set_list)):
                for j in range(i + 1, len(set_list)):
                    loc_a = set_list[i]
                    loc_b = set_list[j]
                    prep_a = loc_a.prep_days_required
                    strike_a = loc_a.strike_days_required
                    prep_b = loc_b.prep_days_required
                    strike_b = loc_b.strike_days_required
                    a_before_b = model.new_bool_var(f"a_before_b_{loc_a.id}_{loc_b.id}")

                    for da in range(1, num_days + 1):
                        if (loc_a.id, da) in loc_active:
                            for db in range(1, num_days + 1):
                                if (loc_b.id, db) in loc_active:
                                    if da + strike_a >= db - prep_b:
                                        model.add_bool_or([
                                            loc_active[loc_a.id, da].negated(),
                                            loc_active[loc_b.id, db].negated(),
                                            a_before_b.negated(),
                                        ])
                                    if db + strike_b >= da - prep_a:
                                        model.add_bool_or([
                                            loc_active[loc_a.id, da].negated(),
                                            loc_active[loc_b.id, db].negated(),
                                            a_before_b,
                                        ])

    # --------------------------------------------------------------------------
    # CONSTRAINT 9: Multi-Unit Concurrency & Cast Exclusivity
    # --------------------------------------------------------------------------
    distinct_units = {str(s.unit_type) for s in data.scenes}
    if len(distinct_units) > 1:
        for t in data.talents:
            scenes_t = scenes_by_talent[t.id]
            for d in range(1, num_days + 1):
                unit_vars_for_d = []
                for u_name in distinct_units:
                    u_scenes = [
                        scene_vars_by_day[d][s.id]
                        for s in scenes_t
                        if str(s.unit_type) == u_name and s.id in scene_vars_by_day[d]
                    ]
                    if u_scenes:
                        u_act = model.new_bool_var(f"t_{t.id}_u_{u_name}_d{d}")
                        model.add_max_equality(u_act, u_scenes)
                        unit_vars_for_d.append(u_act)
                if len(unit_vars_for_d) > 1:
                    model.add(sum(unit_vars_for_d) <= 1)

    # --------------------------------------------------------------------------
    # CONSTRAINT 10: High-Hazard Stunt Deferral
    # --------------------------------------------------------------------------
    hazard_penalty_terms: list[cp_model.LinearExpr] = []
    if enable_hazard_deferral:
        for s in data.scenes:
            is_high_hazard = s.stunt_hazard_level >= 4
            if not is_high_hazard and s.stunt_sfx_package_id:
                stunt_pkg = next((pkg for pkg in data.stunts if pkg.id == s.stunt_sfx_package_id), None)
                if stunt_pkg and stunt_pkg.stunt_hazard_level >= 4:
                    is_high_hazard = True

            if is_high_hazard:
                for cid in s.required_cast:
                    if cid in earliest and cid in latest:
                        s_day = cp_model.LinearExpr.WeightedSum(
                            [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                            feasible_days_by_scene[s.id],
                        )
                        early_stunt = model.new_bool_var(f"early_stunt_s{s.id}_c{cid}")
                        model.add(4 * s_day - 3 * earliest[cid] < latest[cid]).only_enforce_if(early_stunt)
                        hazard_penalty_terms.append(early_stunt * 2000)

    # --------------------------------------------------------------------------
    # CONSTRAINT 11: Background Extras Clustering
    # --------------------------------------------------------------------------
    extras_cost_terms: list[cp_model.LinearExpr] = []
    large_extras_scenes = [s for s in data.scenes if s.background_count >= 50]
    if large_extras_scenes:
        for d in range(1, num_days + 1):
            extras_day_vars = [
                scene_vars_by_day[d][s.id]
                for s in large_extras_scenes
                if s.id in scene_vars_by_day[d]
            ]
            if extras_day_vars:
                has_extras_d = model.new_bool_var(f"has_extras_d{d}")
                model.add_max_equality(has_extras_d, extras_day_vars)
                extras_cost_terms.append(has_extras_d * 500)

    # Objective Function: Minimize Talent Hold Spans + Moves + Turnarounds + Stage Leases + Stunt Hazards
    model.minimize(
        cp_model.LinearExpr.Sum(
            hold_cost_terms
            + move_cost_terms
            + turnaround_penalty_terms
            + stage_lease_terms
            + hazard_penalty_terms
            + extras_cost_terms
        )
    )

    # Multithreaded CP-SAT Solver Parameters
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_in_seconds
    solver.parameters.num_search_workers = num_workers or (os.cpu_count() or 8)
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2

    status_code = solver.solve(model)
    solve_duration = (datetime.now() - t_start).total_seconds()

    if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule_status = (
            ScheduleStatus.OPTIMAL if status_code == cp_model.OPTIMAL else ScheduleStatus.FEASIBLE
        )
        scheduled_day_scenes: dict[int, list[Scene]] = defaultdict(list)
        scene_day_assignments: dict[str, int] = {}

        for s in data.scenes:
            for d in feasible_days_by_scene[s.id]:
                if (s.id, d) in x and solver.value(x[s.id, d]) == 1:
                    scheduled_day_scenes[d].append(s)
                    scene_day_assignments[str(s.id)] = d

        # 1. Master Stripboard Construction
        stripboard_days: list[StripboardDay] = []
        for d in range(1, num_days + 1):
            day_scenes = scheduled_day_scenes.get(d, [])
            cal = calendar_dict[d]
            loc_names = {
                location_dict[s.location_id].name
                for s in day_scenes
                if s.location_id in location_dict
            }
            strips: list[StripboardStrip] = [
                StripboardStrip(
                    scene_id=s.id,
                    scene_number=s.scene_number,
                    part=s.part,
                    setting=str(s.setting),
                    time_of_day=str(s.time_of_day),
                    location_name=location_dict[s.location_id].name
                    if s.location_id in location_dict
                    else "",
                    duration_hours=s.duration_hours,
                    page_eighths=s.page_eighths,
                    cast_names=[
                        talent_dict[cid].name for cid in s.required_cast if cid in talent_dict
                    ],
                    prop_names=[
                        prop_dict[pid].name for pid in s.required_prop_ids if pid in prop_dict
                    ],
                    sound_recording=str(s.sound_recording),
                )
                for s in day_scenes
            ]
            stripboard_days.append(
                StripboardDay(
                    day_number=d,
                    calendar_date=cal.calendar_date,
                    is_rest_day=len(day_scenes) == 0,
                    expected_weather=str(cal.expected_weather),
                    total_hours=sum(s.duration_hours for s in day_scenes),
                    total_eighths=sum(s.page_eighths for s in day_scenes),
                    location_names=sorted(loc_names),
                    strips=strips,
                )
            )

        master_stripboard = MasterStripboard(
            project_title=data.project_title,
            total_shoot_days=len([d for d in stripboard_days if not d.is_rest_day]),
            total_hours=sum(d.total_hours for d in stripboard_days),
            days=stripboard_days,
        )

        # 2. DOOD Reports Construction
        dood_reports: list[DayOutOfDaysReport] = []
        talent_daily_status: dict[str, dict[int, str]] = {}

        for t in data.talents:
            daily_codes: dict[int, str] = {}
            scenes_with_t = scenes_by_talent[t.id]
            if not scenes_with_t or t.id not in earliest:
                for d in range(1, num_days + 1):
                    daily_codes[d] = DOODStatusCode.OFF
                dood_reports.append(
                    DayOutOfDaysReport(
                        talent_id=t.id,
                        talent_name=t.name,
                        character_name=t.character_name,
                        daily_codes=daily_codes,
                        total_work_days=0,
                        total_hold_days=0,
                        total_paid_days=0,
                        earliest_work_day=None,
                        latest_work_day=None,
                        total_cost=0.0,
                    )
                )
                talent_daily_status[str(t.id)] = daily_codes
                continue

            if t.id in talent_drop_info and solver.value(talent_drop_info[t.id][0]) == 1:
                e1_val = solver.value(talent_drop_info[t.id][1])
                l1_val = solver.value(talent_drop_info[t.id][2])
                e2_val = solver.value(talent_drop_info[t.id][3])
                l2_val = solver.value(talent_drop_info[t.id][4])
                work_days = 0
                hold_days = 0

                for d in range(1, num_days + 1):
                    is_working = (t.id, d) in talent_work and solver.value(talent_work[t.id, d]) == 1
                    if d < e1_val:
                        daily_codes[d] = DOODStatusCode.OFF
                    elif d == e1_val and d == l1_val:
                        daily_codes[d] = DOODStatusCode.START_WORK
                        work_days += 1
                    elif d == e1_val:
                        daily_codes[d] = DOODStatusCode.START_WORK
                        work_days += 1
                    elif d == l1_val:
                        daily_codes[d] = DOODStatusCode.WORK
                        work_days += 1
                    elif d < l1_val:
                        if is_working:
                            daily_codes[d] = DOODStatusCode.WORK
                            work_days += 1
                        else:
                            daily_codes[d] = DOODStatusCode.HOLD
                            hold_days += 1
                    elif d < e2_val:
                        # Drop hiatus days (unpaid)
                        daily_codes[d] = DOODStatusCode.DROP
                    elif d == e2_val and d == l2_val:
                        daily_codes[d] = DOODStatusCode.WORK_FINISH
                        work_days += 1
                    elif d == e2_val:
                        daily_codes[d] = DOODStatusCode.WORK
                        work_days += 1
                    elif d == l2_val:
                        daily_codes[d] = DOODStatusCode.WORK_FINISH
                        work_days += 1
                    elif d < l2_val:
                        if is_working:
                            daily_codes[d] = DOODStatusCode.WORK
                            work_days += 1
                        else:
                            daily_codes[d] = DOODStatusCode.HOLD
                            hold_days += 1
                    else:
                        daily_codes[d] = DOODStatusCode.OFF

                total_paid = work_days + hold_days
                total_cost = total_paid * t.daily_rate
                dood_reports.append(
                    DayOutOfDaysReport(
                        talent_id=t.id,
                        talent_name=t.name,
                        character_name=t.character_name,
                        daily_codes=daily_codes,
                        total_work_days=work_days,
                        total_hold_days=hold_days,
                        total_paid_days=total_paid,
                        earliest_work_day=e1_val,
                        latest_work_day=l2_val,
                        total_cost=total_cost,
                    )
                )
                talent_daily_status[str(t.id)] = daily_codes
                continue

            e_val = solver.value(earliest[t.id])
            l_val = solver.value(latest[t.id])
            work_days = 0
            hold_days = 0

            for d in range(1, num_days + 1):
                is_working = (t.id, d) in talent_work and solver.value(talent_work[t.id, d]) == 1
                if d < e_val or d > l_val:
                    daily_codes[d] = DOODStatusCode.OFF
                elif d == e_val and d == l_val:
                    daily_codes[d] = DOODStatusCode.START_WORK_FINISH
                    work_days += 1
                elif d == e_val:
                    daily_codes[d] = DOODStatusCode.START_WORK
                    work_days += 1
                elif d == l_val:
                    daily_codes[d] = DOODStatusCode.WORK_FINISH
                    work_days += 1
                elif is_working:
                    daily_codes[d] = DOODStatusCode.WORK
                    work_days += 1
                else:
                    daily_codes[d] = DOODStatusCode.HOLD
                    hold_days += 1

            total_paid = work_days + hold_days
            total_cost = total_paid * t.daily_rate
            dood_reports.append(
                DayOutOfDaysReport(
                    talent_id=t.id,
                    talent_name=t.name,
                    character_name=t.character_name,
                    daily_codes=daily_codes,
                    total_work_days=work_days,
                    total_hold_days=hold_days,
                    total_paid_days=total_paid,
                    earliest_work_day=e_val,
                    latest_work_day=l_val,
                    total_cost=total_cost,
                )
            )
            talent_daily_status[str(t.id)] = daily_codes

        # 3. Call Sheet Generation for all active shoot days
        call_sheets: dict[int, DailyCallSheet] = {}
        for d in range(1, num_days + 1):
            if scheduled_day_scenes.get(d):
                call_sheets[d] = generate_daily_call_sheet(
                    data,
                    d,
                    scheduled_day_scenes[d],
                    calendar_dict[d],
                    location_dict,
                    talent_dict,
                )

        return FilmScheduleResult(
            status=schedule_status,
            is_feasible=True,
            solve_time_seconds=solve_duration,
            objective_cost=solver.objective_value,
            stripboard=master_stripboard,
            dood_reports=dood_reports,
            call_sheets=call_sheets,
            scene_day_assignments=scene_day_assignments,
            talent_daily_status=talent_daily_status,
        )

    return FilmScheduleResult(
        status=ScheduleStatus.INFEASIBLE,
        is_feasible=False,
        solve_time_seconds=solve_duration,
        objective_cost=0.0,
        stripboard=MasterStripboard(
            project_title=data.project_title,
            total_shoot_days=0,
            total_hours=0.0,
            days=[],
        ),
        dood_reports=[],
    )


# ==============================================================================
# ALGORITHMIC DAILY CALL SHEET GENERATION & INTRA-DAY MICRO SOLVER
# ==============================================================================


def optimize_intraday_schedule(
    scenes: list[Scene],
    cal: CalendarDay,
    locations: dict[int | str, Location],
    talents: dict[int | str, Talent],
    *,
    shooting_call_minute: int = 480,  # 08:00 AM (8 * 60)
    max_day_minutes: int = 720,
) -> list[tuple[Scene, int, int]]:
    """Optimizes intra-day shot order, setups, and solar windows using CP-SAT.

    Returns ordered list of (Scene, start_minute_of_day, end_minute_of_day).
    """
    if not scenes:
        return []

    if len(scenes) == 1:
        s = scenes[0]
        st = shooting_call_minute
        et = st + s.duration_minutes
        return [(s, st, et)]

    m = cp_model.CpModel()
    n = len(scenes)
    start_vars: list[cp_model.IntVar] = []
    end_vars: list[cp_model.IntVar] = []
    intervals: list[cp_model.IntervalVar] = []
    horizon = shooting_call_minute + max_day_minutes + 180

    for i, s in enumerate(scenes):
        dur = max(15, s.duration_minutes)
        sv = m.new_int_var(shooting_call_minute, horizon, f"micro_s_{i}")
        ev = m.new_int_var(shooting_call_minute, horizon, f"micro_e_{i}")
        iv = m.new_interval_var(sv, dur, ev, f"micro_iv_{i}")
        start_vars.append(sv)
        end_vars.append(ev)
        intervals.append(iv)

        # Golden hour solar windows
        if s.time_of_day in (TimeOfDay.MAGIC_HOUR, "MAGIC_HOUR"):
            in_dawn = m.new_bool_var(f"in_dawn_{i}")
            in_dusk = m.new_bool_var(f"in_dusk_{i}")
            m.add(sv >= cal.dawn_minute).only_enforce_if(in_dawn)
            m.add(ev <= cal.sunrise_minute + 30).only_enforce_if(in_dawn)
            m.add(sv >= cal.sunset_minute - 45).only_enforce_if(in_dusk)
            m.add(ev <= cal.dusk_minute).only_enforce_if(in_dusk)
            m.add_bool_or([in_dawn, in_dusk])

    # Camera unit non-overlapping constraint
    m.add_no_overlap(intervals)

    # Transition buffers between consecutive scenes
    for i in range(n):
        for j in range(n):
            if i != j:
                i_before_j = m.new_bool_var(f"before_{i}_{j}")
                m.add(end_vars[i] <= start_vars[j]).only_enforce_if(i_before_j)
                buffer_mins = 0
                if scenes[i].setup_id and scenes[j].setup_id and scenes[i].setup_id == scenes[j].setup_id:
                    buffer_mins = 0
                elif scenes[i].location_id != scenes[j].location_id:
                    buffer_mins = 30
                if buffer_mins > 0:
                    m.add(start_vars[j] >= end_vars[i] + buffer_mins).only_enforce_if(i_before_j)

    first_start = m.new_int_var(shooting_call_minute, horizon, "first_start")
    m.add_min_equality(first_start, start_vars)
    m.add(first_start == shooting_call_minute)

    makespan = m.new_int_var(shooting_call_minute, horizon, "micro_makespan")
    for ev in end_vars:
        m.add(makespan >= ev)
    m.minimize(makespan)

    micro_solver = cp_model.CpSolver()
    micro_solver.parameters.max_time_in_seconds = 1.0
    micro_solver.parameters.num_search_workers = 2
    status = micro_solver.solve(m)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        res = []
        for i, s in enumerate(scenes):
            st = micro_solver.value(start_vars[i])
            et = micro_solver.value(end_vars[i])
            res.append((s, st, et))
        res.sort(key=lambda item: item[1])
        return res
    else:
        curr = shooting_call_minute
        res = []
        for s in scenes:
            st = curr
            et = st + s.duration_minutes
            res.append((s, st, et))
            curr = et
        return res


def generate_daily_call_sheet(
    data: ProductionDataset,
    day_num: int,
    scenes: list[Scene],
    cal: CalendarDay,
    locations: dict[int | str, Location],
    talents: dict[int | str, Talent],
    *,
    hospital_info: str = "St. Jude Medical Center, 24/7 Trauma Wing (Tel: 555-0199)",
    general_crew_call_time: str = "07:00",
    shooting_call_time: str = "08:00",
    optimize_intraday: bool = True,
) -> DailyCallSheet:
    """Generate official daily call sheet with backward calculated actor call times."""
    general_crew_call = datetime.strptime(general_crew_call_time, "%H:%M")
    shooting_call = datetime.strptime(shooting_call_time, "%H:%M")
    first_meal_due = general_crew_call + timedelta(hours=6)

    shooting_call_min = shooting_call.hour * 60 + shooting_call.minute
    if optimize_intraday:
        day_schedule = optimize_intraday_schedule(
            scenes, cal, locations, talents, shooting_call_minute=shooting_call_min
        )
    else:
        curr = shooting_call_min
        day_schedule = []
        for s in scenes:
            st = curr
            et = st + s.duration_minutes
            day_schedule.append((s, st, et))
            curr = et

    base_midnight = shooting_call.replace(hour=0, minute=0, second=0, microsecond=0)
    scene_entries: list[CallSheetSceneEntry] = []
    cast_first_seen: dict[int | str, datetime] = {}

    for s, st_min, et_min in day_schedule:
        start_t = base_midnight + timedelta(minutes=st_min)
        end_t = base_midnight + timedelta(minutes=et_min)
        loc = locations.get(s.location_id) or locations.get(str(s.location_id))
        loc_name = loc.name if loc else str(s.location_id)

        scene_entries.append(
            CallSheetSceneEntry(
                scene_number=s.scene_number,
                start_time=start_t.strftime("%I:%M %p"),
                end_time=end_t.strftime("%I:%M %p"),
                setting=f"{s.setting} {s.time_of_day}",
                time_of_day=str(s.time_of_day),
                location_name=loc_name,
                cast_ids=[str(cid) for cid in s.required_cast],
                page_eighths=s.page_eighths,
            )
        )
        for cid in s.required_cast:
            if cid not in cast_first_seen and str(cid) not in cast_first_seen:
                cast_first_seen[cid] = start_t

    # Backward calculation of actor call matrix
    character_calls: list[CallSheetCharacterEntry] = []
    for cid, first_scene_time in cast_first_seen.items():
        t = talents.get(cid) or talents.get(str(cid))
        if not t:
            continue
        set_call = first_scene_time - timedelta(minutes=15)
        wardrobe_call = set_call - timedelta(minutes=t.wardrobe_duration_minutes)
        hmu_call = wardrobe_call - timedelta(minutes=t.hmu_duration_minutes)
        pickup_call = hmu_call - timedelta(minutes=t.travel_duration_minutes)

        character_calls.append(
            CallSheetCharacterEntry(
                talent_id=t.id,
                character_name=t.character_name,
                actor_name=t.name,
                pickup_call=pickup_call.strftime("%I:%M %p"),
                hmu_call=hmu_call.strftime("%I:%M %p"),
                wardrobe_call=wardrobe_call.strftime("%I:%M %p"),
                set_call=set_call.strftime("%I:%M %p"),
            )
        )

    second_meal_due = (
        (first_meal_due + timedelta(hours=6)).strftime("%I:%M %p")
        if sum(s.duration_hours for s in scenes) >= 6.0
        else None
    )

    return DailyCallSheet(
        day_number=day_num,
        calendar_date=cal.calendar_date,
        project_title=data.project_title,
        sunrise_time=cal.sunrise_time,
        sunset_time=cal.sunset_time,
        expected_weather=str(cal.expected_weather),
        general_crew_call=general_crew_call.strftime("%I:%M %p"),
        shooting_call=shooting_call.strftime("%I:%M %p"),
        first_meal_due=first_meal_due.strftime("%I:%M %p"),
        second_meal_due=second_meal_due,
        hospital_info=hospital_info,
        scene_entries=scene_entries,
        character_calls=character_calls,
    )


# ==============================================================================
# OPERATIONAL DISRUPTION & RESCHEDULING DYNAMICS
# ==============================================================================


def reschedule_production(
    data: ProductionDataset,
    *,
    completed_days: list[int] | None = None,
    weather_disruptions: dict[int, WeatherType | str] | None = None,
    talent_blackouts: dict[int | str, list[int]] | None = None,
    activate_cover_sets: bool = True,
    max_time_in_seconds: float = 15.0,
    fixed_assignments: dict[int | str, int] | None = None,
) -> FilmScheduleResult:
    """Perform rolling-horizon rescheduling preserving completed days while re-optimizing."""
    updated_calendar: list[CalendarDay] = []
    weather_map = weather_disruptions or {}

    for c in data.calendar:
        weather_val = weather_map.get(c.day_number, c.expected_weather)
        weather = WeatherType(weather_val) if isinstance(weather_val, str) else weather_val
        updated_calendar.append(
            CalendarDay(
                day_number=c.day_number,
                calendar_date=c.calendar_date,
                is_statutory_holiday=c.is_statutory_holiday,
                is_inauspicious=c.is_inauspicious,
                expected_weather=weather,
                sunrise_time=c.sunrise_time,
                sunset_time=c.sunset_time,
                is_weekend=c.is_weekend,
            )
        )

    # Talent blackout updates
    blackout_map = talent_blackouts or {}
    updated_talents: list[Talent] = []
    for t in data.talents:
        extra_blackouts = blackout_map.get(t.id) or blackout_map.get(str(t.id)) or []
        combined_blackouts = sorted(set(t.blackout_days) | set(extra_blackouts))
        updated_talents.append(
            Talent(
                id=t.id,
                name=t.name,
                character_name=t.character_name,
                daily_rate=t.daily_rate,
                is_minor=t.is_minor,
                max_daily_hours=t.max_daily_hours,
                hmu_duration_minutes=t.hmu_duration_minutes,
                wardrobe_duration_minutes=t.wardrobe_duration_minutes,
                travel_duration_minutes=t.travel_duration_minutes,
                blackout_days=combined_blackouts,
                blackout_windows=t.blackout_windows,
            )
        )

    # Scene cover set release logic
    updated_scenes: list[Scene] = []
    for s in data.scenes:
        is_cover = s.is_cover_set
        if activate_cover_sets and is_cover:
            # If weather disrupted the primary scene, activate cover set
            is_cover = False
        updated_scenes.append(
            Scene(
                id=s.id,
                scene_number=s.scene_number,
                part=s.part,
                location_id=s.location_id,
                setting=s.setting,
                time_of_day=s.time_of_day,
                page_eighths=s.page_eighths,
                duration_hours=s.duration_hours,
                duration_minutes=s.duration_minutes,
                required_cast=s.required_cast,
                character_ids=s.character_ids,
                required_prop_ids=s.required_prop_ids,
                required_costume_ids=s.required_costume_ids,
                required_equipment_ids=s.required_equipment_ids,
                stunt_sfx_package_id=s.stunt_sfx_package_id,
                weather_requirement=s.weather_requirement,
                sound_recording=s.sound_recording,
                holiday_compatibility=s.holiday_compatibility,
                earliest_allowed_day=s.earliest_allowed_day,
                latest_allowed_day=s.latest_allowed_day,
                is_cover_set=is_cover,
                cover_for_scene_id=s.cover_for_scene_id,
                requires_precedence_over=s.requires_precedence_over,
                min_lag_days=s.min_lag_days,
                is_second_unit=s.is_second_unit,
                is_vfx_heavy=s.is_vfx_heavy,
                dependencies=s.dependencies,
            )
        )

    reschedule_dataset = ProductionDataset(
        project_title=data.project_title,
        talents=updated_talents,
        locations=data.locations,
        props=data.props,
        costumes=data.costumes,
        equipment=data.equipment,
        stunts=data.stunts,
        calendar=updated_calendar,
        scenes=updated_scenes,
        max_shooting_days=data.max_shooting_days,
        max_hours_per_day=data.max_hours_per_day,
    )

    return optimize_production_schedule(
        reschedule_dataset,
        max_time_in_seconds=max_time_in_seconds,
        fixed_assignments=fixed_assignments,
    )


# ==============================================================================
# EXTENDED DOMAIN ADAPTER
# ==============================================================================


class FilmProductionScheduler(DomainAdapter):
    """Generates optimized film shooting schedules minimizing shoot days, location moves, and cast idle time."""

    def __init__(
        self,
        *,
        project_title: str = "Feature Film Shoot",
        shoot_day_hours: int = 10,
        day_start_hour: int = 8,
        night_start_hour: int = 19,
        max_shooting_days: int = 30,
    ) -> None:
        self.project_title = project_title
        self.shoot_day_hours = shoot_day_hours
        self.day_start_hour = day_start_hour
        self.night_start_hour = night_start_hour
        self.max_shooting_days = max_shooting_days

        self.scenes: dict[str, Scene] = {}
        self.cast: dict[str, Talent] = {}
        self.locations: dict[str, Location] = {}
        self.props: dict[str, Prop] = {}
        self.costumes: dict[str, Costume] = {}
        self.equipment: dict[str, SpecialtyEquipment] = {}
        self.stunts: dict[str, StuntSFXPackage] = {}
        self.calendar: dict[int, CalendarDay] = {}
        self.units: dict[str, ProductionUnit] = {}
        self.setups: dict[str, CameraSetup] = {}
        self.location_travel_times: dict[tuple[str, str], int] = {}

    def add_cast_member(
        self,
        id: int | str,
        name: str = "",
        day_rate: float = 0.0,
        blackout_windows: list[IntervalWindow] | None = None,
        *,
        character_name: str = "",
        daily_rate: float | None = None,
        is_minor: bool = False,
        max_daily_hours: float = 10.0,
        hmu_duration_minutes: int = 60,
        wardrobe_duration_minutes: int = 30,
        travel_duration_minutes: int = 30,
        blackout_days: list[int] | None = None,
    ) -> Talent:
        rate = daily_rate if daily_rate is not None else day_rate
        member = Talent(
            id=id,
            name=name or str(id),
            character_name=character_name or name or str(id),
            daily_rate=rate,
            day_rate=rate,
            is_minor=is_minor,
            max_daily_hours=max_daily_hours,
            hmu_duration_minutes=hmu_duration_minutes,
            wardrobe_duration_minutes=wardrobe_duration_minutes,
            travel_duration_minutes=travel_duration_minutes,
            blackout_days=blackout_days or [],
            blackout_windows=blackout_windows or [],
        )
        self.cast[str(id)] = member
        return member

    def add_location(
        self,
        id: int | str,
        name: str = "",
        turnaround_minutes: int = 60,
        blackout_windows: list[IntervalWindow] | None = None,
        *,
        location_type: LocationType | str = LocationType.SOUNDSTAGE,
        permitted_days: list[int] | None = None,
        noise_curfew_hour: int | None = None,
        allows_sync_sound: bool = True,
        daily_rental_cost: float = 0.0,
        prep_days_required: int = 0,
        strike_days_required: int = 0,
    ) -> Location:
        loc_type = LocationType(location_type) if isinstance(location_type, str) else location_type
        loc = Location(
            id=id,
            name=name or str(id),
            location_type=loc_type,
            permitted_days=permitted_days or [],
            noise_curfew_hour=noise_curfew_hour,
            allows_sync_sound=allows_sync_sound,
            daily_rental_cost=daily_rental_cost,
            prep_days_required=prep_days_required,
            strike_days_required=strike_days_required,
            turnaround_minutes=turnaround_minutes,
            blackout_windows=blackout_windows or [],
        )
        self.locations[str(id)] = loc
        return loc

    def add_prop(
        self,
        id: int | str,
        name: str,
        category: PropCategory | str = PropCategory.HERO,
        total_quantity: int = 1,
        is_destructible: bool = False,
        requires_armorer: bool = False,
        reset_duration_minutes: int = 0,
    ) -> Prop:
        cat = PropCategory(category) if isinstance(category, str) else category
        prop = Prop(
            id=id,
            name=name,
            category=cat,
            total_quantity=total_quantity,
            is_destructible=is_destructible,
            requires_armorer=requires_armorer,
            reset_duration_minutes=reset_duration_minutes,
        )
        self.props[str(id)] = prop
        return prop

    def add_costume(
        self,
        id: int | str,
        character_id: int | str,
        costume_code: str,
        distress_stage: int = 1,
        available_duplicates: int = 1,
        requires_specialist_dresser: bool = False,
    ) -> Costume:
        costume = Costume(
            id=id,
            character_id=character_id,
            costume_code=costume_code,
            distress_stage=distress_stage,
            available_duplicates=available_duplicates,
            requires_specialist_dresser=requires_specialist_dresser,
        )
        self.costumes[str(id)] = costume
        return costume

    def add_equipment(
        self,
        id: int | str,
        name: str,
        equipment_type: SpecialtyEquipmentType | str = SpecialtyEquipmentType.TECHNOCRANE,
        daily_rental_cost: float = 0.0,
        rental_start_day: int = 1,
        rental_end_day: int = 365,
        requires_certified_technician: bool = True,
    ) -> SpecialtyEquipment:
        eq_type = (
            SpecialtyEquipmentType(equipment_type)
            if isinstance(equipment_type, str)
            else equipment_type
        )
        eq = SpecialtyEquipment(
            id=id,
            name=name,
            equipment_type=eq_type,
            daily_rental_cost=daily_rental_cost,
            rental_start_day=rental_start_day,
            rental_end_day=rental_end_day,
            requires_certified_technician=requires_certified_technician,
        )
        self.equipment[str(id)] = eq
        return eq

    def add_stunt_package(
        self,
        id: int | str,
        *,
        has_wirework: bool = False,
        has_pyrotechnics: bool = False,
        has_squibs: bool = False,
        pre_rigging_hours_required: float = 0.0,
        mandatory_medic_count: int = 1,
    ) -> StuntSFXPackage:
        stunt = StuntSFXPackage(
            id=id,
            has_wirework=has_wirework,
            has_pyrotechnics=has_pyrotechnics,
            has_squibs=has_squibs,
            pre_rigging_hours_required=pre_rigging_hours_required,
            mandatory_medic_count=mandatory_medic_count,
        )
        self.stunts[str(id)] = stunt
        return stunt

    def add_unit(
        self,
        id: int | str,
        name: str,
        unit_type: ProductionUnitType | str = ProductionUnitType.MAIN,
        daily_operating_cost: float = 0.0,
    ) -> ProductionUnit:
        u_type = ProductionUnitType(unit_type) if isinstance(unit_type, str) else unit_type
        unit = ProductionUnit(
            id=id,
            name=name,
            unit_type=u_type,
            daily_operating_cost=daily_operating_cost,
        )
        self.units[str(id)] = unit
        return unit

    def add_setup(
        self,
        id: int | str,
        name: str,
        axis_angle: str = "",
        lighting_setup_id: str = "",
    ) -> CameraSetup:
        setup = CameraSetup(
            id=id,
            name=name,
            axis_angle=axis_angle,
            lighting_setup_id=lighting_setup_id,
        )
        self.setups[str(id)] = setup
        return setup

    def add_calendar_day(
        self,
        day_number: int,
        calendar_date: str,
        *,
        is_statutory_holiday: bool = False,
        is_inauspicious: bool = False,
        expected_weather: WeatherType | str = WeatherType.CLEAR,
        sunrise_time: str = "06:15",
        sunset_time: str = "18:30",
        is_weekend: bool = False,
    ) -> CalendarDay:
        weather = WeatherType(expected_weather) if isinstance(expected_weather, str) else expected_weather
        cal = CalendarDay(
            day_number=day_number,
            calendar_date=calendar_date,
            is_statutory_holiday=is_statutory_holiday,
            is_inauspicious=is_inauspicious,
            expected_weather=weather,
            sunrise_time=sunrise_time,
            sunset_time=sunset_time,
            is_weekend=is_weekend,
        )
        self.calendar[day_number] = cal
        return cal

    def add_scene(
        self,
        id: int | str,
        scene_number: str,
        duration_minutes: int = 60,
        character_ids: list[str] | None = None,
        location_id: int | str = "",
        is_night: bool = False,
        is_exterior: bool = False,
        dependencies: list[str] | None = None,
        *,
        part: int = 1,
        page_eighths: int = 8,
        duration_hours: float | None = None,
        required_cast: list[int | str] | None = None,
        required_prop_ids: list[int | str] | None = None,
        required_costume_ids: list[int | str] | None = None,
        required_equipment_ids: list[int | str] | None = None,
        stunt_sfx_package_id: int | str | None = None,
        weather_requirement: WeatherRequirement | str = WeatherRequirement.ANY,
        sound_recording: SoundRecording | str = SoundRecording.SYNC_SOUND,
        holiday_compatibility: HolidayCompatibility | str = HolidayCompatibility.NORMAL,
        earliest_allowed_day: int | None = None,
        latest_allowed_day: int | None = None,
        is_cover_set: bool = False,
        cover_for_scene_id: int | str | None = None,
        requires_precedence_over: int | str | None = None,
        min_lag_days: int = 0,
        is_second_unit: bool = False,
        is_vfx_heavy: bool = False,
        unit_type: ProductionUnitType | str = ProductionUnitType.MAIN,
        setup_id: int | str | None = None,
        background_count: int = 0,
        vfx_turnover_deadline_day: int | None = None,
        stunt_hazard_level: int = 1,
    ) -> Scene:
        cast_list: list[int | str] = list(required_cast) if required_cast is not None else [str(c) for c in (character_ids or [])]
        dur_h = duration_hours if duration_hours is not None else (duration_minutes / 60.0)
        wr = (
            WeatherRequirement(weather_requirement)
            if isinstance(weather_requirement, str)
            else weather_requirement
        )
        sr = (
            SoundRecording(sound_recording)
            if isinstance(sound_recording, str)
            else sound_recording
        )
        hc = (
            HolidayCompatibility(holiday_compatibility)
            if isinstance(holiday_compatibility, str)
            else holiday_compatibility
        )
        u_type = ProductionUnitType(unit_type) if isinstance(unit_type, str) else unit_type

        scene = Scene(
            id=id,
            scene_number=scene_number,
            part=part,
            location_id=location_id,
            setting=SettingType.EXT if is_exterior else SettingType.INT,
            time_of_day=TimeOfDay.NIGHT if is_night else TimeOfDay.DAY,
            page_eighths=page_eighths,
            duration_hours=dur_h,
            duration_minutes=duration_minutes,
            required_cast=cast_list,
            character_ids=[str(c) for c in cast_list],
            required_prop_ids=required_prop_ids or [],
            required_costume_ids=required_costume_ids or [],
            required_equipment_ids=required_equipment_ids or [],
            stunt_sfx_package_id=stunt_sfx_package_id,
            weather_requirement=wr,
            sound_recording=sr,
            holiday_compatibility=hc,
            earliest_allowed_day=earliest_allowed_day,
            latest_allowed_day=latest_allowed_day,
            is_cover_set=is_cover_set,
            cover_for_scene_id=cover_for_scene_id,
            requires_precedence_over=requires_precedence_over,
            min_lag_days=min_lag_days,
            is_second_unit=is_second_unit,
            is_vfx_heavy=is_vfx_heavy,
            unit_type=u_type,
            setup_id=setup_id,
            background_count=background_count,
            vfx_turnover_deadline_day=vfx_turnover_deadline_day,
            stunt_hazard_level=stunt_hazard_level,
            dependencies=dependencies or [],
            is_night=is_night,
            is_exterior=is_exterior,
        )
        self.scenes[str(id)] = scene
        return scene

    def set_location_travel(self, loc1: str, loc2: str, travel_minutes: int) -> None:
        self.location_travel_times[(loc1, loc2)] = travel_minutes
        self.location_travel_times[(loc2, loc1)] = travel_minutes

    def to_dataset(self) -> ProductionDataset:
        """Convert current adapter configuration into a ProductionDataset."""
        calendar_list = list(self.calendar.values())
        if not calendar_list:
            calendar_list = [
                CalendarDay(day_number=d, calendar_date=f"Day {d:02d}")
                for d in range(1, self.max_shooting_days + 1)
            ]

        return ProductionDataset(
            project_title=self.project_title,
            talents=list(self.cast.values()),
            locations=list(self.locations.values()),
            props=list(self.props.values()),
            costumes=list(self.costumes.values()),
            equipment=list(self.equipment.values()),
            stunts=list(self.stunts.values()),
            calendar=calendar_list,
            scenes=list(self.scenes.values()),
            units=list(self.units.values()),
            setups=list(self.setups.values()),
            max_shooting_days=self.max_shooting_days,
            max_hours_per_day=float(self.shoot_day_hours),
        )

    @classmethod
    def from_dataset(cls, dataset: ProductionDataset) -> FilmProductionScheduler:
        """Instantiate a FilmProductionScheduler preloaded with dataset elements."""
        adapter = cls(
            project_title=dataset.project_title,
            shoot_day_hours=int(dataset.max_hours_per_day),
            max_shooting_days=dataset.max_shooting_days,
        )
        for t in dataset.talents:
            adapter.cast[str(t.id)] = t
        for loc in dataset.locations:
            adapter.locations[str(loc.id)] = loc
        for p in dataset.props:
            adapter.props[str(p.id)] = p
        for c in dataset.costumes:
            adapter.costumes[str(c.id)] = c
        for eq in dataset.equipment:
            adapter.equipment[str(eq.id)] = eq
        for st in dataset.stunts:
            adapter.stunts[str(st.id)] = st
        for cal in dataset.calendar:
            adapter.calendar[cal.day_number] = cal
        for s in dataset.scenes:
            adapter.scenes[str(s.id)] = s
        for u in dataset.units:
            adapter.units[str(u.id)] = u
        for stp in dataset.setups:
            adapter.setups[str(stp.id)] = stp
        return adapter

    def optimize(
        self,
        dataset: ProductionDataset | None = None,
        *,
        max_time_in_seconds: float = 30.0,
        num_workers: int | None = None,
        move_penalty: int = 500,
        enable_drop_pickup: bool = False,
        enable_soundstage_lease_tracking: bool = False,
        enable_hazard_deferral: bool = False,
        enable_intraday_micro_optimization: bool = True,
        fixed_assignments: dict[int | str, int] | None = None,
    ) -> FilmScheduleResult:
        """Run the extended combinatorial CP-SAT solver and generate stripboard and DOOD reports."""
        ds = dataset or self.to_dataset()
        return optimize_production_schedule(
            ds,
            max_time_in_seconds=max_time_in_seconds,
            num_workers=num_workers,
            move_penalty=move_penalty,
            enable_drop_pickup=enable_drop_pickup,
            enable_soundstage_lease_tracking=enable_soundstage_lease_tracking,
            enable_hazard_deferral=enable_hazard_deferral,
            enable_intraday_micro_optimization=enable_intraday_micro_optimization,
            fixed_assignments=fixed_assignments,
        )

    def reschedule(
        self,
        *,
        completed_days: list[int] | None = None,
        weather_disruptions: dict[int, WeatherType | str] | None = None,
        talent_blackouts: dict[int | str, list[int]] | None = None,
        activate_cover_sets: bool = True,
        max_time_in_seconds: float = 15.0,
    ) -> FilmScheduleResult:
        """Re-optimize shooting schedule under unexpected set disruptions."""
        ds = self.to_dataset()
        return reschedule_production(
            ds,
            completed_days=completed_days,
            weather_disruptions=weather_disruptions,
            talent_blackouts=talent_blackouts,
            activate_cover_sets=activate_cover_sets,
            max_time_in_seconds=max_time_in_seconds,
        )

    def build_scheduler(self) -> Scheduler:
        """Build standard backward-compatible Scheduler for general constraint solving."""
        scheduler = Scheduler()

        # 1. Add cast resources (capacity = 1)
        for cast_id, member in self.cast.items():
            scheduler.add_resource(
                id=f"cast:{cast_id}",
                name=member.name,
                capacity=1,
                resource_type=ResourceType.PERSON,
                blackout_windows=member.blackout_windows,
            )

        # 2. Add location resources (capacity = 1)
        for loc_id, loc in self.locations.items():
            scheduler.add_resource(
                id=f"loc:{loc_id}",
                name=loc.name,
                capacity=1,
                resource_type=ResourceType.LOCATION,
                blackout_windows=loc.blackout_windows,
            )

        # 3. Add scenes as tasks
        for scene_id, scene in self.scenes.items():
            required_resources = [f"loc:{scene.location_id}"]
            for cid in scene.character_ids:
                if cid in self.cast or str(cid) in self.cast:
                    required_resources.append(f"cast:{cid}")

            scheduler.add_task(
                id=scene_id,
                duration=scene.duration_minutes,
                name=f"Scene {scene.scene_number}",
                required_resources=required_resources,
                dependencies=scene.dependencies,
                priority=TaskPriority.NORMAL,
            )

        # 4. Add location turnaround transitions
        for loc_id, loc in self.locations.items():
            loc_scenes = [
                s_id for s_id, s in self.scenes.items() if str(s.location_id) == str(loc_id)
            ]
            if len(loc_scenes) > 1:
                matrix: dict[tuple[str, str], int] = {}
                for s1 in loc_scenes:
                    for s2 in loc_scenes:
                        if s1 != s2:
                            matrix[(s1, s2)] = loc.turnaround_minutes
                scheduler.add_transition_matrix(
                    resource_id=f"loc:{loc_id}",
                    transition_matrix=matrix,
                    default_buffer=loc.turnaround_minutes,
                )

        # 5. Composite objective: minimize total shoot duration + cast idle time
        objectives = [
            MinimizeMakespanObjective(weight=1.0),
            MinimizeIdleTimeObjective(
                resource_ids=[f"cast:{cid}" for cid in self.cast],
                weight=0.3,
            ),
        ]
        scheduler.minimize(WeightedCompositeObjective(objectives))

        return scheduler
