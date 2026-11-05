"""Central registry of canonical optimization agent tools."""

from __future__ import annotations

from typing import Any

from ojas_ops.agents.tools.base import AgentTool
from ojas_ops.agents.tools.disruption import simulate_schedule_delay
from ojas_ops.agents.tools.film import audit_dood, optimize_film_shoot
from ojas_ops.agents.tools.manufacturing import optimize_job_shop
from ojas_ops.agents.tools.validation import verify_schedule_feasibility


class ToolRegistry:
    """Central catalog of Ojas Ops operational optimization tools."""

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        """Register a canonical agent tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        """Retrieve a registered tool by name."""
        if name not in self._tools:
            available = list(self._tools.keys())
            raise KeyError(f"Unknown agent tool '{name}'. Available tools: {available}")
        return self._tools[name]

    def all(self) -> list[AgentTool]:
        """Return list of all registered tools."""
        return list(self._tools.values())

    def find_by_capability(self, capability: str) -> list[AgentTool]:
        """Find tools supporting a given operational capability."""
        return [
            tool
            for tool in self._tools.values()
            if tool.capability == capability or capability in tool.supports
        ]

    def find_by_skill(self, skill_name: str) -> list[AgentTool]:
        """Find tools assigned to a given stage director skill."""
        return [
            tool
            for tool in self._tools.values()
            if skill_name in tool.agent_skills
        ]

    def get_antigravity_tools(self) -> list[dict[str, Any]]:
        """Export all tools formatted for Google Antigravity."""
        return [tool.to_antigravity() for tool in self._tools.values()]

    def get_anthropic_tools(self) -> list[dict[str, Any]]:
        """Export all tools formatted for Anthropic Claude Messages API."""
        return [tool.to_anthropic() for tool in self._tools.values()]

    def get_langchain_tools(self) -> list[Any]:
        """Export all tools formatted for LangChain / LangGraph."""
        return [tool.to_langchain() for tool in self._tools.values()]

    def get_crewai_tools(self) -> list[Any]:
        """Export all tools formatted for CrewAI."""
        return [tool.to_crewai() for tool in self._tools.values()]

    def dispatch(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool by name with arguments."""
        tool = self.get(tool_name)
        return tool.run(**kwargs)

    async def adispatch(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool asynchronously by name with arguments."""
        tool = self.get(tool_name)
        return await tool.arun(**kwargs)


def create_default_registry() -> ToolRegistry:
    """Constructs and populates the default registry with all core operational tools."""
    registry = ToolRegistry()

    # 1. Film shooting schedule optimization
    registry.register(
        AgentTool(
            name="optimize_film_schedule",
            description=(
                "Solves a combinatorial film shooting schedule using Google OR-Tools CP-SAT. "
                "Enforces SAG-AFTRA 10-day drop-and-pickup, continuous soundstage leases, "
                "multi-unit concurrency, and location setup minimization."
            ),
            parameters_schema={
                "type": "object",
                "properties": {
                    "dataset_dict": {
                        "type": "object",
                        "description": "Production dataset containing scenes, cast, and locations.",
                    },
                    "max_time_seconds": {
                        "type": "number",
                        "description": "Time limit in seconds.",
                        "default": 30.0,
                    },
                    "enable_drop_pickup": {
                        "type": "boolean",
                        "description": "Whether to enforce SAG-AFTRA 10-day hold drop/pickup rule.",
                        "default": True,
                    },
                },
                "required": ["dataset_dict"],
            },
            fn=optimize_film_shoot,
            capability="film-crossboarding",
            provider="ortools-cpsat",
            tier="core",
            agent_skills=["crossboard-director"],
        )
    )

    # 2. DOOD cast utilization audit
    registry.register(
        AgentTool(
            name="audit_dood",
            description=(
                "Generates a Day Out of Days (DOOD) cast utilization audit tracking work, "
                "hold, and drop/pickup days for actors."
            ),
            parameters_schema={
                "type": "object",
                "properties": {
                    "dataset_dict": {
                        "type": "object",
                        "description": "Production dataset defining scenes and cast requirements.",
                    },
                    "max_time_seconds": {
                        "type": "number",
                        "description": "Time limit in seconds.",
                        "default": 30.0,
                    },
                },
                "required": ["dataset_dict"],
            },
            fn=audit_dood,
            capability="dood-audit",
            provider="ojas-ops",
            tier="core",
            agent_skills=["dood-director"],
        )
    )

    # 3. Manufacturing job shop optimization
    registry.register(
        AgentTool(
            name="optimize_job_shop",
            description=(
                "Optimizes discrete manufacturing machine scheduling with setup changeover "
                "minimization and makespan reduction using CP-SAT."
            ),
            parameters_schema={
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of operations with duration and machine requirements.",
                    },
                    "machines": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of available machines and capacity.",
                    },
                    "time_limit_seconds": {
                        "type": "number",
                        "description": "Time limit in seconds.",
                        "default": 30.0,
                    },
                },
                "required": ["operations", "machines"],
            },
            fn=optimize_job_shop,
            capability="job-shop-flow",
            provider="ortools-cpsat",
            tier="core",
            agent_skills=["schedule-director"],
        )
    )

    # 4. Disruption simulation & reactive rescheduling
    registry.register(
        AgentTool(
            name="simulate_schedule_delay",
            description=(
                "Simulates operational disruptions (task delays, machine breakdowns) and "
                "computes rescheduling impact and new makespan."
            ),
            parameters_schema={
                "type": "object",
                "properties": {
                    "schedule_id": {
                        "type": "string",
                        "description": "Identifier of the baseline schedule.",
                    },
                    "disruption_type": {
                        "type": "string",
                        "description": "Type of disturbance: TASK_DELAY, RESOURCE_BREAKDOWN, or CAPACITY_REDUCTION.",
                        "default": "TASK_DELAY",
                    },
                    "magnitude_minutes": {
                        "type": "integer",
                        "description": "Duration of the delay or downtime in minutes.",
                    },
                    "affected_tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task IDs directly affected by the delay.",
                    },
                },
                "required": ["schedule_id", "magnitude_minutes", "affected_tasks"],
            },
            fn=simulate_schedule_delay,
            is_async=True,
            capability="disruption-simulation",
            provider="ojas-ops",
            tier="advanced",
            agent_skills=["simulation-director"],
        )
    )

    # 5. Deterministic schedule feasibility verification
    registry.register(
        AgentTool(
            name="verify_schedule_feasibility",
            description=(
                "Performs independent deterministic verification on candidate schedules "
                "without solver dependencies, checking dependencies and calendar blackouts."
            ),
            parameters_schema={
                "type": "object",
                "properties": {
                    "schedule_id": {
                        "type": "string",
                        "description": "Identifier of the schedule to audit.",
                    },
                    "tasks": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of tasks with duration and requirements.",
                    },
                    "resources": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of resources with capacity and blackout windows.",
                    },
                },
                "required": ["schedule_id"],
            },
            fn=verify_schedule_feasibility,
            is_async=True,
            capability="schedule-validation",
            provider="ojas-ops",
            tier="core",
            agent_skills=["validator-reviewer"],
        )
    )

    return registry


default_tool_registry = create_default_registry()
