/**
 * Ojas Ops SDK TypeScript Types
 * Strongly typed contracts mirroring all Ojas Ops backend models, schemas, and endpoints
 */

// ============================================================================
// Core Primitive Types & Common DTOs
// ============================================================================

export interface IntervalWindow {
  start: number;
  end: number;
  label?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  total?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
  items?: T[];
}

export interface TenantPaginationQuery {
  tenant_id?: string;
  page?: number;
  page_size?: number;
  status?: string;
  search?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  service: string;
}

export interface ReadinessResponse {
  ready: string;
  engine: string;
}

// ============================================================================
// Model-Based CRUD Records
// ============================================================================

export interface ScheduleRunRecord {
  id: number;
  tenant_id: string;
  scenario_name: string;
  status: string;
  makespan?: number | null;
  objective_value?: number | null;
  solver_status: string;
  solve_time_seconds: number;
  result_json: Record<string, unknown>;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface OptimizationJobRecord {
  id: number;
  tenant_id: string;
  temporal_workflow_id: string;
  task_queue: string;
  status: string;
  incumbent_objective?: number | null;
  best_bound?: number | null;
  progress_basis_points: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ScenarioRecordDTO {
  id: number;
  tenant_id: string;
  name: string;
  domain: string;
  scale: string;
  definition_json: Record<string, unknown>;
  golden_expected_json?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface DisruptionLogRecord {
  id: number;
  tenant_id: string;
  schedule_run_id: string;
  disruption_type: string;
  magnitude_minutes: number;
  affected_tasks: string[];
  rescheduled_makespan?: number | null;
  metadata?: Record<string, unknown>;
  created_at: string;
}

// ============================================================================
// Temporal Workflows & Human-in-the-Loop (HITL)
// ============================================================================

export interface WorkflowStatusResponse {
  status: string;
  workflow_id: string;
  incumbent_objective?: number | null;
  best_bound?: number | null;
  progress_basis_points?: number;
}

export interface WorkflowSignalRequest {
  decision: "APPROVED" | "REJECTED";
  notes?: string | null;
}

export interface WorkflowSignalResponse {
  workflow_id: string;
  status: string;
  signal_sent: boolean;
  error?: string | null;
}

export interface ApprovalStateResponse {
  status: string;
  decision?: string | null;
  notes?: string | null;
  has_solution: boolean;
}

export interface DispatchResponse {
  workflow_id: string;
  status: string;
  task_queue?: string;
  schedule_id?: string;
}

// ============================================================================
// Core Scheduling & Validation
// ============================================================================

export interface TaskRequirement {
  resource_id: string;
  capacity?: number;
  quantity?: number;
  candidate_pool?: string[];
}

export interface Task {
  id: string;
  name: string;
  duration: number;
  priority?: number;
  required_resources?: string[];
  requirements?: TaskRequirement[];
  dependencies?: string[];
  eligible_resources?: string[];
  earliest_start?: number;
  latest_end?: number;
  attributes?: Record<string, unknown>;
}

export interface Resource {
  id: string;
  name: string;
  capacity?: number;
  skills?: string[];
  blackout_windows?: IntervalWindow[];
  cost_per_time_unit_minor?: number;
  cost_per_hour?: number;
  attributes?: Record<string, unknown>;
}

export interface PrecedenceConstraint {
  predecessor_id: string;
  successor_id: string;
  min_delay?: number;
  max_delay?: number;
}

export interface ScenarioData {
  name: string;
  domain?: string;
  tasks: Task[];
  resources: Resource[];
  precedences?: PrecedenceConstraint[];
  horizon_start?: number;
  horizon_end?: number;
  metadata?: Record<string, unknown>;
}

export interface ScheduledTask {
  task_id: string;
  start_time: number;
  end_time: number;
  duration: number;
  assigned_resources: string[];
}

export interface SolverMetrics {
  wall_time: number;
  user_time?: number;
  branches?: number;
  conflicts?: number;
  objective_value?: number;
  best_objective_bound?: number;
  solve_time_seconds?: number;
}

export type SolverStatus = "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "MODEL_INVALID" | "UNKNOWN";

export interface ScheduleSolution {
  status: SolverStatus;
  schedule_id?: string;
  objective_value?: number;
  makespan?: number;
  tasks_scheduled_count?: number;
  assignments?: ScheduledTask[];
  tasks?: Record<
    string,
    { start: number; end: number; duration?: number; assigned_resources: string[] }
  >;
  metrics?: SolverMetrics;
}

export type ViolationSeverity = "HARD" | "SOFT";

export interface Violation {
  constraint_type: string;
  severity: ViolationSeverity;
  message: string;
  task_ids: string[];
  resource_ids: string[];
  penalty?: number;
}

export interface ValidationReport {
  is_valid: boolean;
  hard_violations_count: number;
  soft_violations_count: number;
  total_penalty: number;
  violations: Violation[];
}

export interface OptimizeScheduleRequest {
  tenant_id?: string;
  project_id?: string;
  schedule_id?: string;
  horizon: { start: number; end: number };
  resources: Resource[];
  tasks: Task[];
  strategy?: "fast" | "balanced" | "deep_optimal";
  max_time_seconds?: number;
  solver_config?: SolverConfig;
}

export interface OptimizeScheduleResponse {
  schedule_id: string;
  status: string;
  makespan?: number;
  objective_value?: number;
  tasks_scheduled_count: number;
  tasks: Record<
    string,
    { start: number; end: number; duration?: number; assigned_resources: string[] }
  >;
  metrics?: SolverMetrics;
}

export interface ValidateScheduleRequest {
  tenant_id?: string;
  schedule_id: string;
  solution?: ScheduleSolution;
  scenario?: ScenarioData;
}

export interface ValidateScheduleResponse {
  schedule_id: string;
  is_valid: boolean;
  report: ValidationReport;
}

export interface SolverConfig {
  time_limit_seconds?: number;
  num_workers?: number;
  search_branching?: string;
  log_search_progress?: boolean;
}

// ============================================================================
// Simulations & Rescheduling
// ============================================================================

export type DisruptionType =
  | "task_delay"
  | "resource_breakdown"
  | "task_cancellation"
  | "capacity_reduction";

export interface DisruptionContract {
  disruption_type: DisruptionType;
  task_id?: string | null;
  delay_minutes?: number;
  resource_id?: string | null;
  blackout_start?: number | null;
  blackout_end?: number | null;
  description?: string;
}

export interface SimulateDisruptionRequest {
  tenant_id: string;
  schedule_id: string;
  baseline_schedule: Record<string, unknown>;
  disruptions: DisruptionContract[];
  current_time?: number;
}

export interface SimulateDisruptionResponse {
  schedule_id: string;
  is_feasible: boolean;
  original_makespan: number;
  new_makespan: number;
  rescheduled_result: Record<string, unknown>;
  affected_tasks: string[];
  stability_metric: number;
}

export interface RescheduleRequest {
  tenant_id: string;
  schedule_id: string;
  disruptions: DisruptionContract[];
  stability_weight?: number;
  current_time?: number;
}

export interface RescheduleResponse {
  schedule_id: string;
  status: string;
  result: Record<string, unknown>;
  makespan: number;
  solve_time_seconds: number;
}

// ============================================================================
// Scenarios & Benchmarks
// ============================================================================

export interface ScenarioDefinition {
  metadata: {
    name: string;
    description?: string;
    domain: string;
  };
  resources: Resource[];
  tasks: Task[];
  precedences?: PrecedenceConstraint[];
  golden_expected?: {
    status?: string;
    max_makespan?: number;
    expected_makespan?: number;
  };
}

export interface GenerateScenarioRequest {
  scenario_type: "jobshop" | "workforce" | "film";
  num_jobs?: number;
  num_machines?: number;
  num_staff?: number;
  num_shifts?: number;
  horizon_hours?: number;
  num_scenes?: number;
  num_cast?: number;
  num_locations?: number;
  seed?: number;
  num_nurses?: number;
  num_days?: number;
  num_actors?: number;
}

export interface GeneratedScenarioSummary {
  scenario_type: string;
  name: string;
  domain: string;
  tasks_count: number;
  resources_count: number;
  tasks: string[];
  resources: string[];
  error?: string;
}

export interface ScenarioExecutionResponse {
  is_success: boolean;
  verification_failures: string[];
  makespan?: number | null;
  status: string;
}

// ============================================================================
// Visualizations & Multi-Format Exporters
// ============================================================================

export interface StripboardRenderRequest {
  stripboard_data: Record<string, unknown>;
  width?: number;
}

export interface DOODRenderRequest {
  reports: Array<Record<string, unknown>>;
  total_days?: number;
  currency_symbol?: string;
}

export interface GanttRenderRequest {
  tasks: Array<{ id: string; resource: string; start: number; end: number }>;
  resources: string[];
  total_makespan: number;
  width?: number;
  height_per_row?: number;
}

export interface ReportExportRequest {
  title: string;
  sections: string[];
  subtitle?: string;
}

export interface RenderHtmlResponse {
  html: string;
}

export interface RenderSvgResponse {
  svg: string;
}

// ============================================================================
// Calendar Engines
// ============================================================================

export interface CulturalIntervalsRequest {
  horizon_days?: number;
  day_minutes?: number;
  enable_rahu_kalam?: boolean;
  enable_yamagandam?: boolean;
}

export interface CulturalIntervalsResponse {
  horizon_days: number;
  blackout_windows: Array<{ start: number; end: number; label: string }>;
  auspicious_windows: Array<{ start: number; end: number; label: string }>;
}

export interface StandardBlackoutsRequest {
  horizon_days?: number;
  working_day_start_minute?: number;
  working_day_end_minute?: number;
  weekend_days?: number[];
}

export interface StandardBlackoutsResponse {
  blackout_windows: Array<{ start: number; end: number; label: string }>;
}

// ============================================================================
// Six Vertical Domain Adapters
// ============================================================================

// 1. Film Production
export interface Scene {
  id: string;
  name: string;
  duration_minutes: number;
  cast_ids: string[];
  location_id: string;
  is_night?: boolean;
  is_exterior?: boolean;
  requires_soundstage?: boolean;
}

export interface CastMember {
  id: string | number;
  name: string;
  character_name?: string;
  daily_rate?: number;
  daily_rate_cents?: number;
  day_rate_cents?: number;
  is_minor?: boolean;
  max_daily_hours?: number;
  hmu_duration_minutes?: number;
  wardrobe_duration_minutes?: number;
  travel_duration_minutes?: number;
  blackout_days?: number[];
  stunt_double_id?: string | number | null;
}

export type Talent = CastMember;

export interface ProductionLocation {
  id: string | number;
  name: string;
  location_type?: "SOUNDSTAGE" | "PRACTICAL_INT" | "PRACTICAL_EXT" | string;
  permitted_days?: number[];
  noise_curfew_hour?: number | null;
  allows_sync_sound?: boolean;
  daily_rental_cost?: number;
  daily_rental_cost_cents?: number;
  prep_days_required?: number;
  strike_days_required?: number;
  turnaround_minutes?: number;
  soundstage_facility_id?: string | number | null;
  is_soundstage?: boolean;
}

export type FilmLocation = ProductionLocation;

export interface PropItem {
  id: string | number;
  name: string;
  category?: "HERO" | "SET_DRESSING" | "BREAKAWAY" | "WEAPON" | "VEHICLE" | string;
  total_quantity?: number;
  is_destructible?: boolean;
  requires_armorer?: boolean;
  reset_duration_minutes?: number;
}

export interface CostumeItem {
  id: string | number;
  character_id: string | number;
  costume_code: string;
  distress_stage?: number;
  available_duplicates?: number;
  requires_specialist_dresser?: boolean;
}

export interface SpecialtyEquipmentItem {
  id: string | number;
  name: string;
  equipment_type?:
    | "TECHNOCRANE"
    | "PHANTOM_HIGH_SPEED"
    | "MOTION_CONTROL"
    | "UNDERWATER_HOUSING"
    | "RUSSIAN_ARM"
    | "DRONE"
    | string;
  daily_rental_cost?: number;
  daily_rental_cost_cents?: number;
  rental_start_day?: number;
  rental_end_day?: number;
  requires_certified_technician?: boolean;
}

export interface StuntSFXItem {
  id: string | number;
  has_wirework?: boolean;
  has_pyrotechnics?: boolean;
  has_squibs?: boolean;
  pre_rigging_hours_required?: number;
  pre_rigging_minutes_required?: number;
  mandatory_medic_count?: number;
  stunt_hazard_level?: number;
}

export interface CalendarDayItem {
  day_number: number;
  calendar_date: string;
  is_statutory_holiday?: boolean;
  is_inauspicious?: boolean;
  expected_weather?: "CLEAR" | "OVERCAST" | "RAIN" | "MONSOON" | string;
  sunrise_time?: string;
  sunset_time?: string;
  dawn_minute?: number;
  sunrise_minute?: number;
  sunset_minute?: number;
  dusk_minute?: number;
  is_weekend?: boolean;
}

export interface FilmProductionUnit {
  id: string | number;
  name: string;
  unit_type?: "MAIN" | "SECOND" | "SPLINTER" | "VFX" | string;
  daily_operating_cost_cents?: number;
}

export interface FilmCameraSetup {
  id: string | number;
  name: string;
  axis_angle?: string;
  lighting_setup_id?: string;
}

export interface FilmScene {
  id: string | number;
  scene_number?: string;
  name?: string;
  part?: number;
  location_id?: string | number;
  setting?: "INT" | "EXT" | string;
  time_of_day?: "DAY" | "NIGHT" | "MAGIC_HOUR" | string;
  page_eighths?: number;
  duration_minutes?: number;
  duration_hours?: number;
  required_cast?: Array<string | number>;
  cast_ids?: string[];
  required_prop_ids?: Array<string | number>;
  required_costume_ids?: Array<string | number>;
  required_equipment_ids?: Array<string | number>;
  stunt_sfx_package_id?: string | number | null;
  weather_requirement?:
    | "ANY"
    | "CLEAR_ONLY"
    | "OVERCAST_ONLY"
    | "RAIN_MANDATORY"
    | "NO_RAIN"
    | string;
  sound_recording?: "SYNC_SOUND" | "MOS" | "WILD_TRACK" | string;
  holiday_compatibility?: "NORMAL" | "HOLIDAY_ONLY" | "FORBID_HOLIDAY" | string;
  earliest_allowed_day?: number | null;
  latest_allowed_day?: number | null;
  is_cover_set?: boolean;
  cover_for_scene_id?: string | number | null;
  requires_precedence_over?: string | number | null;
  min_lag_days?: number;
  is_second_unit?: boolean;
  is_vfx_heavy?: boolean;
  unit_type?: "MAIN" | "SECOND" | "SPLINTER" | "VFX" | string;
  setup_id?: string | number | null;
  background_count?: number;
  vfx_turnover_deadline_day?: number | null;
  stunt_hazard_level?: number;
  dependencies?: string[];
  is_night?: boolean;
  is_exterior?: boolean;
}

export interface ProductionDataset {
  project_title?: string;
  production_title?: string;
  talents?: CastMember[];
  cast?: CastMember[];
  locations: ProductionLocation[];
  props?: PropItem[];
  costumes?: CostumeItem[];
  equipment?: SpecialtyEquipmentItem[];
  stunts?: StuntSFXItem[];
  calendar?: CalendarDayItem[];
  scenes: FilmScene[];
  units?: FilmProductionUnit[];
  setups?: FilmCameraSetup[];
  max_shooting_days?: number;
  max_days?: number;
  max_hours_per_day?: number;
  hmu_stations_capacity?: number;
  medic_capacity?: number;
}

export interface StripboardStrip {
  scene_id: string | number;
  scene_number: string;
  part: number;
  strip_color: "WHITE" | "YELLOW" | "GREEN" | "BLUE" | string;
  setting: string;
  time_of_day: string;
  location_id: string | number;
  location_name: string;
  duration_minutes: number;
  page_eighths: number;
  cast_ids: string[];
  is_second_unit: boolean;
}

export interface StripboardDay {
  day_number: number;
  calendar_date: string;
  is_rest_day: boolean;
  rest_reason?: string | null;
  expected_weather?: string;
  total_duration_minutes: number;
  total_page_eighths: number;
  strips: StripboardStrip[];
}

export interface MasterStripboard {
  project_title: string;
  total_shoot_days: number;
  total_calendar_days: number;
  days: StripboardDay[];
}

export interface DayOutOfDaysReport {
  talent_id: string | number;
  talent_name: string;
  character_name: string;
  daily_codes: Record<string | number, "SW" | "W" | "H" | "WF" | "SWF" | "DROP" | "." | string>;
  total_work_days: number;
  total_hold_days: number;
  total_paid_days: number;
  estimated_cost: number;
}

export interface CallSheetSceneEntry {
  scene_number: string;
  start_time: string;
  end_time: string;
  setting: string;
  time_of_day: string;
  location_name: string;
  cast_ids: string[];
  page_eighths: number;
}

export interface CallSheetCharacterEntry {
  talent_id: string | number;
  character_name: string;
  actor_name: string;
  pickup_call: string;
  hmu_call: string;
  wardrobe_call: string;
  set_call: string;
}

export interface DailyCallSheet {
  day_number: number;
  calendar_date: string;
  project_title: string;
  sunrise_time: string;
  sunset_time: string;
  expected_weather: string;
  general_crew_call: string;
  shooting_call: string;
  first_meal_due: string;
  second_meal_due?: string | null;
  hospital_info: string;
  scene_entries: CallSheetSceneEntry[];
  character_calls: CallSheetCharacterEntry[];
}

export interface FilmScheduleResult {
  status: string;
  is_feasible?: boolean;
  solve_time_seconds?: number;
  objective_cost?: number;
  project_title?: string;
  production_title?: string;
  total_shooting_days?: number;
  stripboard?: MasterStripboard;
  dood_reports?: DayOutOfDaysReport[];
  call_sheets?: Record<string | number, DailyCallSheet>;
  scene_day_assignments?: Record<string, number>;
  talent_daily_status?: Record<string, Record<string | number, string>>;
  shooting_days?: Array<{
    day_number: number;
    scenes: string[];
    cast_working: string[];
    location_id: string;
  }>;
  dood_matrix?: Record<string, string[]>;
}

export interface FilmOptimizeRequest {
  dataset: ProductionDataset;
  max_time_in_seconds?: number;
  move_penalty?: number;
  enable_drop_pickup?: boolean;
  enable_soundstage_lease_tracking?: boolean;
  enable_hazard_deferral?: boolean;
  enable_intraday_micro_optimization?: boolean;
  fixed_assignments?: Record<string, number>;
}

export interface FilmRescheduleRequest {
  dataset: ProductionDataset;
  completed_days?: number[];
  weather_disruptions?: Record<string | number, string>;
  talent_blackouts?: Record<string, number[]>;
  activate_cover_sets?: boolean;
  max_time_in_seconds?: number;
  fixed_assignments?: Record<string, number>;
}

export interface FilmIntradayRequest {
  scenes: FilmScene[];
  calendar_day: CalendarDayItem;
  locations?: ProductionLocation[];
  talents?: CastMember[];
  shooting_call_minute?: number;
  max_day_minutes?: number;
}

export interface FilmCallSheetRequest {
  dataset: ProductionDataset;
  day_number: number;
  general_crew_call_time?: string;
  shooting_call_time?: string;
  hospital_info?: string;
  optimize_intraday?: boolean;
}

// 2. Manufacturing Job-Shop
export interface Machine {
  id: string;
  name: string;
  speed_factor?: number;
}

export interface JobOperation {
  id: string;
  name: string;
  duration_minutes: number;
  required_machine_id: string;
  setup_family?: string;
}

export interface ProductionJob {
  id: string;
  name: string;
  priority?: number;
  operations: JobOperation[];
}

export interface SetupMatrixEntry {
  machine_id: string;
  from_family: string;
  to_family: string;
  setup_minutes: number;
}

export interface ManufacturingOptimizeRequest {
  machines: Machine[];
  jobs: ProductionJob[];
  setup_matrix?: SetupMatrixEntry[];
  max_time_seconds?: number;
}

export interface ManufacturingOptimizeResponse {
  status: string;
  makespan: number;
  solve_time_seconds: number;
  tasks: Record<string, string[]>;
}

// 3. Workforce & Nurse Rostering
export interface StaffMember {
  id: string;
  name: string;
  skills?: string[];
  max_consecutive_days?: number;
  min_rest_hours?: number;
}

export interface ShiftSlot {
  id: string;
  name: string;
  start_minute: number;
  duration_minutes: number;
  required_skill?: string;
}

export interface WorkforceOptimizeRequest {
  staff: StaffMember[];
  shifts: ShiftSlot[];
  horizon_minutes?: number;
  max_time_seconds?: number;
}

export interface WorkforceOptimizeResponse {
  status: string;
  makespan: number;
  solve_time_seconds: number;
  assignments: Record<string, string[]>;
}

// 4. Marketing Budget Flighting
export interface MarketingChannel {
  id: string;
  name: string;
  daily_budget_cents_cap?: number;
}

export interface MediaFlight {
  id: string;
  name: string;
  channel_id: string;
  duration_days: number;
  daily_budget_cents: number;
}

export interface MarketingOptimizeRequest {
  channels: MarketingChannel[];
  flights: MediaFlight[];
  horizon_days?: number;
  max_time_seconds?: number;
}

export interface MarketingOptimizeResponse {
  status: string;
  makespan: number;
  total_spend_cents: number;
  flights: Record<string, { start: number; end: number }>;
  solve_time_seconds: number;
}

// 5. Academic Timetabling
export interface StudentCohort {
  id: string;
  name: string;
}

export interface Instructor {
  id: string;
  name: string;
}

export interface Classroom {
  id: string;
  name: string;
  capacity?: number;
}

export interface CourseClass {
  id: string;
  name: string;
  cohort_id: string;
  instructor_id: string;
  duration_minutes: number;
}

export interface AcademicOptimizeRequest {
  cohorts: StudentCohort[];
  instructors: Instructor[];
  classrooms: Classroom[];
  classes: CourseClass[];
  horizon_minutes?: number;
  max_time_seconds?: number;
}

export interface AcademicOptimizeResponse {
  status: string;
  makespan: number;
  schedule: Record<string, { start: number; end: number; resources: string[] }>;
  solve_time_seconds: number;
}

// 6. Conference Event Run Sheets
export interface VenueHall {
  id: string;
  name: string;
  capacity?: number;
}

export interface EventSpeaker {
  id: string;
  name: string;
}

export interface EventSession {
  id: string;
  title: string;
  speaker_id: string;
  duration_minutes: number;
  preferred_hall_id?: string;
}

export interface EventsOptimizeRequest {
  halls: VenueHall[];
  speakers: EventSpeaker[];
  sessions: EventSession[];
  event_duration_minutes?: number;
  max_time_seconds?: number;
}

export interface EventsOptimizeResponse {
  status: string;
  makespan: number;
  session_assignments: Record<string, { start: number; end: number; resources: string[] }>;
  solve_time_seconds: number;
}

// ============================================================================
// 7. Instruction-Driven Pipelines & Project Workspaces
// ============================================================================

export type PipelineStageStatus =
  | "pending"
  | "running"
  | "awaiting_human"
  | "completed"
  | "failed"
  | "revising";

export interface PipelineManifestSummary {
  name: string;
  version: string;
  description: string;
  category: string;
  stability: "production" | "beta" | "experimental";
  stages_count: number;
  compatible_rulesets: string[];
}

export interface PipelineStageDefinition {
  name: string;
  skill: string;
  required_artifacts_in?: string[];
  optional_artifacts_in?: string[];
  produces?: string[];
  tools_available?: string[];
  checkpoint_required?: boolean;
  human_approval_default?: boolean;
  review_focus?: string[];
  success_criteria?: string[];
}

export interface PipelineManifest {
  name: string;
  version: string;
  description: string;
  category: string;
  stability: "production" | "beta" | "experimental";
  default_checkpoint_policy?: "guided" | "manual_all" | "autonomous";
  compatible_rulesets?: string[];
  required_skills?: string[];
  stages: PipelineStageDefinition[];
}

export interface RulesetSummary {
  name: string;
  version: string;
  domain: string;
  description: string;
}

export interface RulesetPolicy {
  name: string;
  version: string;
  domain: string;
  description: string;
  parameters: Record<string, unknown>;
  hard_constraints?: string[];
  soft_constraints?: string[];
}

export interface ProjectWorkspaceRecord {
  id: number;
  tenant_id: string;
  project_id: string;
  title: string;
  pipeline_type: string;
  ruleset?: string;
  status: string;
  current_stage: string;
  temporal_workflow_id?: string;
  completed_stages: string[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ProjectInitRequest {
  project_id: string;
  title: string;
  pipeline_type: string;
  tenant_id?: string;
  ruleset?: string;
  metadata?: Record<string, unknown>;
}

export interface ProjectInitResponse {
  status: string;
  project_id: string;
  tenant_id: string;
  pipeline_type: string;
  path: string;
  id?: number | null;
}

export interface ProjectCheckpointRecord {
  version: string;
  tenant_id: string;
  project_id: string;
  pipeline_type: string;
  stage: string;
  status: PipelineStageStatus;
  timestamp: string;
  ruleset?: string;
  checkpoint_policy: string;
  human_approval_required: boolean;
  human_approved: boolean;
  artifacts: Record<string, unknown>;
  review?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface GateApprovalRequest {
  tenant_id?: string;
  notes?: string;
  overrides?: Record<string, unknown>;
}

export interface GateApprovalResponse {
  status: string;
  project_id: string;
  stage: string;
  notes?: string;
}

export interface StageRunRequest {
  tenant_id?: string;
  inputs?: Record<string, unknown>;
  revision_notes?: string;
}

export interface StageRunResponse {
  status: string;
  project_id: string;
  stage: string;
  checkpoint?: ProjectCheckpointRecord;
  artifacts?: Record<string, unknown>;
}

export interface GateRevisionRequest {
  tenant_id?: string;
  feedback: string;
  overrides?: Record<string, unknown>;
}

export interface GateRevisionResponse {
  status: string;
  project_id: string;
  stage: string;
  checkpoint?: ProjectCheckpointRecord;
}

export interface PipelineEventItem {
  id: string;
  timestamp: string;
  tenant_id?: string;
  project_id: string;
  type: string;
  message: string;
  stage?: string;
  data?: Record<string, unknown>;
}
