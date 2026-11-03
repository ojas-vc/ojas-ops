import type {
  DisruptionEvent,
  HealthResponse,
  ScenarioData,
  ScheduleSolution,
  SimulationResult,
  SolverConfig,
  ValidationReport,
} from "./types";

export interface OjasOpsClientOptions {
  baseUrl?: string;
  fetchFn?: typeof fetch;
}

export class OjasOpsClient {
  private readonly baseUrl: string;
  private readonly fetch: typeof fetch;

  constructor(options: OjasOpsClientOptions = {}) {
    this.baseUrl = (options.baseUrl || "http://127.0.0.1:8000").replace(/\/$/, "");
    this.fetch = options.fetchFn || globalThis.fetch;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const response = await this.fetch(url, { ...options, headers });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OjasOps API error (${response.status}): ${errorText}`);
    }
    return response.json() as Promise<T>;
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/api/v1/health/");
  }

  async optimizeSync(
    scenario: ScenarioData,
    solverConfig?: SolverConfig,
  ): Promise<ScheduleSolution> {
    return this.request<ScheduleSolution>("/api/v1/schedules/optimize-sync/", {
      method: "POST",
      body: JSON.stringify({
        scenario,
        solver_config: solverConfig,
      }),
    });
  }

  async validateSchedule(
    solution: ScheduleSolution,
    scenario: ScenarioData,
  ): Promise<ValidationReport> {
    return this.request<ValidationReport>("/api/v1/schedules/validate/", {
      method: "POST",
      body: JSON.stringify({
        solution,
        scenario,
      }),
    });
  }

  async simulateDisruption(
    scenario: ScenarioData,
    currentSolution: ScheduleSolution,
    disruption: DisruptionEvent,
  ): Promise<SimulationResult> {
    return this.request<SimulationResult>("/api/v1/simulation/simulate-disruption/", {
      method: "POST",
      body: JSON.stringify({
        scenario,
        current_solution: currentSolution,
        disruption,
      }),
    });
  }

  async generateScenario(domain: string, scale = "small"): Promise<ScenarioData> {
    return this.request<ScenarioData>("/api/v1/scenarios/generate/", {
      method: "POST",
      body: JSON.stringify({ domain, scale }),
    });
  }
}
