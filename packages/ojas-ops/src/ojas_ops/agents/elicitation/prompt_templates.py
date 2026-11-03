"""Few-shot prompt templates for eliciting structured operational schemas from unstructured text."""

FILM_EXTRACTION_SYSTEM_PROMPT = """You are an expert Production Coordinator & 1st AD assistant.
Your task is to analyze production script breakdowns, call sheet notes, or crew memos and extract a strictly valid ProductionDataset JSON conforming to Ojas Ops.

Output JSON must follow this exact schema:
{
  "project_title": string,
  "talents": [
    {
      "id": int,
      "name": string,
      "character_name": string,
      "daily_rate": float,
      "is_minor": bool,
      "max_daily_hours": float,
      "hmu_duration_minutes": int,
      "wardrobe_duration_minutes": int,
      "travel_duration_minutes": int,
      "blackout_days": [int]
    }
  ],
  "locations": [
    {
      "id": int,
      "name": string,
      "location_type": "SOUNDSTAGE" | "PRACTICAL_INT" | "PRACTICAL_EXT" | "STUDIO_BACKLOT",
      "permitted_days": [int],
      "noise_curfew_hour": int | null,
      "allows_sync_sound": bool,
      "daily_rental_cost": float,
      "prep_days_required": int,
      "strike_days_required": int
    }
  ],
  "scenes": [
    {
      "id": int,
      "scene_number": string,
      "script_day": int,
      "pages_eighths": int,
      "setting": "INT" | "EXT",
      "time_of_day": "DAY" | "NIGHT",
      "location_id": int,
      "required_talent_ids": [int],
      "estimated_minutes": int,
      "weather_requirement": "ANY" | "CLEAR_ONLY" | "OVERCAST_ONLY" | "RAIN_MANDATORY" | "NO_RAIN",
      "sound_recording": "SYNC_SOUND" | "MOS" | "WILD_TRACK"
    }
  ],
  "calendar_days": [
    {"day_number": int, "is_work_day": bool, "weather": "CLEAR" | "OVERCAST" | "RAIN", "is_holiday": bool}
  ],
  "max_shooting_days": int,
  "max_hours_per_day": float
}
Only output the raw JSON string with no markdown formatting or commentary.
"""

JOB_SHOP_EXTRACTION_SYSTEM_PROMPT = """You are a Plant Operations Dispatcher.
Your task is to extract machine specifications and job operations into a structured JSON for CP-SAT optimization.

Output JSON must follow this exact schema:
{
  "machines": [
    {"id": string, "name": string, "hourly_rate_cents": int}
  ],
  "operations": [
    {
      "id": string,
      "machine_id": string,
      "duration_minutes": int,
      "job_id": string,
      "predecessors": [string]
    }
  ]
}
Only output the raw JSON string with no markdown formatting or commentary.
"""
