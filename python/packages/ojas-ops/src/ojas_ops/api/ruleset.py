"""ViewSet managing operational policies and labor rulesets on /rulesets."""

from __future__ import annotations

import builtins
from typing import Any

from django_bolt import ViewSet

from ojas_ops.pipelines.loader import list_available_rulesets, load_ruleset


class RulesetViewSet(ViewSet):
    """ViewSet serving domain labor policies and operational parameter sets."""

    lookup_field = "name"

    async def list(self, request: Any) -> builtins.list[dict[str, Any]]:
        """List all available operational rulesets and labor agreements."""
        return list_available_rulesets()

    async def retrieve(self, request: Any, name: str) -> dict[str, Any]:
        """Retrieve full policy definition for a specific ruleset."""
        try:
            return load_ruleset(name)
        except FileNotFoundError as e:
            return {"error": str(e), "status": "NOT_FOUND"}

    # Backward compatibility aliases
    list_rulesets = list
    get_ruleset = retrieve


