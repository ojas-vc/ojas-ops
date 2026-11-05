"""End-to-End full-stack tests for Instruction-Driven Operational Pipelines."""

import json
from pathlib import Path

import pytest

from ojas_ops.agents.tools.registry import default_tool_registry
from ojas_ops.observability import emit_project_event, get_project_events
from ojas_ops.pipelines.checkpoint import (
    CheckpointValidationError,
    get_completed_stages,
    init_project,
    read_checkpoint,
    write_checkpoint,
)
from ojas_ops.pipelines.loader import (
    list_available_pipelines,
    list_available_rulesets,
    load_pipeline_manifest,
    load_ruleset,
)
from ojas_ops.temporal.activities.agent_activity import execute_agent_stage_activity


def test_all_18_pipeline_manifests_load_and_validate():
    """Verify that all 18 industrial pipelines exist, load, and have required fields."""
    pipelines = list_available_pipelines()
    assert len(pipelines) == 18, f"Expected 18 pipelines, found {len(pipelines)}"

    expected_names = [
        "film-crossboarding",
        "daily-call-sheet-sequencer",
        "production-disruption-recovery",
        "job-shop-flow",
        "flow-shop-batching",
        "jit-assembly-balancing",
        "supply-chain-replenishment",
        "clinical-shift-rostering",
        "surgical-suite-allocator",
        "workforce-fatigue-compliance",
        "conference-multi-track-curator",
        "wedding-occasion-runsheet",
        "exhibition-booth-allocator",
        "campaign-cadence-flighting",
        "field-service-dispatch",
        "academic-semester-timetabler",
        "muhurat-auspicious-scheduler",
        "festival-workforce-rebalance",
    ]

    for name in expected_names:
        manifest = load_pipeline_manifest(name)
        assert manifest["name"] == name
        assert "version" in manifest
        assert len(manifest.get("stages", [])) >= 2, f"Pipeline {name} should have >= 2 stages"
        for stage in manifest["stages"]:
            assert "name" in stage
            assert "skill" in stage


def test_all_8_rulesets_load_and_validate():
    """Verify that all 8 domain labor and operational rulesets exist and parse."""
    rulesets = list_available_rulesets()
    assert len(rulesets) >= 8

    expected_rulesets = [
        "sag-aftra-theatrical",
        "fwice-bollywood",
        "iatse-commercial",
        "automotive-oem",
        "iso9001-cleanroom",
        "icu-acuity-california",
        "vedic-muhurat-standard",
        "tech-conference-standard",
    ]

    for r_name in expected_rulesets:
        rule = load_ruleset(r_name)
        assert rule["name"] == r_name
        assert "domain" in rule
        assert "parameters" in rule


def test_project_workspace_scaffolding_and_dual_persistence(tmp_path: Path):
    """Test multi-tenant workspace initialization on disk."""
    tenant_id = "tenant-beta"
    project_id = "proj-test-101"

    proj_dir = init_project(
        project_id=project_id,
        title="Test Feature Shoot",
        pipeline_type="film-crossboarding",
        tenant_id=tenant_id,
        ruleset="sag-aftra-theatrical",
        base_dir=tmp_path,
    )

    assert proj_dir.exists()
    assert (proj_dir / "project.json").exists()
    assert (proj_dir / "artifacts").is_dir()
    assert (proj_dir / "exports").is_dir()
    assert (proj_dir / "logs").is_dir()
    assert (proj_dir / "history").is_dir()

    with open(proj_dir / "project.json") as f:
        meta = json.load(f)
    assert meta["tenant_id"] == tenant_id
    assert meta["pipeline_type"] == "film-crossboarding"


