"""Calendar provider interval and blackout calculation schemas."""

from typing import Any

import msgspec


class CulturalIntervalsRequest(msgspec.Struct, kw_only=True):
    """Request payload to compute Vedic/cultural astrological intervals."""

    horizon_days: int = 7
    day_minutes: int = 1440
    enable_rahu_kalam: bool = True
    enable_yamagandam: bool = True


class CulturalIntervalsResponse(msgspec.Struct, kw_only=True):
    """Response containing computed blackout windows and auspicious muhurats."""

    horizon_days: int
    blackout_windows: list[dict[str, Any]]
    auspicious_windows: list[dict[str, Any]]


class StandardBlackoutsRequest(msgspec.Struct, kw_only=True):
    """Request payload to generate operational blackout intervals."""

    horizon_days: int = 7
    working_day_start_minute: int = 480  # 08:00
    working_day_end_minute: int = 1020  # 17:00
    weekend_days: list[int] = msgspec.field(default_factory=lambda: [5, 6])


class StandardBlackoutsResponse(msgspec.Struct, kw_only=True):
    """Response containing standard non-working blackout intervals."""

    blackout_windows: list[dict[str, Any]]
