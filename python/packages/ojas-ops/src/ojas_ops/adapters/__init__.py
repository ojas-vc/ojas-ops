"""Domain adapters and industry use-case scheduling models."""

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from ojas_ops.adapters.academic import AcademicTimetableScheduler
from ojas_ops.adapters.base import DomainAdapter
from ojas_ops.adapters.event_run_sheets import EventRunSheetScheduler
from ojas_ops.adapters.film_production import (
    CalendarDay,
    CallSheetCharacterEntry,
    CallSheetSceneEntry,
    CastMember,
    Costume,
    DailyCallSheet,
    DayOutOfDaysReport,
    DOODStatusCode,
    FilmProductionScheduler,
    FilmScheduleResult,
    HolidayCompatibility,
    Location,
    LocationType,
    MasterStripboard,
    ProductionDataset,
    Prop,
    PropCategory,
    Scene,
    SettingType,
    ShootingLocation,
    SoundRecording,
    SpecialtyEquipment,
    SpecialtyEquipmentType,
    StripboardDay,
    StripboardStrip,
    StuntSFXPackage,
    Talent,
    TimeOfDay,
    WeatherRequirement,
    WeatherType,
    generate_daily_call_sheet,
    optimize_production_schedule,
    reschedule_production,
)
from ojas_ops.adapters.manufacturing import ManufacturingScheduler
from ojas_ops.adapters.marketing_flighting import MarketingFlightingScheduler
from ojas_ops.adapters.workforce import WorkforceScheduler

__all__ = [
    "AcademicTimetableScheduler",
    "CalendarDay",
    "CallSheetCharacterEntry",
    "CallSheetSceneEntry",
    "CastMember",
    "Costume",
    "DOODStatusCode",
    "DailyCallSheet",
    "DayOutOfDaysReport",
    "DomainAdapter",
    "EventRunSheetScheduler",
    "FilmProductionScheduler",
    "FilmScheduleResult",
    "HolidayCompatibility",
    "Location",
    "LocationType",
    "ManufacturingScheduler",
    "MarketingFlightingScheduler",
    "MasterStripboard",
    "ProductionDataset",
    "Prop",
    "PropCategory",
    "Scene",
    "SettingType",
    "ShootingLocation",
    "SoundRecording",
    "SpecialtyEquipment",
    "SpecialtyEquipmentType",
    "StripboardDay",
    "StripboardStrip",
    "StuntSFXPackage",
    "Talent",
    "TimeOfDay",
    "WeatherRequirement",
    "WeatherType",
    "WorkforceScheduler",
    "generate_daily_call_sheet",
    "optimize_production_schedule",
    "reschedule_production",
]
