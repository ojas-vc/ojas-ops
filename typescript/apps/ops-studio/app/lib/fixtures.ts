import type {
  AcademicOptimizeRequest,
  CulturalIntervalsRequest,
  DOODRenderRequest,
  EventsOptimizeRequest,
  GanttRenderRequest,
  ManufacturingOptimizeRequest,
  MarketingOptimizeRequest,
  OptimizeScheduleRequest,
  ProductionDataset,
  RescheduleRequest,
  ScenarioDefinition,
  SimulateDisruptionRequest,
  StandardBlackoutsRequest,
  StripboardRenderRequest,
  ValidateScheduleRequest,
  WorkforceOptimizeRequest,
} from "@ojas-ops/sdk";

export const SAMPLE_SCHEDULE_PAYLOAD: OptimizeScheduleRequest = {
  tenant_id: "org_default",
  project_id: "demo_project",
  schedule_id: "sched_demo_01",
  horizon: { start: 0, end: 1440 },
  resources: [
    {
      id: "machine_alpha",
      name: "High Precision CNC Mill",
      capacity: 1,
      cost_per_time_unit_minor: 120,
    },
    {
      id: "machine_beta",
      name: "Automated Lathe",
      capacity: 1,
      cost_per_time_unit_minor: 90,
    },
    {
      id: "assembly_station",
      name: "Final Assembly & QA",
      capacity: 2,
      cost_per_time_unit_minor: 60,
    },
  ],
  tasks: [
    {
      id: "task_roughing",
      name: "Rough Surface Milling",
      duration: 120,
      priority: 1,
      required_resources: ["machine_alpha"],
    },
    {
      id: "task_turning",
      name: "Cylindrical Turning",
      duration: 90,
      priority: 2,
      required_resources: ["machine_beta"],
    },
    {
      id: "task_finishing",
      name: "Precision Finishing",
      duration: 60,
      priority: 1,
      required_resources: ["machine_alpha"],
      dependencies: ["task_roughing"],
    },
    {
      id: "task_assembly",
      name: "Final Component Assembly",
      duration: 75,
      priority: 3,
      required_resources: ["assembly_station"],
      dependencies: ["task_finishing", "task_turning"],
    },
  ],
  strategy: "balanced",
  max_time_seconds: 5.0,
};

export const SAMPLE_VALIDATE_PAYLOAD: ValidateScheduleRequest = {
  schedule_id: "sched_demo_01",
  solution: {
    schedule_id: "sched_demo_01",
    status: "FEASIBLE",
    makespan: 285,
    tasks: {
      task_roughing: { start: 0, end: 120, assigned_resources: ["machine_alpha"] },
      task_turning: { start: 0, end: 90, assigned_resources: ["machine_beta"] },
      task_finishing: { start: 120, end: 180, assigned_resources: ["machine_alpha"] },
      task_assembly: { start: 180, end: 255, assigned_resources: ["assembly_station"] },
    },
  },
};

export const SAMPLE_SCENARIO_PAYLOAD: ScenarioDefinition = {
  metadata: {
    name: "Automated_Gearbox_Production",
    description: "Multi-stage machining benchmark with precedence constraints",
    domain: "manufacturing",
  },
  resources: [
    { id: "mill_01", name: "Vertical Mill", capacity: 1, cost_per_time_unit_minor: 6500 },
    { id: "drill_01", name: "Pneumatic Drill", capacity: 1, cost_per_time_unit_minor: 4200 },
  ],
  tasks: [
    {
      id: "op_cast_cut",
      name: "Cast Cut",
      duration: 45,
      required_resources: ["mill_01"],
    },
    {
      id: "op_bore_holes",
      name: "Bore Holes",
      duration: 30,
      required_resources: ["drill_01"],
      dependencies: ["op_cast_cut"],
    },
  ],
  golden_expected: {
    status: "OPTIMAL",
    max_makespan: 120,
  },
};

export const SAMPLE_SIMULATION_PAYLOAD: SimulateDisruptionRequest = {
  tenant_id: "org_default",
  schedule_id: "sched_run_alpha_01",
  baseline_schedule: {
    status: "optimal",
    makespan: 180,
    tasks: {
      task_roughing: {
        task_id: "task_roughing",
        start: 0,
        end: 120,
        duration: 120,
        assigned_resources: ["machine_alpha"],
      },
      task_finishing: {
        task_id: "task_finishing",
        start: 120,
        end: 180,
        duration: 60,
        assigned_resources: ["machine_alpha"],
      },
    },
  },
  disruptions: [
    {
      disruption_type: "task_delay",
      task_id: "task_roughing",
      delay_minutes: 45,
      description: "Tooling re-calibration pause during milling",
    },
  ],
};

export const SAMPLE_RESCHEDULE_PAYLOAD: RescheduleRequest = {
  tenant_id: "org_default",
  schedule_id: "sched_run_alpha_01",
  disruptions: [
    {
      disruption_type: "task_delay",
      task_id: "task_roughing",
      delay_minutes: 45,
      description: "Tooling re-calibration pause during milling",
    },
  ],
  stability_weight: 1.5,
};

