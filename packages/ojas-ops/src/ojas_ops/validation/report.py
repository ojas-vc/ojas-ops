"""Validation reporting models and violation records."""

from __future__ import annotations

from enum import StrEnum

import msgspec


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ConstraintViolation(msgspec.Struct, kw_only=True):
    """Detailed record of a constraint violation discovered during schedule validation."""

    constraint_name: str
    task_id: str | None = None
    resource_id: str | None = None
    message: str = ""
    severity: Severity = Severity.ERROR
    details: dict[str, str] = msgspec.field(default_factory=dict)


class ValidationReport(msgspec.Struct, kw_only=True):
    """Comprehensive evaluation report of a schedule's feasibility and constraint compliance."""

    is_valid: bool
    violations: list[ConstraintViolation] = msgspec.field(default_factory=list)
    summary: str = ""

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)
