"""Constraint abstractions and solver context for CP-SAT compilation and validation."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"


from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ortools.sat.python import cp_model

    from ojas_ops.models.resource import Resource
    from ojas_ops.models.schedule import ResourceAssignment, ScheduledTask
    from ojas_ops.models.task import Task
    from ojas_ops.models.time import Horizon
    from ojas_ops.validation.report import ConstraintViolation


class TaskVars:
    """OR-Tools CP-SAT variables for a single task."""

    def __init__(
        self,
        *,
        start: cp_model.IntVar,
        end: cp_model.IntVar,
        interval: cp_model.IntervalVar,
        duration: int,
    ) -> None:
        self.start = start
        self.end = end
        self.interval = interval
        self.duration = duration
        # Optional interval vars per resource: resource_id -> (IntervalVar, BoolVar)
        self.resource_intervals: dict[str, tuple[cp_model.IntervalVar, cp_model.IntVar]] = {}


class SolverContext:
    """Holds CP-SAT model and mapped variables during schedule compilation."""

    def __init__(
        self,
        *,
        model: cp_model.CpModel,
        tasks: dict[str, Task],
        resources: dict[str, Resource],
        horizon: Horizon,
    ) -> None:
        self.model = model
        self.tasks = tasks
        self.resources = resources
        self.horizon = horizon
        self.task_vars: dict[str, TaskVars] = {}
        # Mapping: resource_id -> list of interval vars executing on that resource
        self.resource_intervals: dict[str, list[cp_model.IntervalVar]] = {
            rid: [] for rid in resources
        }
        # Mapping: resource_id -> list of (interval_var, demand_int) for cumulative resources
        self.resource_demands: dict[str, list[tuple[cp_model.IntervalVar, int]]] = {
            rid: [] for rid in resources
        }
        self.custom_data: dict[str, object] = {}
        self.soft_penalties: list[cp_model.LinearExpr | int] = []


class Constraint(ABC):
    """Abstract scheduling constraint applicable to CP-SAT and independent validator."""

    def __init__(self, name: str = "", hard: bool = True) -> None:
        self.name = name or self.__class__.__name__
        self.hard = hard

    @abstractmethod
    def apply_to_solver(self, context: SolverContext) -> None:
        """Apply mathematical constraints to the CP-SAT model."""

    @abstractmethod
    def validate(
        self,
        tasks: dict[str, ScheduledTask],
        resources: dict[str, ResourceAssignment],
    ) -> list[ConstraintViolation]:
        """Verify compliance independently without solver dependencies."""
