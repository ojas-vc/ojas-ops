# Operational Onboarding & Pipeline Discovery

## Purpose

Guide the AI agent when a user arrives with a general or exploratory scheduling request (e.g., "Schedule our shoot", "Optimize our factory line", "Make a nurse roster", "Plan a conference").

## Discovery Protocol

1. **Classify the Industry & Operational Domain**:
   - Film, Episodic, Commercial, or Video Shoot $\rightarrow$ `film-crossboarding`, `daily-call-sheet-sequencer`, `production-disruption-recovery`
   - Factory, Machine Shop, or Batch Processing $\rightarrow$ `job-shop-flow`, `flow-shop-batching`, `jit-assembly-balancing`
   - Hospital, Clinic, or Workforce Rostering $\rightarrow$ `clinical-shift-rostering`, `workforce-fatigue-compliance`
   - Conference, Summit, or Festival Occasion $\rightarrow$ `conference-multi-track-curator`, `wedding-occasion-runsheet`
   - Marketing Ad Spend or Growth $\rightarrow$ `campaign-cadence-flighting`
   - Vedic / Cultural Milestone $\rightarrow$ `muhurat-auspicious-scheduler`

2. **Audit Labor Policies & Contracts**:
   - Are union rules applicable?
     - Film: SAG-AFTRA Theatrical, FWICE Bollywood, IATSE Commercial
     - Healthcare: Mandatory ICU Acuity Ratios, Night Shift Rotations
     - Industry: ISO 9001 Cleanroom Cleaning-in-Place (CIP) windows

3. **Initialize Project Workspace**:
   - Always initialize the project workspace before running optimization:
     ```python
     from ojas_ops.pipelines.checkpoint import init_project
     init_project(
         project_id="<project-slug>",
         title="<Human Readable Title>",
         pipeline_type="<pipeline-name>",
         tenant_id="<tenant_id>",
         ruleset="<ruleset-name>"
     )
     ```
   - This creates `projects/<tenant_id>/<project-slug>/` with `artifacts/`, `exports/`, `logs/`, and `project.json`.

4. **Announce the Execution Plan**:
   - State the selected pipeline.
   - List the 5–7 sequential stages.
   - Identify where Human-in-the-Loop (HITL) approval gates will occur.
   - Begin Stage 1.
