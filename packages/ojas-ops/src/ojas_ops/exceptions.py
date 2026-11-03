"""Domain exception definitions for Ojas Ops."""


class OjasOpsError(Exception):
    """Base exception for all Ojas Ops domain errors."""


class OptimizationInfeasibleError(OjasOpsError):
    """Raised when an optimization model has no feasible solution satisfying constraints."""


class ScheduleValidationError(OjasOpsError):
    """Raised when deterministic validation fails on a schedule."""


class TemporalTimeoutError(OjasOpsError):
    """Raised when an asynchronous optimization workflow exceeds its deadline."""


class InvalidConstraintError(OjasOpsError):
    """Raised when an invalid or contradictory constraint specification is provided."""
