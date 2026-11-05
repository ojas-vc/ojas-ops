"""ViewSet managing declarative pipeline manifests on /pipelines."""

from __future__ import annotations

import builtins
from typing import Any

from django_bolt import ViewSet

from ojas_ops.pipelines.loader import list_available_pipelines, load_pipeline_manifest


class PipelineModelViewSet(ViewSet):
    """ViewSet serving declarative pipeline definitions and stage metadata."""

    lookup_field = "name"

    async def list(self, request: Any) -> builtins.list[dict[str, Any]]:
        """List all available operational pipeline manifests."""
        return list_available_pipelines()

    async def retrieve(self, request: Any, name: str) -> dict[str, Any]:
        """Retrieve full declarative manifest for a specific pipeline."""
        try:
            return load_pipeline_manifest(name)
        except FileNotFoundError as e:
            return {"error": str(e), "status": "NOT_FOUND"}

    # Backward compatibility aliases
    list_pipelines = list
    get_pipeline = retrieve


