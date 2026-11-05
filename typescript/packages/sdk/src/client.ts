import type {
  AcademicOptimizeRequest,
  AcademicOptimizeResponse,
  ApprovalStateResponse,
  CulturalIntervalsRequest,
  CulturalIntervalsResponse,
  DOODRenderRequest,
  DailyCallSheet,
  DispatchResponse,
  DisruptionLogRecord,
  EventsOptimizeRequest,
  EventsOptimizeResponse,
  FilmCallSheetRequest,
  FilmIntradayRequest,
  FilmOptimizeRequest,
  FilmRescheduleRequest,
  FilmScheduleResult,
  GanttRenderRequest,
  GateApprovalRequest,
  GateApprovalResponse,
  GateRevisionRequest,
  GateRevisionResponse,
  GenerateScenarioRequest,
  GeneratedScenarioSummary,
  HealthResponse,
  ManufacturingOptimizeRequest,
  ManufacturingOptimizeResponse,
  MarketingOptimizeRequest,
  MarketingOptimizeResponse,
  OptimizationJobRecord,
  OptimizeScheduleRequest,
  OptimizeScheduleResponse,
  PaginatedResponse,
  PipelineEventItem,
  PipelineManifest,
  PipelineManifestSummary,
  ProductionDataset,
  ProjectCheckpointRecord,
  ProjectInitRequest,
  ProjectInitResponse,
  ProjectWorkspaceRecord,
  ReadinessResponse,
  RenderHtmlResponse,
  RenderSvgResponse,
  ReportExportRequest,
  RescheduleRequest,
  RescheduleResponse,
  RulesetPolicy,
  RulesetSummary,
  ScenarioDefinition,
  ScenarioExecutionResponse,
  ScenarioRecordDTO,
  ScheduleRunRecord,
  SimulateDisruptionRequest,
  SimulateDisruptionResponse,
  StageRunRequest,
  StageRunResponse,
  StandardBlackoutsRequest,
  StandardBlackoutsResponse,
  StripboardRenderRequest,
  TenantPaginationQuery,
  ValidateScheduleRequest,
  ValidateScheduleResponse,
  WorkflowSignalRequest,
  WorkflowSignalResponse,
  WorkflowStatusResponse,
  WorkforceOptimizeRequest,
  WorkforceOptimizeResponse,
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
    const customFetch = options.fetchFn;
    this.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
      if (customFetch) {
        return customFetch(input, init);
      }
      return globalThis.fetch(input, init);
    };
  }

  private buildQueryString(query?: TenantPaginationQuery): string {
    if (!query) return "";
    const params = new URLSearchParams();
    if (query.tenant_id) params.set("tenant_id", query.tenant_id);
    if (query.page) params.set("page", String(query.page));
    if (query.page_size) params.set("page_size", String(query.page_size));
    if (query.status) params.set("status", query.status);
    if (query.search) params.set("search", query.search);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
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
      throw new Error(
        `OjasOps API error (${response.status} ${response.statusText}): ${errorText}`,
      );
    }
    return response.json() as Promise<T>;
  }

  private normalizePaginated<T>(raw: any): PaginatedResponse<T> {
    const count = raw?.count ?? raw?.total ?? (Array.isArray(raw) ? raw.length : 0);
    const results = raw?.results ?? raw?.items ?? (Array.isArray(raw) ? raw : []);
    return {
      count,
      total: count,
      results,
      items: results,
      next: raw?.next,
      previous: raw?.previous,
    };
  }

  // ==========================================================================
  // Cloud Health Probes
  // ==========================================================================

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/healthz");
  }

  async getReadiness(): Promise<ReadinessResponse> {
    return this.request<ReadinessResponse>("/readyz");
  }

  // ==========================================================================
  // 1. Model-Based CRUD: Schedule Runs
  // ==========================================================================

  scheduleRuns = {
    list: async (query?: TenantPaginationQuery): Promise<PaginatedResponse<ScheduleRunRecord>> => {
      const qs = this.buildQueryString(query);
      const res = await this.request<any>(`/schedule-runs/${qs}`);
      return this.normalizePaginated<ScheduleRunRecord>(res);
    },

    get: async (id: number | string): Promise<ScheduleRunRecord> => {
      return this.request<ScheduleRunRecord>(`/schedule-runs/${id}/`);
    },

    create: async (data: Partial<ScheduleRunRecord>): Promise<ScheduleRunRecord> => {
      return this.request<ScheduleRunRecord>("/schedule-runs/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    update: async (
      id: number | string,
      data: Partial<ScheduleRunRecord>,
    ): Promise<ScheduleRunRecord> => {
      return this.request<ScheduleRunRecord>(`/schedule-runs/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number | string): Promise<void> => {
      await this.request<void>(`/schedule-runs/${id}/`, {
        method: "DELETE",
      });
    },
  };

  // ==========================================================================
  // 2. Model-Based CRUD & Workflows: Optimization Jobs
  // ==========================================================================

  optimizationJobs = {
    list: async (
      query?: TenantPaginationQuery,
    ): Promise<PaginatedResponse<OptimizationJobRecord>> => {
      const qs = this.buildQueryString(query);
      const res = await this.request<any>(`/optimization-jobs/${qs}`);
      return this.normalizePaginated<OptimizationJobRecord>(res);
    },

    get: async (id: number | string): Promise<OptimizationJobRecord> => {
      return this.request<OptimizationJobRecord>(`/optimization-jobs/${id}/`);
    },

    create: async (data: Partial<OptimizationJobRecord>): Promise<OptimizationJobRecord> => {
      return this.request<OptimizationJobRecord>("/optimization-jobs/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number | string): Promise<void> => {
      await this.request<void>(`/optimization-jobs/${id}/`, {
        method: "DELETE",
      });
    },

    dispatch: async (payload: OptimizeScheduleRequest): Promise<DispatchResponse> => {
      return this.request<DispatchResponse>("/optimization-jobs/dispatch", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    dispatchHitl: async (payload: OptimizeScheduleRequest): Promise<DispatchResponse> => {
      return this.request<DispatchResponse>("/optimization-jobs/hitl-dispatch", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    getWorkflowStatus: async (workflowId: string): Promise<WorkflowStatusResponse> => {
      return this.request<WorkflowStatusResponse>(
        `/optimization-jobs/${workflowId}/workflow-status`,
      );
    },

    getApprovalState: async (workflowId: string): Promise<ApprovalStateResponse> => {
      return this.request<ApprovalStateResponse>(`/optimization-jobs/${workflowId}/approval-state`);
    },

    submitApproval: async (
      workflowId: string,
      signal: WorkflowSignalRequest,
    ): Promise<WorkflowSignalResponse> => {
      return this.request<WorkflowSignalResponse>(`/optimization-jobs/${workflowId}/approvals`, {
        method: "POST",
        body: JSON.stringify(signal),
      });
    },
  };

  // ==========================================================================
  // 3. Model-Based CRUD & Benchmarks: Scenarios
  // ==========================================================================

  scenarios = {
    list: async (query?: TenantPaginationQuery): Promise<PaginatedResponse<ScenarioRecordDTO>> => {
      const qs = this.buildQueryString(query);
      const res = await this.request<any>(`/scenarios/${qs}`);
      return this.normalizePaginated<ScenarioRecordDTO>(res);
    },

    get: async (id: number | string): Promise<ScenarioRecordDTO> => {
      return this.request<ScenarioRecordDTO>(`/scenarios/${id}/`);
    },

    create: async (data: Partial<ScenarioRecordDTO>): Promise<ScenarioRecordDTO> => {
      return this.request<ScenarioRecordDTO>("/scenarios/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    update: async (
      id: number | string,
      data: Partial<ScenarioRecordDTO>,
    ): Promise<ScenarioRecordDTO> => {
      return this.request<ScenarioRecordDTO>(`/scenarios/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number | string): Promise<void> => {
      await this.request<void>(`/scenarios/${id}/`, {
        method: "DELETE",
      });
    },

    execute: async (scenario: ScenarioDefinition): Promise<ScenarioExecutionResponse> => {
      return this.request<ScenarioExecutionResponse>("/scenarios/execute", {
        method: "POST",
        body: JSON.stringify(scenario),
      });
    },

    generate: async (params: GenerateScenarioRequest): Promise<GeneratedScenarioSummary> => {
      return this.request<GeneratedScenarioSummary>("/scenarios/generate", {
        method: "POST",
        body: JSON.stringify(params),
      });
    },
  };

  // ==========================================================================
  // 4. Model-Based CRUD: Disruption Logs
  // ==========================================================================

  disruptionLogs = {
    list: async (
      query?: TenantPaginationQuery,
    ): Promise<PaginatedResponse<DisruptionLogRecord>> => {
      const qs = this.buildQueryString(query);
      const res = await this.request<any>(`/disruption-logs/${qs}`);
      return this.normalizePaginated<DisruptionLogRecord>(res);
    },

    get: async (id: number | string): Promise<DisruptionLogRecord> => {
      return this.request<DisruptionLogRecord>(`/disruption-logs/${id}/`);
    },

    create: async (data: Partial<DisruptionLogRecord>): Promise<DisruptionLogRecord> => {
      return this.request<DisruptionLogRecord>("/disruption-logs/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number | string): Promise<void> => {
      await this.request<void>(`/disruption-logs/${id}/`, {
        method: "DELETE",
      });
    },
  };

  // ==========================================================================
  // 5. Operations Research Services: Schedules
  // ==========================================================================

  schedules = {
    optimize: async (payload: OptimizeScheduleRequest): Promise<OptimizeScheduleResponse> => {
      return this.request<OptimizeScheduleResponse>("/schedules/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    validate: async (payload: ValidateScheduleRequest): Promise<ValidateScheduleResponse> => {
      return this.request<ValidateScheduleResponse>("/schedules/validate", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================================================
  // 6. Simulation & Reactive Rescheduling
  // ==========================================================================

  simulations = {
    simulateDisruptions: async (
      payload: SimulateDisruptionRequest,
    ): Promise<SimulateDisruptionResponse> => {
      return this.request<SimulateDisruptionResponse>("/simulations/disruptions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    reschedule: async (payload: RescheduleRequest): Promise<RescheduleResponse> => {
      return this.request<RescheduleResponse>("/simulations/reschedule", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================================================
  // 7. Visualizations & Document Exporters
  // ==========================================================================

  visualizations = {
    renderStripboardHtml: async (payload: StripboardRenderRequest): Promise<RenderHtmlResponse> => {
      return this.request<RenderHtmlResponse>("/visualizations/stripboards/html", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    renderStripboardSvg: async (payload: StripboardRenderRequest): Promise<RenderSvgResponse> => {
      return this.request<RenderSvgResponse>("/visualizations/stripboards/svg", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    renderDoodHtml: async (payload: DOODRenderRequest): Promise<RenderHtmlResponse> => {
      return this.request<RenderHtmlResponse>("/visualizations/dood-reports", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    renderGanttSvg: async (payload: GanttRenderRequest): Promise<RenderSvgResponse> => {
      return this.request<RenderSvgResponse>("/visualizations/gantt-charts", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    exportReportHtml: async (payload: ReportExportRequest): Promise<RenderHtmlResponse> => {
      return this.request<RenderHtmlResponse>("/visualizations/reports", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================================================
  // 8. Calendar Providers
  // ==========================================================================

  calendars = {
    culturalIntervals: async (
      payload: CulturalIntervalsRequest,
    ): Promise<CulturalIntervalsResponse> => {
      return this.request<CulturalIntervalsResponse>("/calendars/cultural/intervals", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    standardBlackouts: async (
      payload: StandardBlackoutsRequest,
    ): Promise<StandardBlackoutsResponse> => {
      return this.request<StandardBlackoutsResponse>("/calendars/standard/blackouts", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================================================
  // 9. Six Vertical Domain Adapters
  // ==========================================================================

  adapters = {
    filmProduction: Object.assign(
      async (payload: FilmOptimizeRequest | ProductionDataset): Promise<FilmScheduleResult> => {
        return this.request<FilmScheduleResult>("/adapters/film-production/optimize", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      },
      {
        optimize: async (
          payload: FilmOptimizeRequest | ProductionDataset,
        ): Promise<FilmScheduleResult> => {
          return this.request<FilmScheduleResult>("/adapters/film-production/optimize", {
            method: "POST",
            body: JSON.stringify(payload),
          });
        },
        reschedule: async (payload: FilmRescheduleRequest): Promise<FilmScheduleResult> => {
          return this.request<FilmScheduleResult>("/adapters/film-production/reschedule", {
            method: "POST",
            body: JSON.stringify(payload),
          });
        },
        intraday: async (payload: FilmIntradayRequest): Promise<Array<Record<string, unknown>>> => {
          return this.request<Array<Record<string, unknown>>>(
            "/adapters/film-production/intraday",
            {
              method: "POST",
              body: JSON.stringify(payload),
            },
          );
        },
        callSheet: async (payload: FilmCallSheetRequest): Promise<DailyCallSheet> => {
          return this.request<DailyCallSheet>("/adapters/film-production/call-sheet", {
            method: "POST",
            body: JSON.stringify(payload),
          });
        },
      },
    ),

    manufacturing: async (
      payload: ManufacturingOptimizeRequest,
    ): Promise<ManufacturingOptimizeResponse> => {
      return this.request<ManufacturingOptimizeResponse>("/adapters/manufacturing/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    workforce: async (payload: WorkforceOptimizeRequest): Promise<WorkforceOptimizeResponse> => {
      return this.request<WorkforceOptimizeResponse>("/adapters/workforce/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    marketingFlighting: async (
      payload: MarketingOptimizeRequest,
    ): Promise<MarketingOptimizeResponse> => {
      return this.request<MarketingOptimizeResponse>("/adapters/marketing-flighting/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    academicTimetables: async (
      payload: AcademicOptimizeRequest,
    ): Promise<AcademicOptimizeResponse> => {
      return this.request<AcademicOptimizeResponse>("/adapters/academic-timetables/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    eventRunSheets: async (payload: EventsOptimizeRequest): Promise<EventsOptimizeResponse> => {
      return this.request<EventsOptimizeResponse>("/adapters/event-run-sheets/optimize", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================================================
  // 7. Instruction-Driven Pipelines & Project Workspaces
  // ==========================================================================

  pipelines = {
    list: async (): Promise<PipelineManifestSummary[]> => {
      return this.request<PipelineManifestSummary[]>("/pipelines");
    },

    get: async (name: string): Promise<PipelineManifest> => {
      return this.request<PipelineManifest>(`/pipelines/${encodeURIComponent(name)}`);
    },
  };

  rulesets = {
    list: async (): Promise<RulesetSummary[]> => {
      return this.request<RulesetSummary[]>("/rulesets");
    },

    get: async (name: string): Promise<RulesetPolicy> => {
      return this.request<RulesetPolicy>(`/rulesets/${encodeURIComponent(name)}`);
    },
  };

  projects = {
    list: async (tenantId = "default"): Promise<PaginatedResponse<ProjectWorkspaceRecord>> => {
      return this.request<PaginatedResponse<ProjectWorkspaceRecord>>(
        `/projects?tenant_id=${encodeURIComponent(tenantId)}`
      );
    },

    init: async (payload: ProjectInitRequest): Promise<ProjectInitResponse> => {
      return this.request<ProjectInitResponse>("/projects/init", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    getCompletedStages: async (
      projectId: string,
      tenantId = "default"
    ): Promise<{ project_id: string; completed_stages: string[] }> => {
      return this.request<{ project_id: string; completed_stages: string[] }>(
        `/projects/${encodeURIComponent(projectId)}/stages/completed?tenant_id=${encodeURIComponent(tenantId)}`
      );
    },

    getCheckpoint: async (
      projectId: string,
      stageName: string,
      tenantId = "default"
    ): Promise<ProjectCheckpointRecord> => {
      return this.request<ProjectCheckpointRecord>(
        `/projects/${encodeURIComponent(projectId)}/checkpoints/${encodeURIComponent(stageName)}?tenant_id=${encodeURIComponent(tenantId)}`
      );
    },

    approveGate: async (
      projectId: string,
      stageName: string,
      payload: GateApprovalRequest
    ): Promise<GateApprovalResponse> => {
      return this.request<GateApprovalResponse>(
        `/projects/${encodeURIComponent(projectId)}/gates/${encodeURIComponent(stageName)}/approve`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
    },

    runStage: async (
      projectId: string,
      stageName: string,
      payload: StageRunRequest = {}
    ): Promise<StageRunResponse> => {
      return this.request<StageRunResponse>(
        `/projects/${encodeURIComponent(projectId)}/stages/${encodeURIComponent(stageName)}/run`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
    },

    reviseGate: async (
      projectId: string,
      stageName: string,
      payload: GateRevisionRequest
    ): Promise<GateRevisionResponse> => {
      return this.request<GateRevisionResponse>(
        `/projects/${encodeURIComponent(projectId)}/gates/${encodeURIComponent(stageName)}/revise`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
    },

    getArtifact: async (
      projectId: string,
      artifactName: string,
      tenantId = "default"
    ): Promise<Record<string, unknown>> => {
      return this.request<Record<string, unknown>>(
        `/projects/${encodeURIComponent(projectId)}/artifacts/${encodeURIComponent(artifactName)}?tenant_id=${encodeURIComponent(tenantId)}`
      );
    },

    getEvents: async (
      projectId: string,
      tenantId = "default"
    ): Promise<PipelineEventItem[]> => {
      return this.request<PipelineEventItem[]>(
        `/projects/${encodeURIComponent(projectId)}/events?tenant_id=${encodeURIComponent(tenantId)}`
      );
    },
  };
}
