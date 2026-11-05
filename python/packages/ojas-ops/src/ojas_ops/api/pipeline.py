"""ViewSet managing declarative pipeline manifests on /pipelines."""

from __future__ import annotations

from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.pipelines.loader import list_available_pipelines, load_pipeline_manifest


class PipelineModelViewSet(ViewSet):
    """ViewSet serving declarative pipeline definitions and stage metadata."""

    @action(methods=["GET"], detail=False, path="")
    async def list_pipelines(self, request: Any) -> list[dict[str, Any]]:
        """List all available operational pipeline manifests."""
        return list_available_pipelines()

    @action(methods=["GET"], detail=False, path="{name}")
    async def get_pipeline(self, request: Any, name: str) -> dict[str, Any]:
        """Retrieve full declarative manifest for a specific pipeline."""
        try:
            return load_pipeline_manifest(name)
        except FileNotFoundError as e:
            return {"error": str(e), "status": "NOT_FOUND"}