export const SAMPLE_STRIPBOARD_PAYLOAD: StripboardRenderRequest = {
  stripboard_data: {
    project_title: "Chitram Feature Film Production",
    total_shoot_days: 2,
    days: [
      {
        day_number: 1,
        date: "2026-11-15",
        total_pages_eighths: 32,
        total_estimated_minutes: 480,
        strips: [
          {
            scene_number: "1",
            setting: "INT",
            time_of_day: "DAY",
            synopsis: "Opening conference table discussion",
            location_name: "Soundstage A",
            character_numbers: [1, 2, 4],
            pages_eighths: 16,
          },
          {
            scene_number: "4A",
            setting: "EXT",
            time_of_day: "DUSK",
            synopsis: "Car chase in back alley",
            location_name: "Backlot Urban Street",
            character_numbers: [1, 3],
            pages_eighths: 16,
          },
        ],
      },
      {
        day_number: 2,
        date: "2026-11-16",
        total_pages_eighths: 24,
        total_estimated_minutes: 420,
        strips: [
          {
            scene_number: "9",
            setting: "INT",
            time_of_day: "NIGHT",
            synopsis: "Safehouse infiltration",
            location_name: "Warehouse Stage 2",
            character_numbers: [2, 5],
            pages_eighths: 24,
          },
        ],
      },
    ],
  },
  width: 900,
};

export const SAMPLE_DOOD_PAYLOAD: DOODRenderRequest = {
  reports: [
    {
      talent_id: "cast_hero",
      character_name: "Vikram (Lead)",
      daily_status: { "1": "SW", "2": "W", "3": "H", "4": "W", "5": "WF" },
      total_work_days: 4,
      total_hold_days: 1,
      total_paid_days: 5,
      total_cost: 25000,
    },
    {
      talent_id: "cast_mentor",
      character_name: "Professor Rao",
      daily_status: { "1": "SW", "2": "WF", "3": "I", "4": "I", "5": "I" },
      total_work_days: 2,
      total_hold_days: 0,
      total_paid_days: 2,
      total_cost: 8000,
    },
  ],
  total_days: 5,
};

export const SAMPLE_GANTT_PAYLOAD: GanttRenderRequest = {
  tasks: [
    { id: "task_1", resource: "Crew_A", start: 0, end: 180 },
    { id: "task_2", resource: "Crew_B", start: 180, end: 360 },
    { id: "task_3", resource: "Crew_A", start: 360, end: 480 },
    { id: "task_4", resource: "Inspector", start: 480, end: 540 },
  ],
  resources: ["Crew_A", "Crew_B", "Inspector"],
  total_makespan: 540,
  width: 900,
  height_per_row: 45,
};

export const SAMPLE_CULTURAL_PAYLOAD: CulturalIntervalsRequest = {
  horizon_days: 7,
  enable_rahu_kalam: true,
  enable_yamagandam: true,
};

export const SAMPLE_STANDARD_BLACKOUTS_PAYLOAD: StandardBlackoutsRequest = {
  horizon_days: 7,
  working_day_start_minute: 480,
  working_day_end_minute: 1020,
  weekend_days: [5, 6],
};

export const SAMPLE_FILM_PAYLOAD: ProductionDataset = {
  production_title: "Chitram Cinematic Feature",
  max_days: 5,
  cast: [
    { id: "lead_actor", name: "Arjun", day_rate_cents: 600000 },
    { id: "antagonist", name: "Devraj", day_rate_cents: 450000 },
    { id: "supporting", name: "Pooja", day_rate_cents: 250000 },
  ],
  locations: [
    { id: "loc_mansion", name: "Heritage Palace" },
    { id: "loc_docks", name: "Container Port" },
  ],
  scenes: [
    {
      id: "sc_1",
      name: "Opening Scene 1",
      duration_minutes: 180,
      location_id: "loc_mansion",
      cast_ids: ["lead_actor", "supporting"],
      is_night: false,
      is_exterior: false,
    },
    {
      id: "sc_2",
      name: "Courtyard Confrontation",
      duration_minutes: 240,
      location_id: "loc_mansion",
      cast_ids: ["lead_actor", "antagonist"],
      is_night: true,
      is_exterior: false,
    },
    {
      id: "sc_3",
      name: "Docks Infiltration",
      duration_minutes: 210,
      location_id: "loc_docks",
      cast_ids: ["lead_actor", "antagonist"],
      is_night: true,
      is_exterior: true,
    },
  ],
};

