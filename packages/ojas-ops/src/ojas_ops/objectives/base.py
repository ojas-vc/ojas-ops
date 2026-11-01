"""Base objective protocol and linear expression builders for CP-SAT."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ojas_ops.constraints.base import SolverContext
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask


class Objective(ABC):
    """Abstract optimization objective."""

    def __init__(
        self,
        name: str = "",
        weight: float = 1.0,
        is_maximize: bool = False,
    ) -> None:
        self.name = name or self.__class__.__name__
        self.weight = weight
        self.is_maximize = is_maximize

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
