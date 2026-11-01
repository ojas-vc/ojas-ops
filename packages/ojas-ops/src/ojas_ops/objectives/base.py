"""Base objective protocol and linear expression builders for CP-SAT."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class Objective(ABC):
    """Abstract optimization objective."""

    def __init__(self, name: str = "", weight: float = 1.0) -> None:
        self.name = name or self.__class__.__name__
        self.weight = weight

    @abstractmethod
    def build_expression(self, context: SolverContext) -> Any:
        """Construct CP-SAT linear expression or integer variable to minimize."""

    @abstractmethod
    def evaluate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> float:
        """Evaluate deterministic objective value on a solved schedule."""
