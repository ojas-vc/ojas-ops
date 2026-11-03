/**
 * Ojas Ops SDK TypeScript Types
 * Strongly typed contracts mirroring the Ojas Ops Operations Research models
 */

export interface IntervalWindow {
  start: number;
  end: number;
}

export interface TaskRequirement {
  resource_id: string;
  quantity: number;
}

export interface Task {
  id: string;
  name: string;
  duration: number;
  requirements?: TaskRequirement[];
  eligible_resources?: string[];
  earliest_start?: number;
  latest_end?: number;
  priority?: number;
  attributes?: Record<string, unknown>;
}

export interface Resource {
  id: string;
  name: string;
  capacity?: number;
  skills?: string[];
  blackout_windows?: IntervalWindow[];
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
}

export type SolverStatus = "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "MODEL_INVALID" | "UNKNOWN";

export interface ScheduleSolution {
  status: SolverStatus;
  objective_value?: number;
  makespan?: number;
  assignments: ScheduledTask[];
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

export interface DisruptionEvent {
  event_type: "TASK_DELAY" | "RESOURCE_BREAKDOWN" | "NEW_TASK" | "CANCELLED_TASK";
  target_id: string;
  start_time: number;
  duration?: number;
  impact_magnitude?: number;
  description?: string;
}

export interface SimulationResult {
  disruption_applied: DisruptionEvent;
  is_feasible: boolean;
  recovery_solution?: ScheduleSolution;
  impact_summary: {
    delay_delta: number;
    cost_delta: number;
    affected_tasks_count: number;
  };
}

export interface SolverConfig {
  time_limit_seconds?: number;
  num_workers?: number;
  search_branching?: string;
  log_search_progress?: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  service: string;
}