def test_checkpoint_gating_and_validation_error(tmp_path: Path):
    """Test that human approval default blocks completed status if not approved."""
    tenant_id = "tenant-1"
    project_id = "proj-gate-test"

    init_project(
        project_id=project_id,
        title="Gating Test",
        pipeline_type="film-crossboarding",
        tenant_id=tenant_id,
        base_dir=tmp_path,
    )

    # Attempting to write status='completed' on a gated stage without human_approved=True must raise
    with pytest.raises(CheckpointValidationError):
        write_checkpoint(
            tenant_id=tenant_id,
            project_id=project_id,
            stage="crossboard",
            status="completed",
            artifacts={"stripboard": []},
            pipeline_type="film-crossboarding",
            human_approval_required=True,
            human_approved=False,
            base_dir=tmp_path,
        )

    # Writing as awaiting_human is valid
    cp_path = write_checkpoint(
        tenant_id=tenant_id,
        project_id=project_id,
        stage="crossboard",
        status="awaiting_human",
        artifacts={"stripboard": [{"day": 1}]},
        pipeline_type="film-crossboarding",
        human_approval_required=True,
        human_approved=False,
        base_dir=tmp_path,
    )
    assert cp_path.exists()

    cp = read_checkpoint(tenant_id, project_id, "crossboard", base_dir=tmp_path)
    assert cp is not None
    assert cp["status"] == "awaiting_human"
    assert cp["artifacts"]["stripboard"] == [{"day": 1}]

    # Simulating operator sign-off
    cp_path_approved = write_checkpoint(
        tenant_id=tenant_id,
        project_id=project_id,
        stage="crossboard",
        status="completed",
        artifacts=cp["artifacts"],
        pipeline_type="film-crossboarding",
        human_approval_required=True,
        human_approved=True,
        metadata={"approval_notes": "Signed off by Line Producer."},
        base_dir=tmp_path,
    )
    assert cp_path_approved.exists()

    completed = get_completed_stages(tenant_id, project_id, base_dir=tmp_path)
    assert "crossboard" in completed


def test_agent_stage_execution_activity_flow():
    """Test executing a stage via execute_agent_stage_activity."""
    import asyncio

    manifest = load_pipeline_manifest("job-shop-flow")
    stage_def = manifest["stages"][0]  # routing stage

    result = asyncio.run(
        execute_agent_stage_activity(
            {
                "tenant_id": "test-tenant",
                "project_id": "test-proj-activity",
                "pipeline_name": "job-shop-flow",
                "stage_name": stage_def["name"],
                "stage_def": stage_def,
                "ruleset_name": "automotive-oem",
                "context_data": {
                    "operations": [
                        {"id": "OP1", "part": "P1", "duration": 20},
                    ],
                    "machines": [{"id": "M1", "capacity": 1}],
                },
            }
        )
    )

    assert result["status"] in ("completed", "awaiting_human")
    assert result["stage"] == stage_def["name"]
    assert "artifacts" in result


def test_observability_event_streaming_and_buffering():
    """Test emitting and querying project operational events."""
    tenant = "tenant-obs"
    proj = "proj-obs-1"

    emit_project_event(
        tenant_id=tenant,
        project_id=proj,
        stage="routing",
        event_type="stage_started",
        message="Started routing operations",
    )
    emit_project_event(
        tenant_id=tenant,
        project_id=proj,
        stage="routing",
        event_type="tool_called",
        message="Dispatched solver tool",
        data={"solver": "ortools"},
    )

    events = get_project_events(tenant, proj)
    assert len(events) >= 2
    assert events[-2]["event_type"] == "stage_started" if "event_type" in events[-2] else events[-2]["type"] == "stage_started"
    assert events[-1]["message"] == "Dispatched solver tool"


def test_tool_registry_capability_and_skill_discovery():
    """Verify tool discovery by capability and stage director skill."""
    film_tools = default_tool_registry.find_by_capability("film-crossboarding")
    assert len(film_tools) >= 1
    assert film_tools[0].name == "optimize_film_schedule"

    dood_tools = default_tool_registry.find_by_skill("dood-director")
    assert len(dood_tools) >= 1
    assert dood_tools[0].name == "audit_dood"
