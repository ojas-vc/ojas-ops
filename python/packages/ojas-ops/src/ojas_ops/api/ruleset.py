"""ViewSet managing operational policies and labor rulesets on /rulesets."""

from __future__ import annotations

from typing import Any

from django_bolt import ViewSet, action

from ojas_ops.pipelines.loader import list_available_rulesets, load_ruleset


class RulesetViewSet(ViewSet):
    """ViewSet serving domain labor policies and operational parameter sets."""

    @action(methods=["GET"], detail=False, path="")
    async def list_rulesets(self, request: Any) -> list[dict[str, Any]]:
        """List all available operational rulesets and labor agreements."""
        return list_available_rulesets()

    @action(methods=["GET"], detail=False, path="{name}")
    async def get_ruleset(self, request: Any, name: str) -> dict[str, Any]:
        """Retrieve full policy definition for a specific ruleset."""
        try:
            return load_ruleset(name)
        except FileNotFoundError as e:
            return {"error": str(e), "status": "NOT_FOUND"}