export const SAMPLE_MANUFACTURING_PAYLOAD: ManufacturingOptimizeRequest = {
  machines: [
    { id: "cnc_mill_01", name: "5-Axis CNC Mill", speed_factor: 1.0 },
    { id: "lathe_02", name: "High Speed Lathe", speed_factor: 1.2 },
  ],
  jobs: [
    {
      id: "turbine_blade_batch",
      name: "Titanium Turbine Blades",
      priority: 1,
      operations: [
        {
          id: "op_blade_rough",
          name: "Blade Roughing",
          required_machine_id: "cnc_mill_01",
          duration_minutes: 60,
          setup_family: "aerospace",
        },
        {
          id: "op_blade_turn",
          name: "Blade Turning",
          required_machine_id: "lathe_02",
          duration_minutes: 40,
          setup_family: "aerospace",
        },
      ],
    },
    {
      id: "shaft_batch",
      name: "Rotor Shafts",
      priority: 2,
      operations: [
        {
          id: "op_shaft_turn",
          name: "Shaft Turning",
          required_machine_id: "lathe_02",
          duration_minutes: 50,
          setup_family: "rotary",
        },
        {
          id: "op_shaft_finish",
          name: "Shaft Finishing",
          required_machine_id: "cnc_mill_01",
          duration_minutes: 35,
          setup_family: "rotary",
        },
      ],
    },
  ],
  setup_matrix: [
    {
      machine_id: "cnc_mill_01",
      from_family: "aerospace",
      to_family: "rotary",
      setup_minutes: 20,
    },
    {
      machine_id: "cnc_mill_01",
      from_family: "rotary",
      to_family: "aerospace",
      setup_minutes: 25,
    },
  ],
  max_time_seconds: 5.0,
};

export const SAMPLE_WORKFORCE_PAYLOAD: WorkforceOptimizeRequest = {
  staff: [
    { id: "doc_1", name: "Dr. Ananya", skills: ["emergency", "icu"] },
    { id: "nurse_1", name: "Nurse Vikram", skills: ["emergency"] },
    { id: "nurse_2", name: "Nurse Priya", skills: ["icu", "general"] },
    { id: "tech_1", name: "Radiology Tech Rahul", skills: ["imaging"] },
  ],
  shifts: [
    { id: "shift_er_am", name: "Emergency AM", start_minute: 420, duration_minutes: 480, required_skill: "emergency" },
    { id: "shift_er_pm", name: "Emergency PM", start_minute: 900, duration_minutes: 480, required_skill: "emergency" },
    { id: "shift_icu_night", name: "ICU Night Watch", start_minute: 1380, duration_minutes: 480, required_skill: "icu" },
  ],
  max_time_seconds: 5.0,
};

export const SAMPLE_MARKETING_PAYLOAD: MarketingOptimizeRequest = {
  channels: [
    { id: "meta_ads", name: "Meta Video Ads", daily_budget_cents_cap: 150000 },
    { id: "google_search", name: "Google High-Intent Search", daily_budget_cents_cap: 200000 },
    { id: "ott_streaming", name: "Connected TV & OTT", daily_budget_cents_cap: 350000 },
  ],
  flights: [
    {
      id: "brand_launch_pulse",
      name: "Brand Launch Pulse",
      channel_id: "meta_ads",
      duration_days: 14,
      daily_budget_cents: 120000,
    },
    {
      id: "search_harvesting",
      name: "Search Harvesting",
      channel_id: "google_search",
      duration_days: 21,
      daily_budget_cents: 150000,
    },
    {
      id: "ott_heavy_weekend",
      name: "OTT Weekend Heavy Pulse",
      channel_id: "ott_streaming",
      duration_days: 7,
      daily_budget_cents: 250000,
    },
  ],
  max_time_seconds: 5.0,
};

export const SAMPLE_ACADEMIC_PAYLOAD: AcademicOptimizeRequest = {
  cohorts: [
    { id: "cs_year_2", name: "CS Sophomores" },
    { id: "ee_year_3", name: "EE Juniors" },
  ],
  classrooms: [
    { id: "lecture_hall_a", name: "Main Auditorium A", capacity: 100 },
    { id: "lab_302", name: "Computer Systems Lab", capacity: 50 },
  ],
  instructors: [
    { id: "prof_turing", name: "Prof. Alan Turing" },
    { id: "prof_shannon", name: "Prof. Claude Shannon" },
  ],
  classes: [
    {
      id: "cs201_algo",
      name: "Algorithms & Data Structures",
      cohort_id: "cs_year_2",
      instructor_id: "prof_turing",
      duration_minutes: 90,
    },
    {
      id: "ee305_dsp",
      name: "Digital Signal Processing",
      cohort_id: "ee_year_3",
      instructor_id: "prof_shannon",
      duration_minutes: 90,
    },
  ],
  max_time_seconds: 5.0,
};

export const SAMPLE_EVENTS_PAYLOAD: EventsOptimizeRequest = {
  halls: [
    { id: "grand_ballroom", name: "Grand Keynote Ballroom", capacity: 800 },
    { id: "breakout_room_1", name: "Breakout Room Alpha", capacity: 200 },
  ],
  speakers: [
    { id: "speaker_keynote_1", name: "Dr. Evelyn Reed (AI Fellow)" },
    { id: "speaker_panel_2", name: "Marcus Vance (VP Ops)" },
  ],
  sessions: [
    {
      id: "session_keynote",
      title: "Opening Keynote: Autonomous Operations",
      duration_minutes: 60,
      speaker_id: "speaker_keynote_1",
    },
    {
      id: "session_workshop",
      title: "Hands-on CP-SAT Constraint Programming",
      duration_minutes: 90,
      speaker_id: "speaker_panel_2",
    },
  ],
  max_time_seconds: 5.0,
};
